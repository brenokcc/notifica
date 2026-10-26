"""Extrai a tabela de bairros (ID -> nome/categoria) do SINAN via AJAX.

Somente eventos AJAX de consulta sao disparados. Nenhum botao de salvar ou
confirmar (form:botaoOk) e enviado.
"""

import argparse
import csv
import os
import re
import sys
import time
import unicodedata
from pathlib import Path

from bs4 import BeautifulSoup

from .enviar_ficha import (
    CADASTRO_URL,
    autenticar_com_retentativa,
    extrair_view_state,
    parametros_ajax,
    tem_formulario_login,
)


UF_ID = "12"
MUNICIPIO_ID = "500370"
MUNICIPIO_NOME = "DOURADOS"

CAMPO_UF = "form:notificacao_paciente_endereco_municipio_uf_id"
CAMPO_MUNICIPIO = "form:notificacao_paciente_endereco_municipio_id"
CAMPO_BAIRRO = "form:notificacao_paciente_endereco_bairro_id"
CAMPO_NOME_BAIRRO = "form:notificacao_paciente_endereco_bairro_noBairrocomboboxField"
CAMPO_CATEGORIA = "form:categoria_localidade_bairro_residencia"

ARQUIVO_CSV = Path("dados/bairros_sinan_ids.csv")
GRAVAR_A_CADA = 25


class SessaoExpirada(Exception):
    pass


def campos_formulario(html):
    """Le os campos do formulario com seus valores atuais, sem botoes."""
    soup = BeautifulSoup(html, "html.parser")
    formulario = soup.find("form", id="form") or soup.find("form")
    dados = {}
    if not formulario:
        return dados
    for campo in formulario.find_all(["input", "select", "textarea"]):
        nome = campo.get("name")
        if not nome or nome == "javax.faces.ViewState":
            continue
        tipo = (campo.get("type") or "").lower()
        if tipo in ("submit", "button", "image", "reset"):
            continue
        if tipo in ("checkbox", "radio") and not campo.has_attr("checked"):
            continue
        if campo.name == "select":
            opcao = campo.find("option", selected=True)
            dados[nome] = opcao.get("value", "") if opcao else ""
        elif campo.name == "textarea":
            dados[nome] = campo.get_text()
        else:
            dados[nome] = campo.get("value", "")
    dados["form"] = "form"
    return dados


def ler_view_state(texto, anterior):
    soup = BeautifulSoup(texto, "html.parser")
    campo = soup.find("input", {"name": "javax.faces.ViewState"}) or soup.find(
        id="javax.faces.ViewState"
    )
    if campo and campo.get("value"):
        return campo["value"]
    match = re.search(
        r'name="javax\.faces\.ViewState"[^>]*value="([^"]+)"', texto
    ) or re.search(r'value="([^"]+)"[^>]*name="javax\.faces\.ViewState"', texto)
    return match.group(1) if match else anterior


def resposta_expirada(resposta):
    texto = resposta.text
    return (
        "login.jsf" in resposta.url
        or resposta.headers.get("Ajax-Expired")
        or "ViewExpiredException" in texto
        or tem_formulario_login(texto)
    )


def valor_elemento(soup, elemento_id):
    elemento = soup.find(id=elemento_id) or soup.find(attrs={"name": elemento_id})
    if not elemento:
        return None
    if elemento.name == "select":
        opcao = elemento.find("option", selected=True)
        return opcao.get_text(strip=True) if opcao else ""
    if elemento.name == "input":
        return elemento.get("value", "").strip()
    return " ".join(elemento.get_text(" ", strip=True).split())


def disparar(sessao, html_eventos, dados, view_state, campo_id):
    """Dispara um evento AJAX de consulta e devolve (view_state, texto)."""
    parametros = None
    for html in html_eventos:
        try:
            parametros = parametros_ajax(html, campo_id)
            break
        except RuntimeError:
            continue
    if parametros is None:
        raise RuntimeError(f"Evento AJAX nao encontrado: {campo_id}")

    envio = dict(dados)
    envio.pop("form:botaoOk", None)
    envio.update(
        {
            "AJAXREQUEST": "_viewRoot",
            "AJAX:EVENTS_COUNT": "1",
            "javax.faces.ViewState": view_state,
            **parametros,
        }
    )
    assert "form:botaoOk" not in envio

    resposta = sessao.post(
        CADASTRO_URL,
        data=envio,
        headers={
            "Accept": "text/xml,application/xml,text/html,*/*",
            "X-Requested-With": "XMLHttpRequest",
        },
        timeout=30,
    )
    resposta.raise_for_status()
    resposta.encoding = resposta.encoding or "utf-8"
    if resposta_expirada(resposta):
        raise SessaoExpirada()
    return ler_view_state(resposta.text, view_state), resposta.text


