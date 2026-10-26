import argparse
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import requests
import truststore
from bs4 import BeautifulSoup


# python api/sinan/client.py --arquivo-ficha dados/ficha_9999999.json  --confirmar-numero 9999999

truststore.inject_into_ssl()

LOGIN_URL = "https://sinan.saude.gov.br/sinan/login/login.jsf"
CADASTRO_URL = (
    "https://sinan.saude.gov.br/sinan/secured/notificacao/"
    "individual/dengue/dengueIndividual.jsf"
)


def criar_sessao():
    sessao = requests.Session()
    sessao.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "pt-BR,pt;q=0.9",
        }
    )
    return sessao


def extrair_view_state(html):
    soup = BeautifulSoup(html, "html.parser")
    campo = soup.find("input", {"name": "javax.faces.ViewState"})
    if not campo:
        raise RuntimeError("ViewState nao encontrado.")
    return campo["value"]


def extrair_mensagens(html):
    soup = BeautifulSoup(html, "html.parser")
    mensagens = []
    for seletor in ("#erros", ".rich-messages", ".mensagem", ".erro", ".error"):
        for elemento in soup.select(seletor):
            texto = " ".join(elemento.get_text(" ", strip=True).split())
            if texto and texto not in mensagens:
                mensagens.append(texto)
    return mensagens


def tem_formulario_login(html):
    soup = BeautifulSoup(html, "html.parser")
    return bool(
        soup.find("input", {"name": "form:username"})
        and soup.find("input", {"name": "form:password"})
    )


def autenticar(usuario, senha):
    sessao = criar_sessao()
    resposta = sessao.get(LOGIN_URL, timeout=30)
    resposta.raise_for_status()

    soup = BeautifulSoup(resposta.text, "html.parser")
    formulario = soup.find("form")
    if not formulario:
        raise RuntimeError("Formulario de login nao encontrado.")

    payload = {
        campo["name"]: campo.get("value", "")
        for campo in formulario.find_all("input")
        if campo.get("name")
    }
    payload["form:username"] = usuario
    payload["form:password"] = senha

    botao = formulario.find("input", {"type": "submit"})
    if botao and botao.get("name"):
        payload[botao["name"]] = botao.get("value", "")

    post_url = urljoin(LOGIN_URL, formulario.get("action", LOGIN_URL))
    resposta = sessao.post(post_url, data=payload, timeout=30)
    resposta.raise_for_status()

    cadastro = sessao.get(CADASTRO_URL, timeout=30)
    cadastro.raise_for_status()
    if tem_formulario_login(cadastro.text):
        raise RuntimeError("O SINAN retornou para a tela de login.")

    return sessao, cadastro.text


def autenticar_com_retentativa(usuario, senha, tentativas, intervalo):
    ultimo_erro = None
    for numero in range(1, tentativas + 1):
        try:
            return autenticar(usuario, senha)
        except requests.RequestException as erro:
            ultimo_erro = erro
            if numero < tentativas:
                print(f"Falha de conexao. Nova tentativa em {intervalo}s.")
                time.sleep(intervalo)
    raise RuntimeError(f"Nao foi possivel acessar o SINAN: {ultimo_erro}")


