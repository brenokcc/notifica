from slth.db import models, role, meta
import os
import json
from django.conf import settings
from slth.components import GeoMap
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from slth.utils import age
import qrcode
import base64
from io import BytesIO
from uuid import uuid1
from django.db import transaction


@role("administrador", username="cpf")
class Administrador(models.Model):
    cpf = models.CharField(verbose_name="CPF", blank=False)
    nome = models.CharField(verbose_name="Nome")
    email = models.CharField(verbose_name="E-mail", null=True, blank=True)

    class Meta:
        verbose_name = "Administrador"
        verbose_name_plural = "Administradores"

    def __str__(self):
        return self.nome


class Funcao(models.Model):
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "Função"
        verbose_name_plural = "Funções"

    def __str__(self):
        return self.nome


class NotificanteQuerySet(models.QuerySet):
    def all(self):
        return super().all().fields("cpf", "nome", "email", "funcao", "get_unidade")


class Notificante(models.Model):
    cpf = models.CharField(verbose_name="CPF", blank=False)
    nome = models.CharField(verbose_name="Nome")
    email = models.CharField(verbose_name="E-mail", null=True, blank=True)
    funcao = models.ForeignKey(Funcao, verbose_name="Função", on_delete=models.CASCADE)

    objects = NotificanteQuerySet()

    class Meta:
        verbose_name = "Notificante"
        verbose_name_plural = "Notificantes"

    def __str__(self):
        return self.nome

    @meta("Unidade")
    def get_unidade(self):
        return ", ".join(self.unidadesaude_set.values_list("nome", flat=True))


class GestorUnidadeQuerySet(models.QuerySet):
    def all(self):
        return super().all().fields("cpf", "nome", "get_unidade")


class GestorUnidade(models.Model):
    cpf = models.CharField(verbose_name="CPF", blank=False)
    nome = models.CharField(verbose_name="Nome")
    email = models.CharField(verbose_name="E-mail", null=True, blank=True)

    objects = GestorUnidadeQuerySet()

    class Meta:
        verbose_name = "Gestor de Unidade"
        verbose_name_plural = "Gestores de Unidade"

    def __str__(self):
        return self.nome

    @meta("Unidade")
    def get_unidade(self):
        return ", ".join(self.unidadesaude_set.values_list("nome", flat=True))


class GestorMunicipalQuerySet(models.QuerySet):
    def all(self):
        return super().all().fields("cpf", "nome", "get_municipio")


class GestorMunicipal(models.Model):
    cpf = models.CharField(verbose_name="CPF", blank=False)
    nome = models.CharField(verbose_name="Nome")
    email = models.CharField(verbose_name="E-mail", null=True, blank=True)

    objects = GestorMunicipalQuerySet()

    class Meta:
        verbose_name = "Gestor de Municipal"
        verbose_name_plural = "Gestores Municipais"

    def __str__(self):
        return self.nome

    @meta("Município")
    def get_municipio(self):
        return ", ".join(self.municipio_set.values_list("nome", flat=True))


class ReguladorQuerySet(models.QuerySet):
    def all(self):
        return super().all().fields("cpf", "nome", "get_municipio")


class Regulador(models.Model):
    cpf = models.CharField(verbose_name="CPF", blank=False)
    nome = models.CharField(verbose_name="Nome")
    email = models.CharField(verbose_name="E-mail", null=True, blank=True)

    objects = ReguladorQuerySet()

    class Meta:
        verbose_name = "Regulador"
        verbose_name_plural = "Reguladores"

    def __str__(self):
        return self.nome

    @meta("Município")
    def get_municipio(self):
        return ", ".join(self.municipio_set.values_list("nome", flat=True))


class TipoNotificacao(models.Model):
    codigo = models.CharField(verbose_name="Código")
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "Tipo de Notificação"
        verbose_name_plural = "Tipos de Notificação"

    def __str__(self):
        return self.nome


class Doenca(models.Model):
    nome = models.CharField(verbose_name="Nome")
    cid10 = models.CharField(verbose_name="CID10")
    modelo_ficha = models.CharField(
        verbose_name="Modelo da Ficha",
        null=True,
        choices=[
            ["ficha/padrao.html", "Padrão"],
            ["ficha/dengue-chikungunya.html", "Dengue/Chikungunya"],
        ],
    )

    class Meta:
        verbose_name = "Doença"
        verbose_name_plural = "Doenças"

    def __str__(self):
        return self.nome


class Ocupacao(models.Model):
    codigo = models.CharField(verbose_name="Código")
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "Ocupação"
        verbose_name_plural = "Ocupações"

    def __str__(self):
        return self.nome