def iniciar(usuario, senha, uf_id=UF_ID, municipio_id=MUNICIPIO_ID,
            municipio_nome=MUNICIPIO_NOME):
    """Autentica e prepara UF/municipio de residencia."""
    sessao, html = autenticar_com_retentativa(usuario, senha, 3, 30)
    view_state = extrair_view_state(html)
    dados = campos_formulario(html)
    dados.update(
        {
            CAMPO_UF: uf_id,
            "form:notificacao_paciente_endereco_municipio_uf_pais_id": "1",
            "form:notificacao_paciente_endereco_municipio_uf_pais_noPais": "BRASIL",
            "form:notificacao_paciente_endereco_municipio_uf_pais_noPaiscomboboxField": "BRASIL",
        }
    )
    html_eventos = [html]

    view_state, texto = disparar(sessao, html_eventos, dados, view_state, CAMPO_UF)
    html_eventos.insert(0, texto)

    dados.update(
        {
            CAMPO_MUNICIPIO: municipio_id,
            "form:notificacao_paciente_endereco_municipio_noMunicipio": municipio_nome,
            "form:notificacao_paciente_endereco_municipio_noMunicipiocomboboxField": municipio_nome,
        }
    )
    view_state, texto = disparar(
        sessao, html_eventos, dados, view_state, CAMPO_MUNICIPIO
    )
    # A secao de residencia e re-renderizada: o evento do bairro pode estar aqui.
    html_eventos.insert(0, texto)
    return sessao, html_eventos, dados, view_state


def consultar_bairro(sessao, html_eventos, dados, view_state, bairro_id):
    envio = dict(dados)
    envio.update(
        {
            CAMPO_BAIRRO: str(bairro_id),
            "form:notificacao_paciente_endereco_bairro_noBairro": "",
            CAMPO_NOME_BAIRRO: "",
        }
    )
    view_state, texto = disparar(sessao, html_eventos, envio, view_state, CAMPO_BAIRRO)
    soup = BeautifulSoup(texto, "html.parser")
    nome = valor_elemento(soup, CAMPO_NOME_BAIRRO) or ""
    categoria = valor_elemento(soup, CAMPO_CATEGORIA) or ""
    return view_state, nome, categoria, texto


def mostrar_estrutura(texto):
    """Mostra a estrutura da resposta AJAX sem dados de sessao."""
    soup = BeautifulSoup(texto, "html.parser")
    print("Estrutura da resposta AJAX (tag, id/name, tamanho do valor):")
    for elemento in soup.find_all(True):
        ident = elemento.get("id") or elemento.get("name")
        if not ident or "ViewState" in ident:
            continue
        valor = elemento.get("value")
        extra = f"value_len={len(valor)}" if valor is not None else ""
        if ident in (CAMPO_NOME_BAIRRO, CAMPO_CATEGORIA, CAMPO_BAIRRO):
            extra += f" value={valor!r}" if valor is not None else (
                f" texto={elemento.get_text(' ', strip=True)[:80]!r}"
            )
        print(f"  <{elemento.name}> {ident} {extra}")


def ler_ids_gravados():
    if not ARQUIVO_CSV.exists():
        return set()
    with ARQUIVO_CSV.open(encoding="utf-8", newline="") as arquivo:
        return {
            int(linha["ID"])
            for linha in csv.DictReader(arquivo, delimiter=";")
            if linha.get("ID", "").isdigit()
        }