def montar_payload(ficha, view_state):
    payload = {
        "AJAXREQUEST": "_viewRoot",
        "form": "form",
        "form:botaoOk": "form:botaoOk",
        "form:categoria_localidade_bairro_residencia": "BAIRRO",
        "form:desBairro": "",
        "form:dtNascimentoInputCurrentDate": ficha["mes_referencia"],
        "form:dtNascimentoInputDate": ficha["data_nascimento"],
        "form:dtNotificacaoInputCurrentDate": ficha["mes_referencia"],
        "form:dtNotificacaoInputDate": ficha["data_notificacao"],
        "form:dtPrimeirosSintomasInputCurrentDate": ficha["mes_referencia"],
        "form:dtPrimeirosSintomasInputDate": ficha["data_primeiros_sintomas"],
        "form:notificacao_nomePaciente": ficha["nome_paciente"],
        "form:notificacao_nome_mae": ficha["nome_mae"],
        "form:notificacao_paciente_endereco_bairro_id": ficha.get("bairro_id", ""),
        "form:notificacao_paciente_endereco_bairro_noBairro": ficha["bairro"],
        "form:notificacao_paciente_endereco_bairro_noBairrocomboboxField": ficha["bairro"],
        "form:notificacao_paciente_endereco_municipio_id": ficha["municipio_residencia_id"],
        "form:notificacao_paciente_endereco_municipio_noMunicipio": ficha["municipio_residencia"],
        "form:notificacao_paciente_endereco_municipio_noMunicipiocomboboxField": ficha["municipio_residencia"],
        "form:notificacao_paciente_endereco_municipio_uf_id": ficha["uf_residencia_id"],
        "form:notificacao_paciente_endereco_municipio_uf_pais_id": "1",
        "form:notificacao_paciente_endereco_municipio_uf_pais_noPais": "BRASIL",
        "form:notificacao_paciente_endereco_municipio_uf_pais_noPaiscomboboxField": "BRASIL",
        "form:notificacao_paciente_endereco_noLogradouro": ficha["logradouro"],
        "form:notificacao_paciente_endereco_numeroCasa": ficha["numero_residencia"],
        "form:notificacao_paciente_endereco_zona": ficha["zona"],
        "form:notificacao_paciente_escolaridade": ficha.get("escolaridade", ""),
        "form:notificacao_paciente_gestante": ficha["gestante"],
        "form:notificacao_paciente_idade": ficha["idade"],
        "form:notificacao_paciente_raca": ficha["raca"],
        "form:notificacao_paciente_sexo": ficha["sexo"],
        "form:notificacao_paciente_tipoIdade": ficha["tipo_idade"],
        "form:notificacao_unidadeSaude_coCnes": ficha["cnes"],
        "form:notificacao_unidadeSaude_estabelecimento": ficha["unidade_saude"],
        "form:notificacao_unidadeSaude_estabelecimentocomboboxField": ficha["unidade_saude"],
        "form:notificacao_unidadeSaude_municipio_id": ficha["municipio_unidade_id"],
        "form:notificacao_unidadeSaude_municipio_noMunicipio": ficha["municipio_unidade"],
        "form:notificacao_unidadeSaude_municipio_noMunicipiocomboboxField": ficha["municipio_unidade"],
        "form:notificacao_unidadeSaude_municipio_uf_id": ficha["uf_unidade_id"],
        "form:nuNotificacao": ficha["numero_notificacao"],
        "form:primeirosSintomas": ficha["semana_primeiros_sintomas"],
        "form:richagravo": ficha["agravo"],
        "form:richagravocomboboxField": ficha["agravo"],
        "form:semNotificacao": ficha["semana_notificacao"],
        "javax.faces.ViewState": view_state,
    }

    # Campos vazios que o formulario JSF espera receber.
    vazios = [
        "form:notificacao_paciente_endereco_cep",
        "form:notificacao_paciente_endereco_coLogradouro",
        "form:notificacao_paciente_endereco_complemento",
        "form:notificacao_paciente_endereco_distrito_id",
        "form:notificacao_paciente_endereco_distrito_noDistrito",
        "form:notificacao_paciente_endereco_distrito_noDistritocomboboxField",
        "form:notificacao_paciente_endereco_geoCampoDois",
        "form:notificacao_paciente_endereco_geoCampoUm",
        "form:notificacao_paciente_endereco_pontoReferencia",
        "form:notificacao_paciente_telefone",
        "form:modalCadastradarNovaNotificacaoOpenedState",
        "form:modalNotificacaoCadastradaSemInvestigacaoOpenedState",
        "form:modalNotificacaoComInvestigacaoOpenedState",
        "form:modalNotificacaoExisteNaoContarOpenedState",
        "form:modalNotificacaoExistenteIgnorarOpenedState",
        "form:modalNotificacaoExistenteInterlocutorOpenedState",
        "form:modalNotificacaoExistenteOpenedState",
        "form:modalPossivelDuplicidadeOpenedState",
    ]
    payload.update({campo: "" for campo in vazios})
    return payload


def parametros_ajax(html, campo_id):
    soup = BeautifulSoup(html, "html.parser")
    campo = soup.find(id=campo_id)
    if not campo:
        raise RuntimeError(f"Campo nao encontrado: {campo_id}")

    def ler_codigo(codigo):
        grupo = re.search(r"similarityGroupingId':'([^']+)'", codigo)
        bloco = re.search(r"parameters':\{([^}]*)\}", codigo)
        if not grupo or not bloco:
            return None
        parametros = dict(re.findall(r"'([^']+)':'([^']*)'", bloco.group(1)))
        parametros.setdefault(grupo.group(1), grupo.group(1))
        return parametros

    for atributo in ("onchange", "onblur", "onclick", "onselect"):
        codigo = campo.get(atributo, "")
        parametros = ler_codigo(codigo)
        if parametros:
            return parametros

        for nome_funcao in re.findall(r"\b([A-Za-z_]\w*)\s*\(", codigo):
            for script in soup.find_all("script"):
                texto = script.get_text()
                if f"{nome_funcao}=function" in texto:
                    parametros = ler_codigo(texto)
                    if parametros:
                        return parametros

    raise RuntimeError(f"Evento AJAX nao encontrado: {campo_id}")