class Pais(models.Model):
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Países"

    def __str__(self):
        return self.nome


class Estado(models.Model):
    codigo = models.CharField(verbose_name="Código IBGE", max_length=2, unique=True)
    sigla = models.CharField(verbose_name="Sigla", max_length=2, unique=True)
    nome = models.CharField(verbose_name="Nome", max_length=60, unique=True)

    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"
        ordering = ["nome"]

    @property
    def id(self):
        return self.codigo

    def __str__(self):
        return "%s/%s" % (self.nome, self.sigla)


@role("gm", username="gestores__cpf", municipio="pk")
@role("regulador", username="reguladores__cpf", municipio="pk")
class Municipio(models.Model):
    estado = models.ForeignKey(Estado, verbose_name="Estado", on_delete=models.CASCADE)
    codigo = models.CharField(max_length=7, verbose_name="Código IBGE", unique=True)
    nome = models.CharField(verbose_name="Nome", max_length=60)
    gestores = models.ManyToManyField(GestorMunicipal, blank=True)
    reguladores = models.ManyToManyField(Regulador, blank=True)

    class Meta:
        verbose_name = "Município"
        verbose_name_plural = "Municípios"

    def __str__(self):
        return "%s/%s" % (self.nome, self.estado.sigla)

    def serializer(self):
        return (
            super()
            .serializer()
            .fieldset("Dados Gerais", (("codigo", "nome"), "estado"))
            .fieldset("Equipe", ("gestores", "reguladores"))
        )

    def formfactory(self):
        return (
            super()
            .formfactory()
            .fieldset("Dados Gerais", (("codigo", "nome"), "estado"))
            .fieldset(
                "Equipe",
                (
                    "gestores:gestormunicipal.cadastrar",
                    "reguladores:regulador.cadastrar",
                ),
            )
        )


@role("notificante", username="notificantes__cpf", unidade="pk")
@role("gu", username="gestores__cpf", unidade="pk")
class UnidadeSaude(models.Model):
    codigo = models.CharField(verbose_name="Código")
    nome = models.CharField(verbose_name="Nome")

    municipio = models.ForeignKey(
        Municipio, verbose_name="Município", on_delete=models.CASCADE
    )
    gestores = models.ManyToManyField(GestorUnidade, blank=True)
    notificantes = models.ManyToManyField(Notificante, blank=True)

    class Meta:
        icon = "building"
        verbose_name = "Unidade de Saúde"
        verbose_name_plural = "Unidades de Saúde"

    def __str__(self):
        return self.nome

    def serializer(self):
        return (
            super()
            .serializer()
            .fieldset("Dados Gerais", (("codigo", "nome"), "municipio"))
            .fieldset("Equipe", ("gestores", "notificante"))
        )

    def formfactory(self):
        return (
            super()
            .formfactory()
            .fieldset("Dados Gerais", (("codigo", "nome"), "municipio"))
            .fieldset(
                "Equipe",
                (
                    "gestores:gestorunidade.cadastrar",
                    "notificantes:notificante.cadastrar",
                ),
            )
        )


class SolicitacaoCadastroNotificante(models.Model):
    cpf = models.CharField(verbose_name="CPF", blank=False)
    nome = models.CharField(verbose_name="Nome")
    email = models.CharField(verbose_name="E-mail")
    funcao = models.ForeignKey(Funcao, verbose_name="Função", on_delete=models.CASCADE)
    unidades = models.ManyToManyField(UnidadeSaude, verbose_name="Unidades", blank=True)
    data_solicitacao = models.DateTimeField(
        verbose_name="Data da Solicitação", auto_now_add=True
    )
    aprovada = models.BooleanField(verbose_name="Aprovada", null=True)
    observacao = models.TextField(verbose_name="Observação")

    class Meta:
        icon = "user-plus"
        verbose_name = "Solicitação de Cadastro"
        verbose_name_plural = "Solicitações de Cadastro"

    def __str__(self):
        return self.nome

    def formfactory(self):
        return (
            super()
            .formfactory()
            .fieldset(
                "Dados Gerais", (("cpf", "nome"), ("email", "funcao"), "unidades")
            )
            .info("Você receberá um e-mail assim que sua solicitação for avaliada.")
        )

    @transaction.atomic
    def processar(self):
        if self.aprovada:
            notificante = (
                Notificante.objects.filter(cpf=self.cpf).first() or Notificante()
            )
            enviar_senha = notificante.pk is None
            notificante.cpf = self.cpf
            notificante.nome = self.nome
            notificante.email = self.email
            notificante.funcao = self.funcao
            notificante.save()
            for unidade in self.unidades.all():
                unidade.notificantes.add(notificante)
                unidade.post_save()
            if enviar_senha:
                user = User.objects.get(username=self.cpf)
                user.set_password("123")
                user.save()
        else:
            print(99999)