def gravar(linhas):
    if not linhas:
        return
    novo = not ARQUIVO_CSV.exists()
    ARQUIVO_CSV.parent.mkdir(exist_ok=True)
    with ARQUIVO_CSV.open("a", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        if novo:
            escritor.writerow(["ID", "NM_BAIRRO", "CATEGORIA"])
        escritor.writerows(linhas)
    linhas.clear()


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c)).upper()


def main():
    global ARQUIVO_CSV
    parser = argparse.ArgumentParser(description="Extrai IDs de bairro do SINAN.")
    parser.add_argument("--inicio", type=int, default=1)
    parser.add_argument("--fim", type=int, default=700)
    parser.add_argument("--intervalo", type=float, default=0.3)
    parser.add_argument("--uf-id", default=UF_ID, help="Codigo da UF no SINAN (MS=12).")
    parser.add_argument("--municipio-id", default=MUNICIPIO_ID, help="Codigo IBGE (6 digitos).")
    parser.add_argument("--municipio-nome", default=MUNICIPIO_NOME)
    parser.add_argument("--arquivo", type=Path, default=ARQUIVO_CSV, help="CSV de saida.")
    parser.add_argument("--buscar", help="Texto(s) para filtrar, separados por virgula.")
    parser.add_argument(
        "--estrutura",
        action="store_true",
        help="Mostra a estrutura da resposta AJAX do primeiro ID consultado.",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ARQUIVO_CSV = args.arquivo
    local = (args.uf_id, args.municipio_id, args.municipio_nome)
    gravados = ler_ids_gravados()
    pendentes = [i for i in range(args.inicio, args.fim + 1) if i not in gravados]
    print(f"IDs na faixa: {args.fim - args.inicio + 1}; ja gravados: "
          f"{args.fim - args.inicio + 1 - len(pendentes)}; a consultar: {len(pendentes)}")

    usuario = os.getenv("SINAN_USERNAME")
    senha = os.getenv("SINAN_PASSWORD")
    if pendentes and (not usuario or not senha):
        raise SystemExit("Defina SINAN_USERNAME e SINAN_PASSWORD.")

    consultados = 0
    encontrados = 0
    maior_id = None
    buffer = []
    estrutura_mostrada = not args.estrutura

    try:
        if pendentes:
            sessao, html_eventos, dados, view_state = iniciar(usuario, senha, *local)
        for bairro_id in pendentes:
            try:
                view_state, nome, categoria, texto = consultar_bairro(
                    sessao, html_eventos, dados, view_state, bairro_id
                )
            except SessaoExpirada:
                print(f"Sessao expirada no ID {bairro_id}. Reautenticando...")
                sessao, html_eventos, dados, view_state = iniciar(usuario, senha, *local)
                try:
                    view_state, nome, categoria, texto = consultar_bairro(
                        sessao, html_eventos, dados, view_state, bairro_id
                    )
                except SessaoExpirada:
                    print("Sessao expirou de novo apos reautenticar. Parando.")
                    break

            consultados += 1
            if not estrutura_mostrada:
                mostrar_estrutura(texto)
                estrutura_mostrada = True

            if nome:
                encontrados += 1
                maior_id = bairro_id
                buffer.append([bairro_id, nome, categoria])
                print(f"  {bairro_id}: {nome} | {categoria}")
            if consultados % GRAVAR_A_CADA == 0:
                gravar(buffer)
                print(f"[{consultados}/{len(pendentes)}] gravado.")
            time.sleep(args.intervalo)
    finally:
        gravar(buffer)

    print()
    print(f"Total consultado: {consultados}")
    print(f"Total encontrado: {encontrados}")
    print(f"Maior ID com retorno (nesta execucao): {maior_id}")

    if args.buscar and ARQUIVO_CSV.exists():
        termos = [normalizar(t.strip()) for t in args.buscar.split(",") if t.strip()]
        print(f"\nLinhas contendo {termos}:")
        with ARQUIVO_CSV.open(encoding="utf-8", newline="") as arquivo:
            for linha in csv.DictReader(arquivo, delimiter=";"):
                texto = normalizar(f"{linha['NM_BAIRRO']} {linha['CATEGORIA']}")
                if any(t in texto for t in termos):
                    print(f"  {linha['ID']};{linha['NM_BAIRRO']};{linha['CATEGORIA']}")


if __name__ == "__main__":
    main()