def parametros_calendario(html, campo_id):
    # rich:calendar: o evento fica no 'onchanged' do script new Calendar(...).
    if not campo_id.endswith("InputDate"):
        return None
    base = campo_id[: -len("InputDate")]
    inicio = html.find(f"new Calendar('{base}'")
    if inicio < 0:
        return None
    trecho = html[inicio:]
    trecho = trecho[: trecho.find(".load()")] if ".load()" in trecho else trecho
    onchanged = re.search(r"'onchanged':function\(event\)\{(.*?)\}\s*\)\s*\}", trecho)
    if not onchanged:
        return None
    grupo = re.search(r"similarityGroupingId':'([^']+)'", onchanged.group(1))
    bloco = re.search(r"parameters':\{([^}]*)\}", onchanged.group(1))
    if not grupo or not bloco:
        return None
    parametros = dict(re.findall(r"'([^']+)':'([^']*)'", bloco.group(1)))
    parametros.setdefault(grupo.group(1), grupo.group(1))
    return parametros


def parametros_ajax_em(htmls, campo_id):
    # Procura o evento nos HTMLs mais recentes primeiro (secoes re-renderizadas).
    for html in htmls:
        try:
            return parametros_ajax(html, campo_id)
        except RuntimeError:
            continue
    for html in htmls:
        parametros = parametros_calendario(html, campo_id)
        if parametros:
            return parametros
    raise RuntimeError(f"Evento AJAX nao encontrado: {campo_id}")


def valor_campo(html, campo_id):
    campo = BeautifulSoup(html, "html.parser").find(id=campo_id)
    return campo.get("value", "").strip() if campo else None


def executar_ajax(sessao, htmls, payload, view_state, campo_id):
    dados = dict(payload)
    dados.pop("form:botaoOk", None)
    dados.update(
        {
            "AJAXREQUEST": "_viewRoot",
            "AJAX:EVENTS_COUNT": "1",
            "javax.faces.ViewState": view_state,
            **parametros_ajax_em(htmls, campo_id),
        }
    )
    resposta = sessao.post(
        CADASTRO_URL,
        data=dados,
        headers={
            "Accept": "text/xml,application/xml,text/html,*/*",
            "X-Requested-With": "XMLHttpRequest",
        },
        timeout=30,
    )
    resposta.raise_for_status()

    match = re.search(
        r'name="javax\.faces\.ViewState"[^>]*value="([^"]+)"',
        resposta.text,
    )
    return (match.group(1) if match else view_state), resposta.text


def preparar_formulario(sessao, html, ficha, info=None):
    view_state = extrair_view_state(html)
    payload = montar_payload(ficha, view_state)
    htmls = [html]

    # Datas primeiro: o servidor calcula a semana epidemiologica (campos de
    # semana sao desabilitados). O bairro so e aceito depois do municipio.
    campos_ajax = [
        "form:dtNotificacaoInputDate",
        "form:dtPrimeirosSintomasInputDate",
        "form:notificacao_unidadeSaude_municipio_uf_id",
        "form:notificacao_unidadeSaude_municipio_id",
        "form:notificacao_unidadeSaude_coCnes",
        "form:notificacao_paciente_sexo",
        "form:notificacao_paciente_endereco_municipio_uf_id",
        "form:notificacao_paciente_endereco_municipio_id",
        "form:notificacao_paciente_endereco_bairro_id",
    ]
    for campo_id in campos_ajax:
        view_state, texto = executar_ajax(sessao, htmls, payload, view_state, campo_id)
        htmls.insert(0, texto)
        if info is not None:
            info.setdefault("eventos_executados", []).append(campo_id)
            if campo_id == "form:notificacao_unidadeSaude_coCnes":
                info["unidade_devolvida_cnes"] = valor_campo(
                    texto, "form:notificacao_unidadeSaude_estabelecimentocomboboxField"
                )
            if campo_id == "form:notificacao_paciente_endereco_bairro_id":
                info["bairro_devolvido"] = valor_campo(
                    texto, "form:notificacao_paciente_endereco_bairro_noBairrocomboboxField"
                )
                info["categoria_devolvida"] = valor_campo(
                    texto, "form:categoria_localidade_bairro_residencia"
                )
            for campo_semana in ("form:semNotificacao", "form:primeirosSintomas"):
                valor = valor_campo(texto, campo_semana)
                if valor:
                    info[f"semana_devolvida[{campo_semana}]"] = valor

    return montar_payload(ficha, view_state)