class Sexo(models.Model):
    codigo = models.CharField(verbose_name="Código")
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "Sexo"
        verbose_name_plural = "Sexos"

    def __str__(self):
        return self.nome


class PeriodoGestacao(models.Model):
    codigo = models.CharField(verbose_name="Código")
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "Período de Gestação"
        verbose_name_plural = "Períodos de Gestação"

    def __str__(self):
        return self.nome


class Raca(models.Model):
    codigo = models.CharField(verbose_name="Código")
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "Raça"
        verbose_name_plural = "Raças"

    def __str__(self):
        return self.nome


class Escolaridade(models.Model):
    codigo = models.CharField(verbose_name="Código")
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "Escolaridade"
        verbose_name_plural = "Escolaridades"

    def __str__(self):
        return self.nome


class Zona(models.Model):
    codigo = models.CharField(verbose_name="Código")
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "Zona"
        verbose_name_plural = "Zonas"

    def __str__(self):
        return self.nome


class SinalClinico(models.Model):
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "Sinal Clínico"
        verbose_name_plural = "Sinais Clínicos"

    def __str__(self):
        return self.nome


class DoencaPreExistente(models.Model):
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "Doença Pré-Existente"
        verbose_name_plural = "Doenças Pré-Existentes"

    def __str__(self):
        return self.nome


class TipoLocal(models.Model):
    codigo = models.CharField(verbose_name="Código")
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "Tipo de Local"
        verbose_name_plural = "Tipos de Locais"

    def __str__(self):
        return self.nome


class ClassificacaoInfeccao(models.Model):
    codigo = models.CharField(verbose_name="Código")
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "Classificação de Infecção"
        verbose_name_plural = "Classificações de Infecção"

    def __str__(self):
        return self.nome


class CriterioConfirmacao(models.Model):
    codigo = models.CharField(verbose_name="Código")
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "Critério de Confirmação"
        verbose_name_plural = "Critérios de Confirmação"

    def __str__(self):
        return self.nome


class ApresentacaoClinica(models.Model):
    codigo = models.CharField(verbose_name="Código")
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "Apresentação Clínica"
        verbose_name_plural = "Apresentações Clínicas"

    def __str__(self):
        return self.nome


class TipoEvolucao(models.Model):
    codigo = models.CharField(verbose_name="Código")
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "Tipo de Evolução"
        verbose_name_plural = "Tipos de Evolução"

    def __str__(self):
        return self.nome


class SinalAlarme(models.Model):
    codigo = models.CharField(verbose_name="Código")
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "Sinal de Alarme"
        verbose_name_plural = "Sinais de Alarme"

    def __str__(self):
        return self.nome


class SinalExtravasamentoPlasma(models.Model):
    codigo = models.CharField(verbose_name="Código")
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "Sinal de Extravasamento do Plasma"
        verbose_name_plural = "Sinais de Extravasamento do Plasma"

    def __str__(self):
        return self.nome


class SinalSangramentoGrave(models.Model):
    codigo = models.CharField(verbose_name="Código")
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "Sinal de Sangramento Grave"
        verbose_name_plural = "Sinais de Sangramento Grave"

    def __str__(self):
        return self.nome


class SinalComprometimentoOrgao(models.Model):
    codigo = models.CharField(verbose_name="Código")
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "Sinal de Comprometimento dos Órgãos"
        verbose_name_plural = "Sinais de Comprometimento dos Órgãos"

    def __str__(self):
        return self.nome