CAMPOS_NAO_PESSOAIS = [
    "form:richagravo",
    "form:dtNotificacaoInputDate",
    "form:dtPrimeirosSintomasInputDate",
    "form:semNotificacao",
    "form:primeirosSintomas",
    "form:nuNotificacao",
    "form:notificacao_unidadeSaude_municipio_uf_id",
    "form:notificacao_unidadeSaude_municipio_id",
    "form:notificacao_unidadeSaude_coCnes",
    "form:notificacao_unidadeSaude_estabelecimento",
    "form:notificacao_paciente_sexo",
    "form:notificacao_paciente_gestante",
    "form:notificacao_paciente_raca",
    "form:notificacao_paciente_escolaridade",
    "form:notificacao_paciente_endereco_municipio_uf_id",
    "form:notificacao_paciente_endereco_municipio_uf_pais_id",
    "form:notificacao_paciente_endereco_municipio_uf_pais_noPais",
    "form:notificacao_paciente_endereco_municipio_uf_pais_noPaiscomboboxField",
    "form:notificacao_paciente_endereco_municipio_id",
    "form:notificacao_paciente_endereco_zona",
    "form:notificacao_paciente_endereco_bairro_id",
    "form:notificacao_paciente_endereco_bairro_noBairro",
    "form:categoria_localidade_bairro_residencia",
]


def main():
    parser = argparse.ArgumentParser(description="Envia uma ficha para o SINAN.")
    parser.add_argument("--arquivo-ficha", type=Path, required=True)
    parser.add_argument("--confirmar-numero")
    parser.add_argument("--tentativas-login", type=int, default=5)
    parser.add_argument("--intervalo", type=int, default=60)
    parser.add_argument(
        "--simular",
        action="store_true",
        help="Executa login e AJAX, monta o payload e NAO faz o POST final.",
    )
    args = parser.parse_args()
    ficha = json.loads(args.arquivo_ficha.read_text(encoding="utf-8"))
    numero = str(ficha["numero_notificacao"])
    if not args.simular and args.confirmar_numero != numero:
        raise Exception("Numero de confirmacao incorreto. Envio cancelado.")
    pendentes = [chave for chave, valor in ficha.items() if str(valor).strip() == "PREENCHER"]
    if pendentes:
        raise Exception(f"Ficha com campos a preencher: {', '.join(pendentes)}")

    enviar_ficha(ficha, args.simular)

def enviar_ficha(ficha, simular=False):
    usuario = os.getenv("SINAN_USERNAME")
    senha = os.getenv("SINAN_PASSWORD")
    if not usuario or not senha:
        raise Exception("Defina SINAN_USERNAME e SINAN_PASSWORD.")
    sessao, html = autenticar_com_retentativa(usuario, senha, 5, 5)
    info = {}
    payload = preparar_formulario(sessao, html, ficha, info)

    if simular or 1:
        print("SIMULACAO: nenhum POST final foi feito.")
        print(f"Eventos AJAX executados: {len(info['eventos_executados'])}/9")
        for campo_id in info["eventos_executados"]:
            print(f"  ok {campo_id}")
        print(f"Chaves do payload ({len(payload)}):")
        for chave in sorted(payload):
            if chave != "javax.faces.ViewState":
                print(f"  {chave}")
        print("Campos nao pessoais:")
        for chave in CAMPOS_NAO_PESSOAIS:
            print(f"  {chave} = {payload.get(chave)!r}")
        print("Devolvido pelo SINAN nos AJAX:")
        for chave, valor in info.items():
            if chave != "eventos_executados":
                print(f"  {chave} = {valor!r}")
        print(f"Unidade no JSON: {ficha['unidade_saude']!r}")
        return info
    else:
        resposta = sessao.post(CADASTRO_URL, data=payload, timeout=30)
        resposta.raise_for_status()
        resposta.encoding = "utf-8"

        mensagens = extrair_mensagens(resposta.text)
        sucesso = any("realizada com sucesso" in texto.lower() for texto in mensagens)
        relatorio = {
            "data_hora": datetime.now().isoformat(timespec="seconds"),
            "numero_notificacao": ficha["numero_notificacao"],
            "resultado": "CADASTRO_CONFIRMADO" if sucesso else "RESPOSTA_REQUER_ANALISE",
            "status_http": resposta.status_code,
            "voltou_login": tem_formulario_login(resposta.text),
            "mensagens_sinan": mensagens,
        }

        caminho = Path(f"relatorios/resultado_envio_ficha_{ficha["numero_notificacao"]}.json")
        caminho.parent.mkdir(exist_ok=True)
        caminho.write_text(
            json.dumps(relatorio, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(json.dumps(relatorio, ensure_ascii=False, indent=2))
        return relatorio


if __name__ == "__main__":
    main()