class Hospital(models.Model):
    nome = models.CharField(verbose_name="Nome")
    codigo = models.CharField(verbose_name="Código")
    municipio = models.ForeignKey(
        Municipio,
        verbose_name="Município",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    telefone = models.CharField(verbose_name="Telefone", null=True, blank=True)

    class Meta:
        verbose_name = "Hospital"
        verbose_name_plural = "Hospitais"

    def __str__(self):
        return self.nome


class NotificacaoIndividualQuerySet(models.QuerySet):
    def all(self):
        return (
            self.search("cpf", "nome")
            .fields("get_numero", "notificante", "data", "nome")
            .filters("municipio", "unidade", "validada")
        )

    @meta("Total de Notificações")
    def get_total(self):
        return self.total()

    @meta("Notificantes")
    def get_total_notificantes(self):
        return self.total("notificante")

    @meta("Pacientes")
    def get_total_pacientes(self):
        return self.total("cpf")

    @meta("Total por Unidade")
    def get_total_por_unidade(self):
        return self.counter("unidade", chart="bar")

    @meta("Total por Sexo")
    def get_total_por_sexo(self):
        return self.counter("sexo", chart="donut")

    @meta("Dourados/MS")
    def get_mapa(self):
        map = GeoMap(
            -54.815434332605591,
            -22.251316151125515,
            zoom=10.2,
            max_zoom=20,
            min_zoom=10,
            title="Geovisualização",
        )
        with open(os.path.join(settings.BASE_DIR, "api", "dourados.json")) as file:
            features = json.loads(file.read()).get("features")
            for feature in features:
                feature["properties"]["info"] = feature["properties"]["ubsf"]
                map.add_polygon_feature(feature)
            for notificacao in self:
                if notificacao.latitude and notificacao.longitude:
                    map.add_point(
                        notificacao.longitude, notificacao.latitude, notificacao
                    )
            return map


class NotificacaoIndividual(models.Model):
    # Dados Gerais
    doenca = models.ForeignKey(
        Doenca, verbose_name="Doença", on_delete=models.CASCADE, pick=True
    )
    data = models.DateField(verbose_name="Data")
    notificante = models.ForeignKey(
        Notificante, verbose_name="Notificante", on_delete=models.CASCADE
    )
    municipio = models.ForeignKey(
        Municipio, verbose_name="Município", on_delete=models.CASCADE, related_name="s1"
    )
    unidade = models.ForeignKey(
        UnidadeSaude, verbose_name="Unidade de Saúde", on_delete=models.CASCADE
    )
    data_primeiros_sintomas = models.DateField(
        verbose_name="Data dos Primeiros Sintomas"
    )

    # Dados do Indivíduo
    cpf = models.CharField(verbose_name="CPF", null=True, blank=False)
    cartao_sus = models.CharField(verbose_name="Cartão SUS", null=True, blank=True)
    nome = models.CharField(verbose_name="Nome")
    data_nascimento = models.DateField(
        verbose_name="Data de Nascimento", null=True, blank=True
    )
    idade = models.IntegerField(verbose_name="Idade", null=True, blank=True)
    sexo = models.ForeignKey(
        Sexo, verbose_name="Sexo", on_delete=models.CASCADE, pick=True
    )
    periodo_gestacao = models.ForeignKey(
        PeriodoGestacao,
        verbose_name="Período de Gestação",
        on_delete=models.CASCADE,
        pick=True,
    )
    raca = models.ForeignKey(
        Raca, verbose_name="Raça", on_delete=models.CASCADE, pick=True
    )
    escolaridade = models.ForeignKey(
        Escolaridade, verbose_name="Escolaridade", on_delete=models.CASCADE, pick=True
    )
    nome_mae = models.CharField(verbose_name="Nome da Mãe")

    # Dados Residenciais
    pais = models.ForeignKey(
        Pais,
        verbose_name="País",
        on_delete=models.CASCADE,
        null=True,
        related_name="s1",
    )
    cep = models.CharField(verbose_name="CEP", null=True, blank=True)
    municipio_residencia = models.ForeignKey(
        Municipio,
        verbose_name="Município da Residência",
        on_delete=models.CASCADE,
        related_name="s2",
        null=True,
        blank=True,
    )
    distrito = models.CharField(verbose_name="Distrito", null=True, blank=True)
    zona = models.ForeignKey(
        Zona, verbose_name="Zona", on_delete=models.CASCADE, null=True, pick=True
    )
    bairro = models.CharField(verbose_name="Bairro", null=True, blank=True)
    logradouro = models.CharField(verbose_name="Logradouro", null=True, blank=True)
    codigo_logradouro = models.CharField(
        verbose_name="Código do Logradouro", null=True, blank=True
    )
    numero_residencia = models.CharField(
        verbose_name="Número da Residência", null=True, blank=True
    )
    complemento = models.CharField(verbose_name="Complemento", null=True, blank=True)
    latitude = models.CharField(verbose_name="Latitude", null=True, blank=True)
    longitude = models.CharField(verbose_name="Longitude", null=True, blank=True)
    referencia = models.CharField(
        verbose_name="Ponto de Referência", null=True, blank=True
    )

    # Dados para Contato
    telefone = models.CharField(verbose_name="Telefone", null=True, blank=True)
    email = models.CharField(verbose_name="E-mail", null=True, blank=True)

    # Investigação
    data_investigacao = models.DateField(verbose_name="Data da Investigação")
    ocupacao_investigacao = models.ForeignKey(
        Ocupacao, verbose_name="Ocupação", on_delete=models.CASCADE, null=True
    )

    # Dados Clínicos
    sinais_clinicos = models.ManyToManyField(
        SinalClinico, verbose_name="Sinais Clínicos", pick=True, blank=True
    )
    doencas_pre_existentes = models.ManyToManyField(
        DoencaPreExistente, verbose_name="Doenças Pré-Existentes", pick=True, blank=True
    )

    # Sorologia (IgM) Chikungunya
    data_primeira_amostra_chikungunya = models.DateField(
        verbose_name="Coleta da 1ª Amostra", null=True, blank=True
    )
    resultado_primeira_amostra_chikungunya = models.IntegerField(
        verbose_name="Resultado da 1ª Amostra",
        null=True,
        blank=True,
        choices=[
            [i + 1, x]
            for i, x in enumerate(
                ["Reagente", "Não Reagente", "Inconclusivo", "Não Realizado"]
            )
        ],
        pick=True,
    )
    data_segunda_amostra_chikungunya = models.DateField(
        verbose_name="Coleta da 2ª Amostra", null=True, blank=True
    )
    resultado_segunda_amostra_chikungunya = models.IntegerField(
        verbose_name="Resultado da 2ª Amostra",
        null=True,
        blank=True,
        choices=[
            [i + 1, x]
            for i, x in enumerate(
                ["Reagente", "Não Reagente", "Inconclusivo", "Não Realizado"]
            )
        ],
        pick=True,
    )
    # Exame PRNT
    data_coleta_exame_prnt = models.DateField(
        verbose_name="Coleta Exame PRNT", null=True, blank=True
    )
    resultado_exame_prnt = models.IntegerField(
        verbose_name="Resultado do Exame PRNT",
        null=True,
        blank=True,
        choices=[
            [i + 1, x]
            for i, x in enumerate(
                ["Reagente", "Não Reagente", "Inconclusivo", "Não Realizado"]
            )
        ],
        pick=True,
    )

    # Sorologia (IgM) Dengue
    data_amostra_dengue = models.DateField(
        verbose_name="Data da Coleta", null=True, blank=True
    )
    resultado_amostra_dengue = models.IntegerField(
        verbose_name="Resultado Coleta",
        null=True,
        blank=True,
        choices=[
            [i + 1, x]
            for i, x in enumerate(
                ["Positivo", "Negativo", "Inconclusivo", "Não Realizado"]
            )
        ],
        pick=True,
    )

    # Exame NS1
    data_exame_ns1 = models.DateField(
        verbose_name="Data Exame NS1", null=True, blank=True
    )
    resultado_exame_ns1 = models.IntegerField(
        verbose_name="Resultado Exame NS1",
        null=True,
        blank=True,
        choices=[
            [i + 1, x]
            for i, x in enumerate(
                ["Positivo", "Negativo", "Inconclusivo", "Não Realizado"]
            )
        ],
        pick=True,
    )

    # Isolamento
    data_isolamento = models.DateField(
        verbose_name="Data da Coleta Isolamento", null=True, blank=True
    )
    resultado_isolamento = models.IntegerField(
        verbose_name="Resultado Isolamento",
        null=True,
        blank=True,
        choices=[
            [i + 1, x]
            for i, x in enumerate(
                ["Positivo", "Negativo", "Inconclusivo", "Não Realizado"]
            )
        ],
        pick=True,
    )

    # RT-PCR
    data_rt_pcr = models.DateField(
        verbose_name="Data da Coleta RT-PCR", null=True, blank=True
    )
    resultado_rt_pcr = models.IntegerField(
        verbose_name="Resultado RT-PCR",
        null=True,
        blank=True,
        choices=[
            [i + 1, x]
            for i, x in enumerate(
                ["Positivo", "Negativo", "Inconclusivo", "Não Realizado"]
            )
        ],
        pick=True,
    )
    sorotipo = models.IntegerField(
        verbose_name="Sorotipo",
        null=True,
        blank=True,
        choices=[
            [i + 1, x] for i, x in enumerate(["DENV 1", "DENV 2", "DENV 3", "DENV 4"])
        ],
        pick=True,
    )

    # Outros Exames
    histopatologia = models.IntegerField(
        verbose_name="Histopatologia",
        null=True,
        blank=True,
        choices=[
            [i + 1, x]
            for i, x in enumerate(
                ["Compatível", "Incompatível", "Inconclusivo", "Não realizado"]
            )
        ],
        pick=True,
    )
    imunohistoquimica = models.IntegerField(
        verbose_name="Imunohistoquímica",
        null=True,
        blank=True,
        choices=[
            [i + 1, x]
            for i, x in enumerate(
                ["Positivo", "Negativo", "Inconclusivo", "Não Realizado"]
            )
        ],
        pick=True,
    )

    # Vacinação
    vacinado = models.BooleanField(verbose_name="Vacinado (1ª Dose)", null=True)
    vacinado2 = models.BooleanField(verbose_name="Vacinado (2ª Dose)", null=True)
    data_ultima_vacina = models.DateField(
        verbose_name="Data da Última Vacinação", null=True, blank=True
    )

    # Hospitalização
    hospitalizacao = models.BooleanField(
        verbose_name="Ocorreu Hospitalização", null=True
    )
    data_hospitalizacao = models.DateField(
        verbose_name="Data da Hospitalização", null=True, blank=True
    )
    hospital = models.ForeignKey(
        Hospital,
        verbose_name="Hospital",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # Conclusão
    autoctone = models.BooleanField(
        verbose_name="O caso é autóctone do município de residência?", null=True
    )
    pais_infeccao = models.ForeignKey(
        Pais,
        verbose_name="País da Infecção",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="s2",
    )
    municipio_infeccao = models.ForeignKey(
        Municipio,
        verbose_name="Município da Infecção",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="s3",
    )
    distrito_infeccao = models.CharField(
        verbose_name="Distrito da Infecção", null=True, blank=True
    )
    bairro_infeccao = models.CharField(
        verbose_name="Bairro da Infecção", null=True, blank=True
    )
    classificacao_infeccao = models.ForeignKey(
        ClassificacaoInfeccao,
        verbose_name="Classificação da Infecção",
        on_delete=models.CASCADE,
        null=True,
        pick=True,
    )
    criterio_confirmacao = models.ForeignKey(
        CriterioConfirmacao,
        verbose_name="Critério de Confirmação/Descarte",
        on_delete=models.CASCADE,
        null=True,
        pick=True,
    )
    apresentacao_clinica = models.ForeignKey(
        ApresentacaoClinica,
        verbose_name="Apresentação Clínica",
        on_delete=models.CASCADE,
        null=True,
        pick=True,
    )
    evolucao_caso = models.ForeignKey(
        TipoEvolucao,
        verbose_name="Evolução do Caso",
        on_delete=models.CASCADE,
        null=True,
        pick=True,
    )
    data_obito = models.DateField(verbose_name="Data do Óbito", null=True, blank=True)
    data_encerramento = models.DateField(
        verbose_name="Data do Encerramento", null=True, blank=True
    )

    # Dados Clínicos - Sinais de Alarme
    dengue_com_sinais_de_alarme = models.BooleanField(
        verbose_name="Dengue com Sinais de Alarme", blank=True, null=True
    )
    sinais_alarme_dengue = models.ManyToManyField(
        SinalAlarme, verbose_name="Sinais de Alarme", blank=True, pick=True
    )
    data_inicio_sinais_alarme = models.DateField(
        verbose_name="Data de Início dos Sinais de Alarme", blank=True, null=True
    )

    # Dados Clínicos - Sinais de Alarme
    dengue_grave = models.BooleanField(
        verbose_name="Dengue Grave", blank=True, null=True
    )
    sinais_extravasamento_plasma = models.ManyToManyField(
        SinalExtravasamentoPlasma,
        verbose_name="Sinais de Extravasamento do Plasma",
        blank=True,
        pick=True,
    )
    sinais_sangramento_grave = models.ManyToManyField(
        SinalSangramentoGrave,
        verbose_name="Sinais de Sangramento Grave",
        blank=True,
        pick=True,
    )
    sinais_comprometimento_orgaos = models.ManyToManyField(
        SinalComprometimentoOrgao,
        verbose_name="Sinais de Comprometimento dos Órgãos",
        blank=True,
        pick=True,
    )
    outros_orgaos_afetados = models.CharField(
        verbose_name="Outros Órgãos", null=True, blank=True
    )
    data_inicio_sinais_graves = models.DateField(
        verbose_name="Data de Início dos Sinais de Gravidade", null=True, blank=True
    )

    # Observação
    observacao = models.TextField(verbose_name="Observação", null=True, blank=True)
    validada = models.BooleanField(verbose_name="Validada", null=True, blank=True)

    # Token
    token = models.CharField(verbose_name="Token", null=True, blank=True)

    objects = NotificacaoIndividualQuerySet()

    class Meta:
        icon = "person"
        verbose_name = "Notificação Individual"
        verbose_name_plural = "Notificações Individuais"

    def save(self, *args, **kwargs):
        if self.token is None:
            self.token = uuid1().hex
        if self.data_primeiros_sintomas:
            for name in [
                "data_investigacao",
                "data_primeira_amostra_chikungunya",
                "data_segunda_amostra_chikungunya",
                "data_coleta_exame_prnt",
                "data_amostra_dengue",
                "data_exame_ns1",
                "data_isolamento",
                "data_rt_pcr",
                "data_ultima_vacina",
                "data_hospitalizacao",
                "data_obito",
                "data_encerramento",
                "data_inicio_sinais_alarme",
                "data_inicio_sinais_graves",
                "data_primeiros_sintomas",
            ]:
                data = getattr(self, name)
                if data and data < self.data_primeiros_sintomas:
                    campo = getattr(type(self), name).field.verbose_name
                    raise ValidationError(
                        f'A data informada no campo "{campo}" não pode anteceder a data dos primeiros sintomas.'
                    )
        super().save(*args, **kwargs)

    @meta("Número")
    def get_numero(self):
        return str(self.id).rjust(5, "0")

    def get_idade(self):
        return age(self.data_nascimento)

    def formfactory(self):
        return (
            super()
            .formfactory()
            .fieldset(
                "Dados Gerais",
                (
                    "doenca",
                    "data",
                    ("notificante", "municipio"),
                    ("unidade", "data_primeiros_sintomas"),
                ),
            )
            .fieldset(
                "Dados do Indivíduo",
                (
                    ("cpf", "cartao_sus"),
                    "nome",
                    ("data_nascimento", "idade"),
                    "sexo",
                    "periodo_gestacao",
                    "raca",
                    "escolaridade",
                    "nome_mae",
                ),
            )
            .fieldset(
                "Dados Residenciais",
                (
                    "pais:pais.cadastrar",
                    ("cep", "municipio_residencia:municipio.cadastrar"),
                    ("distrito", "bairro"),
                    ("logradouro", "codigo_logradouro"),
                    ("numero_residencia", "complemento"),
                    "zona",
                    ("latitude", "longitude"),
                    "referencia",
                ),
            )
            .fieldset("Dados de Contato", (("telefone", "email"),))
            .fieldset("Investigação", ("data_investigacao", "ocupacao_investigacao"))
            .fieldset("Dados Clínicos", ("sinais_clinicos", "doencas_pre_existentes"))
            .fieldset(
                "Sorologia (IgM) Chikungunya",
                (
                    "data_primeira_amostra_chikungunya",
                    "resultado_primeira_amostra_chikungunya",
                    "data_segunda_amostra_chikungunya",
                    "resultado_segunda_amostra_chikungunya",
                ),
            )
            .fieldset(
                "Exame de Neutralização por Redução de Placas (PRNT)",
                ("data_coleta_exame_prnt", "resultado_exame_prnt"),
            )
            .fieldset(
                "Sorologia (IgM) Dengue",
                ("data_amostra_dengue", "resultado_amostra_dengue"),
            )
            .fieldset("Exame NS1", ("data_exame_ns1", "resultado_exame_ns1"))
            .fieldset("Outros Exames", ("histopatologia", "imunohistoquimica"))
            .fieldset("RT-PCR", ("data_rt_pcr", "resultado_rt_pcr", "sorotipo"))
            .fieldset("Isolamento", ("data_isolamento", "resultado_isolamento"))
            .fieldset("Vacinação", ("vacinado", "vacinado2", "data_ultima_vacina"))
            .fieldset(
                "Hospitalização", ("hospitalizacao", "data_hospitalizacao", "hospital")
            )
            .fieldset(
                "Conclusão",
                (
                    (
                        "pais_infeccao:pais.cadastrar",
                        "municipio_infeccao:municipio.cadastrar",
                    ),
                    ("distrito_infeccao", "bairro_infeccao"),
                    ("classificacao_infeccao", "criterio_confirmacao"),
                    ("apresentacao_clinica", "evolucao_caso"),
                    ("data_obito", "data_encerramento"),
                ),
            )
            .fieldset(
                "Dados Clínicos - Sinais de Alarme",
                (
                    "dengue_com_sinais_de_alarme",
                    "sinais_alarme_dengue",
                    "data_inicio_sinais_alarme",
                ),
            )
            .fieldset(
                "Dados Clínicos - Sinais de Gravidade",
                (
                    "dengue_grave",
                    "sinais_extravasamento_plasma",
                    "sinais_sangramento_grave",
                    "sinais_comprometimento_orgaos",
                    "outros_orgaos_afetados",
                    "data_inicio_sinais_graves",
                ),
            )
            .fieldset("Observação", ("observacao",))
        )

    def serializer(self):
        return (
            super()
            .serializer()
            .actions("notificacaoindividual.validar")
            .fieldset(
                "Dados Gerais",
                (
                    "doenca",
                    "data",
                    ("notificante", "municipio"),
                    ("unidade", "data_primeiros_sintomas"),
                ),
            )
            .fieldset(
                "Dados do Indivíduo",
                (
                    ("cpf", "cartao_sus"),
                    "nome",
                    ("data_nascimento", "idade"),
                    "sexo",
                    "periodo_gestacao",
                    "raca",
                    "escolaridade",
                    "nome_mae",
                ),
            )
            .fieldset(
                "Dados Residenciais",
                (
                    "pais",
                    ("cep", "municipio_residencia"),
                    ("distrito", "bairro"),
                    ("logradouro", "codigo_logradouro"),
                    ("numero_residencia", "complemento"),
                    "zona",
                    ("latitude", "longitude"),
                    "referencia",
                ),
            )
            .fieldset("Dados de Contato", (("telefone", "email"),))
            .fieldset("Investigação", ("data_investigacao", "ocupacao_investigacao"))
            .fieldset("Dados Clínicos", ("sinais_clinicos", "doencas_pre_existentes"))
            .fieldset(
                "Sorologia (IgM) Chikungunya",
                (
                    "data_primeira_amostra_chikungunya",
                    "resultado_primeira_amostra_chikungunya",
                    "data_segunda_amostra_chikungunya",
                    "resultado_segunda_amostra_chikungunya",
                ),
            )
            .fieldset(
                "Exame de Neutralização por Redução de Placas (PRNT)",
                ("data_coleta_exame_prnt", "resultado_exame_prnt"),
            )
            .fieldset(
                "Sorologia (IgM) Dengue",
                ("data_amostra_dengue", "resultado_amostra_dengue"),
            )
            .fieldset("Exame NS1", ("data_exame_ns1", "resultado_exame_ns1"))
            .fieldset("Outros Exames", ("histopatologia", "imunohistoquimica"))
            .fieldset("Isolamento", ("data_isolamento", "resultado_isolamento"))
            .fieldset("RT-PCR", ("data_rt_pcr", "resultado_rt_pcr", "sorotipo"))
            .fieldset("Vacinação", ("vacinado", "vacinado2", "data_ultima_vacina"))
            .fieldset(
                "Hospitalização", ("hospitalizacao", "data_hospitalizacao", "hospital")
            )
            .fieldset(
                "Conclusão",
                (
                    ("pais_infeccao", "municipio_infeccao"),
                    ("distrito_infeccao", "bairro_infeccao"),
                    ("classificacao_infeccao", "criterio_confirmacao"),
                    ("apresentacao_clinica", "evolucao_caso"),
                    ("data_obito", "data_encerramento"),
                ),
            )
            .fieldset(
                "Dados Clínicos - Sinais de Alarme",
                (
                    "dengue_com_sinais_de_alarme",
                    "sinais_alarme_dengue",
                    "data_inicio_sinais_alarme",
                ),
            )
            .fieldset(
                "Dados Clínicos - Sinais de Gravidade",
                (
                    "dengue_grave",
                    "sinais_extravasamento_plasma",
                    "sinais_sangramento_grave",
                    "sinais_comprometimento_orgaos",
                    "outros_orgaos_afetados",
                    "data_inicio_sinais_graves",
                ),
            )
            .fieldset("Outras Informações", ("observacao", "validada"))
        )

    def __str__(self):
        return f"Notificação {self.get_numero()} - {self.unidade} ({self.data_primeiros_sintomas.strftime('%d/%m/%Y')})"

    def get_url_impressao(self):
        return f"{settings.SITE_URL}/api/notificacaoindividual/imprimir/{self.id}/?token={self.token}"

    def generate_qr_code_base64(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.get_url_impressao())
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(
            buffered, format="PNG"
        )  # You can choose other formats like JPEG if desired
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"  # Include data URI prefix


class NotificacaoSurto(models.Model):
    data_primeiros_sintomas = models.DateField(
        verbose_name="Data dos 1º Sintomas do 1º Caso Suspeito"
    )
    numero_casos_suspeitos = models.CharField(
        verbose_name="Número de Casos Suspeitos/Expostos"
    )
    tipo_local = models.ForeignKey(
        TipoLocal,
        verbose_name="Local Inicial da Ocorrência",
        on_delete=models.CASCADE,
        pick=True,
    )
    hipotese_diagnostica_1 = models.ForeignKey(
        Doenca,
        verbose_name="1ª Hipótese Diagnóstica",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="s1",
    )
    hipotese_diagnostica_2 = models.ForeignKey(
        Doenca,
        verbose_name="1ª Hipótese Diagnóstica",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="s2",
    )

    class Meta:
        icon = "people-line"
        verbose_name = "Notificação de Surto"
        verbose_name_plural = "Notificações de Surto"

    def __str__(self):
        return f"Notificação {self.id}"
