from slth.db import models, role, meta
import os
import json
from django.conf import settings
from slth.components import GeoMap, FileLink, TemplateContent
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from slth.utils import age
import qrcode
import base64
from io import BytesIO
from uuid import uuid1
from datetime import datetime, timedelta
from django.db import transaction
from slth.models import Email
from slth.components import Badge



class TermoUso(models.Model):
    user = models.ForeignKey(User, verbose_name='Usuário', on_delete=models.CASCADE)
    aceito = models.BooleanField(verbose_name='Aceito', help_text="Concordo e aceito com os termos acima descritos.", null=True)
    data_assinatura = models.DateTimeField(verbose_name='Data da Assinatura', null=True, blank=True)

    class Meta:
        verbose_name = 'Termo de Uso'
        verbose_name_plural = 'Termos de Uso'

    def __str__(self):
        return f'Termo de Uso de {self.user}'

    @meta(None)
    def get_termo_consentimento_digital(self):
        return TemplateContent('termouso.html', dict(atendimento=self))


@role("administrador", username="cpf", email="email")
class Administrador(models.Model):
    cpf = models.CharField(verbose_name="CPF", blank=False)
    nome = models.CharField(verbose_name="Nome")
    email = models.CharField(verbose_name="E-mail", null=True)

    class Meta:
        verbose_name = "Administrador"
        verbose_name_plural = "Administradores"

    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        User.objects.filter(username=self.cpf).update(first_name=self.nome.split()[0])


class AgenteQuerySet(models.QuerySet):
    def all(self):
        return super().all().search('cpf', 'nome').fields(
            "cpf", "nome", "email", "get_municipio"
        ).lookup('gm', municipio__gestores__cpf='username')


class Agente(models.Model):
    cpf = models.CharField(verbose_name="CPF", blank=False)
    nome = models.CharField(verbose_name="Nome")
    email = models.CharField(verbose_name="E-mail", null=True)

    objects = AgenteQuerySet()

    class Meta:
        icon = 'person-shelter'
        verbose_name = "Agente de Endemias"
        verbose_name_plural = "Agentes de Endemias"

    def __str__(self):
        return f'{self.nome} ({self.cpf})'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        User.objects.filter(username=self.cpf).update(first_name=self.nome.split()[0])

    @meta("Município")
    def get_municipio(self):
        return ", ".join(self.municipio_set.values_list("nome", flat=True))


class Supervisor(models.Model):
    cpf = models.CharField(verbose_name="CPF", blank=False)
    nome = models.CharField(verbose_name="Nome")
    email = models.CharField(verbose_name="E-mail", null=True)

    objects = AgenteQuerySet()

    class Meta:
        icon = 'person'
        verbose_name = "Supervisor de Endemia"
        verbose_name_plural = "Supervisores de Endemia"

    def __str__(self):
        return f'{self.nome} ({self.cpf})'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        User.objects.filter(username=self.cpf).update(first_name=self.nome.split()[0])

    @meta("Município")
    def get_municipio(self):
        return ", ".join(self.municipio_set.values_list("nome", flat=True))


class Funcao(models.Model):
    nome = models.CharField(verbose_name="Nome")

    class Meta:
        verbose_name = "Função"
        verbose_name_plural = "Funções"

    def __str__(self):
        return self.nome


class NotificanteQuerySet(models.QuerySet):
    def all(self):
        return super().all().search('cpf', 'nome').fields("cpf", "nome", "email", "funcao", "get_equipes")


class Notificante(models.Model):
    cpf = models.CharField(verbose_name="CPF", blank=False)
    nome = models.CharField(verbose_name="Nome")
    email = models.CharField(verbose_name="E-mail", null=True)
    funcao = models.ForeignKey(Funcao, verbose_name="Função", on_delete=models.CASCADE)

    objects = NotificanteQuerySet()

    class Meta:
        verbose_name = "Notificante"
        verbose_name_plural = "Notificantes"

    def __str__(self):
        return f'{self.nome} ({self.cpf})'

    @meta("Equipe")
    def get_equipes(self):
        return ", ".join(self.equipe_set.values_list("nome", flat=True))
    
    def serializer(self):
        return super().serializer().fieldset("", (("cpf",  "nome"), "email",  "funcao"))
    
    def formfactory(self):
        return super().formfactory().fieldset("", (("cpf",  "nome"), "email",  "funcao"))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        User.objects.filter(username=self.cpf).update(first_name=self.nome.split()[0])
    


class GestorUnidadeQuerySet(models.QuerySet):
    def all(self):
        return super().all().search('cpf', 'nome').fields("cpf", "nome", "get_unidade")


class GestorUnidade(models.Model):
    cpf = models.CharField(verbose_name="CPF", blank=False)
    nome = models.CharField(verbose_name="Nome")
    email = models.CharField(verbose_name="E-mail", null=True)

    objects = GestorUnidadeQuerySet()

    class Meta:
        verbose_name = "Gestor de Unidade"
        verbose_name_plural = "Gestores de Unidade"

    def __str__(self):
        return f'{self.nome} ({self.cpf})'

    @meta("Unidade")
    def get_unidade(self):
        return ", ".join(self.unidadesaude_set.values_list("nome", flat=True))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        User.objects.filter(username=self.cpf).update(first_name=self.nome.split()[0])
    

class GestorMunicipalQuerySet(models.QuerySet):
    def all(self):
        return super().all().search('cpf', 'nome').fields("cpf", "nome", "get_municipio")


class GestorMunicipal(models.Model):
    cpf = models.CharField(verbose_name="CPF", blank=False)
    nome = models.CharField(verbose_name="Nome")
    email = models.CharField(verbose_name="E-mail", null=True)

    objects = GestorMunicipalQuerySet()

    class Meta:
        verbose_name = "Gestor de Municipal"
        verbose_name_plural = "Gestores Municipais"

    def __str__(self):
        return f'{self.nome} ({self.cpf})'

    @meta("Município")
    def get_municipio(self):
        return ", ".join(self.municipio_set.values_list("nome", flat=True))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        User.objects.filter(username=self.cpf).update(first_name=self.nome.split()[0])


class ReguladorQuerySet(models.QuerySet):
    def all(self):
        return super().all().search('cpf', 'nome').fields("cpf", "nome", "get_municipio")


class Regulador(models.Model):
    cpf = models.CharField(verbose_name="CPF", blank=False)
    nome = models.CharField(verbose_name="Nome")
    email = models.CharField(verbose_name="E-mail", null=True)

    objects = ReguladorQuerySet()

    class Meta:
        verbose_name = "Regulador"
        verbose_name_plural = "Reguladores"

    def __str__(self):
        return f'{self.nome} ({self.cpf})'

    @meta("Município")
    def get_municipio(self):
        return ", ".join(self.municipio_set.values_list("nome", flat=True))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        User.objects.filter(username=self.cpf).update(first_name=self.nome.split()[0])


class MotivoPerdaPrazoBloqueio(models.Model):
    nome = models.CharField(verbose_name='Nome')

    class Meta:
        verbose_name = 'Motivo de Perda de Prazo de Bloqueio'
        verbose_name_plural = 'Motivos de Perda de Prazo de Bloqueio'


    def __str__(self):
        return self.nome


class ChamadoQuerySet(models.QuerySet):
    def all(self):
        return self.filters('classificacao', 'atendido', 'resolvido')


class Chamado(models.Model):
    usuario = models.ForeignKey(User, verbose_name='', on_delete=models.CASCADE)
    data_abertura = models.DateTimeField(verbose_name='Data da Abertura', auto_created=True)
    descricao = models.TextField(verbose_name='Descrição', help_text='Descrição da solicitação ou problema')
    classificacao = models.CharField(verbose_name='Classificação', choices=[['', 'Não-classificado'], ['tecnico', 'Técnico'], ['negocio', 'Negócio']], null=True, blank=True)
    atendente = models.ForeignKey(User, verbose_name='Atendente', on_delete=models.CASCADE, null=True, blank=True, related_name='r1')
    data_atendimento = models.DateTimeField(verbose_name='Data do Atendimento', null=True)
    atendido = models.BooleanField(verbose_name="Atendido", null=True, blank=True)
    resolvido = models.BooleanField(verbose_name="Resolvido", null=True, blank=True)
    observacao = models.TextField(verbose_name='Observação', null=True, blank=True)
    
    class Meta:
        icon = "concierge-bell"
        verbose_name = 'Chamado'
        verbose_name_plural = 'Chamados'

    objects = ChamadoQuerySet()

    def __str__(self):
        return f'Chamado {self.id}'
    
    def save(self, *args, **kwargs):
        if self.data_abertura is None:
            self.data_abertura = datetime.now()
        if self.data_atendimento and self.atendido is None:
            self.atendido = True
        if self.resolvido is not None and self.data_atendimento is None:
            self.data_atendimento = datetime.now()
        super().save(*args, **kwargs)
    
    def formfactory(self):
        return super().formfactory().fields('usuario', 'descricao')
    
    def serializer(self):
        return super().serializer().fieldset(
            'Dados Gerais', fields=(('usuario', 'data_abertura'), 'descricao'),
        ).fieldset(
            'Dados do Atendimento', fields=(('classificacao', 'atendente'), ('data_atendimento', 'resolvido'), 'observacao'),
        )


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

class MunicipioQuerySet(models.QuerySet):
    def all(self):
        return (
            self.fields("estado",  "nome", "gestores", "reguladores", "supervisores").search("nome", "gestores__nome").filters("estado").lookup("administrador")
            .lookup("notificante", unidadesaude__equipe__notificantes__cpf="username")
            .lookup("gm", gestores__cpf="username")
            .lookup("supervisor", supervisores__cpf="username")
        )


@role("gm", username="gestores__cpf", email="gestores__email", municipio="pk")
@role("regulador", username="reguladores__cpf", email="reguladores__email", municipio="pk")
@role("agente", username="agentes__cpf", email="agentes__email", municipio="pk")
@role("supervisor", username="supervisores__cpf", email="supervisores__email", municipio="pk")
class Municipio(models.Model):
    estado = models.ForeignKey(Estado, verbose_name="Estado", on_delete=models.CASCADE)
    codigo = models.CharField(max_length=7, verbose_name="Código IBGE", unique=True)
    nome = models.CharField(verbose_name="Nome", max_length=60)
    gestores = models.ManyToManyField(GestorMunicipal, blank=True)
    reguladores = models.ManyToManyField(Regulador, blank=True)
    agentes = models.ManyToManyField(Agente, verbose_name="Agentes de Endemia", blank=True)
    supervisores = models.ManyToManyField(Supervisor, verbose_name="Supervisores de Endemia", blank=True)

    objects = MunicipioQuerySet()

    class Meta:
        icon = "map-marked"
        verbose_name = "Município"
        verbose_name_plural = "Municípios"

    def __str__(self):
        return "%s/%s" % (self.nome, self.estado.sigla)

    def serializer(self):
        return (
            super()
            .serializer().actions('municipio.adicionaragente', "municipio.editar")
            .fieldset("Dados Gerais", (("codigo", "nome"), "estado"))
            .fieldset("Gestão", ("gestores", "reguladores", "supervisores"))
            .queryset('get_agentes')
        )

    def formfactory(self):
        return (
            super()
            .formfactory()
            .fieldset("Dados Gerais", (("codigo", "nome"), "estado"))
            .fieldset(
                "Gestão",
                (
                    "gestores:gestormunicipal.cadastrar",
                    "reguladores:regulador.cadastrar",
                    "supervisores:supervisor.cadastrar",
                ),
            )
        )
    
    def get_agentes(self):
        return self.agentes.search('cpf', 'nome').fields(
            "cpf", "nome", "email"
        ).actions('agente.desvincular')


class UnidadeSaudeQuerySet(models.QuerySet):
    def all(self):
        return (
            self.search("nome").filters("municipio")
            .lookup("gm", municipio__gestores__cpf="username")
            .lookup("administrador")
            .lookup("regulador", municipio__reguladores__cpf="username")
            .lookup("gu", gestores__cpf="username")
            .lookup("notificante", equipe__notificantes__cpf="username")
        )


@role("gu", username="gestores__cpf", email="gestores__email", unidade="pk")
class UnidadeSaude(models.Model):
    codigo = models.CharField(verbose_name="CNES")
    nome = models.CharField(verbose_name="Nome")

    municipio = models.ForeignKey(
        Municipio, verbose_name="Município", on_delete=models.CASCADE
    )
    gestores = models.ManyToManyField(GestorUnidade, blank=True)

    objects = UnidadeSaudeQuerySet()

    class Meta:
        icon = "building"
        verbose_name = "Unidade de Saúde"
        verbose_name_plural = "Unidades de Saúde"

    def __str__(self):
        return f'{self.codigo} - {self.nome}'

    def serializer(self):
        return (
            super()
            .serializer().actions('unidadesaude.editar', 'unidadesaude.addequipe')
            .fieldset("Dados Gerais", (("codigo", "nome"), "municipio", "gestores"))
            .queryset("get_equipes")
        )

    def formfactory(self):
        return (
            super()
            .formfactory()
            .fieldset("Dados Gerais", (("codigo", "nome"), "municipio", "gestores:gestorunidade.cadastrar"))
        )

    def get_equipes(self):
        return self.equipe_set.all().ignore('unidade').actions('equipe.editar', 'equipe.excluir')


class EquipeQuerySet(models.QuerySet):
    def all(self):
        return (
            self.lookup("administrador")
            .lookup("gm", unidade__municipio__gestores__cpf="username")
            .lookup("gu", unidade__gestores__cpf="username")
        )


@role("notificante", username="notificantes__cpf", email="notificantes__email", unidade="pk")
class Equipe(models.Model):
    unidade = models.ForeignKey(UnidadeSaude, verbose_name='Unidade de Saúde', on_delete=models.CASCADE)
    codigo = models.CharField(verbose_name='INE', null=True, blank=True)
    nome = models.CharField(verbose_name='Nome')
    notificantes = models.ManyToManyField(Notificante, blank=True)

    objects = EquipeQuerySet()

    class Meta:
        verbose_name = 'Equipe'
        verbose_name_plural = 'Equipes'

    def __str__(self):
        return f'{self.nome} / {self.unidade}'
    
    def serializer(self):
        return (
            super()
            .serializer()
            .fieldset("Dados Gerais", (("nome", "codigo"),))
            .queryset("notificantes")
        )
    
    def formfactory(self):
        return (
            super()
            .formfactory()
            .fieldset("Dados Gerais", (("nome", "codigo"), "notificantes:notificante.cadastrar"))
        )


class SolicitacaoCadastroQuerySet(models.QuerySet):
    def all(self):
        return (
            self.search('cpf', 'nome').filters('papel', 'aprovada')
            .fields('data', 'cpf', 'nome', 'papel', 'municipio', 'unidade', 'aprovada', 'avaliador', 'data_avaliacao', 'observacao')
            .lookup("administrador")
            .lookup("gm", municipio__gestores__cpf="username")
            .lookup("gu", unidade__gestores__cpf="username")
        )

class SolicitacaoCadastro(models.Model):
    PAPEIS = [
        ['gm', 'Gestor Municipal'],
        ['gu', 'Gestor de Unidade'],
        ['regulador', 'Regulador'],
        ['agente', 'Agente de Endemia'],
        ['notificante', 'Notificante'],
    ]

    objects = SolicitacaoCadastroQuerySet()

    cpf = models.CharField(verbose_name="CPF", blank=False)
    nome = models.CharField(verbose_name="Nome")
    email = models.CharField(verbose_name="E-mail")
    funcao = models.ForeignKey(Funcao, verbose_name="Profissão/Função", on_delete=models.CASCADE)
    papel = models.CharField(verbose_name="Papel", null=True, choices=PAPEIS, pick=True)
    municipio = models.ForeignKey(Municipio, verbose_name="Município", null=True)
    unidade = models.ForeignKey(UnidadeSaude, verbose_name="Unidade", null=True, blank=True, help_text="Obrigatório apenas para notificante.")
    equipe = models.ForeignKey(Equipe, verbose_name="Equipe", null=True, blank=True)

    aprovada = models.BooleanField(verbose_name="Aprovada", null=True, choices=[['', ''], [False, 'Não'], [True, 'Sim']])
    data = models.DateTimeField(
        verbose_name="Data da Solicitação", auto_created=True, null=True
    )
    avaliador = models.ForeignKey(User, verbose_name='Avaliador', on_delete=models.CASCADE, null=True, blank=True)
    data_avaliacao = models.DateTimeField(
        verbose_name="Data da Avaliação", null=True
    )
    observacao = models.TextField(verbose_name="Observação", null=True, blank=True)

    class Meta:
        icon = "user-plus"
        verbose_name = "Solicitação de Cadastro"
        verbose_name_plural = "Solicitações de Cadastro"

    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        if self.papel == 'notificante' and not self.unidade:
            raise ValidationError('Informe a unidade')
        if not self.data:
            self.data = datetime.now()
        super().save(*args, **kwargs)

    def formfactory(self):
        return (
            super()
            .formfactory()
            .fieldset(
                "Dados Gerais", (("cpf", "nome"), ("email", "funcao")),
            ).fieldset(
                "Atuação", ("papel", "municipio", "unidade"),
            )
            .info("Você receberá um e-mail assim que sua solicitação for avaliada.")
        )
    
    def serializer(self):
        return (
            super()
            .serializer()
            .actions("solicitacaocadastro.avaliar")
            .fieldset(
                "Dados Gerais", (("cpf", "nome"), ("email", "funcao")),
            ).fieldset(
                "Atuação", ("papel", "municipio", "unidade"),
            ).fieldset(
                "Avaliação", (("aprovada", "avaliador", "data_avaliacao"), "observacao"),
            )
        )

    @transaction.atomic
    def processar(self):
        model = {'gm': GestorMunicipal, 'gu': GestorUnidade, 'notificante': Notificante, 'agente': Agente, 'regulador': Regulador}[self.papel]
        obj = (
            model.objects.filter(cpf=self.cpf).first() or model()
        )
        obj.cpf = self.cpf
        obj.nome = self.nome
        obj.email = self.email
        obj.funcao = self.funcao
        obj.save()
        if self.aprovada:
            if self.papel == 'notificante':
                if self.equipe is None:
                    raise ValidationError('Informe a equipe do notificante.')
                self.equipe.notificantes.add(obj)
                self.equipe.post_save()
            elif self.papel == 'gu':
                if self.unidade is None:
                    raise ValidationError('Informe a unidade do gestor.')
                self.unidade.gestores.add(obj)
                self.unidade.post_save()
            elif self.papel == 'agente':
                self.municipio.agentes.add(obj)
                self.municipio.post_save()
            elif self.papel == 'gm':
                if self.municipio is None:
                    raise ValidationError('Informe o município do gestor.')
                self.municipio.gestores.add(obj)
                self.municipio.post_save()
            elif self.papel == 'regulador':
                if self.municipio is None:
                    raise ValidationError('Informe o município do regulador.')
                self.municipio.reguladores.add(obj)
                self.municipio.post_save()
            password = None
            user = User.objects.filter(username=self.cpf).first()
            if not user.last_login:
                password = '123' if settings.DEBUG else uuid1().hex[0:6]
                user.set_password(password)
                user.save()
            content = 'A sua solicitação de acesso ao Arbonotifica foi aprovada.'
            if password:
                content = f'{content}\nA sua senha é "{password}" e você poderá alterá-la após acessar o sistema.'
            email = Email(to=obj.email, subject="Arbonotifica - Autorização de Acesso", content=content, action="Acessar", url=settings.SITE_URL)
            email.send()
        else:
            if self.observacao:
                content = f'Sua solicitação de acesso ao Arbonotifica foi negada com a seguinte obervação: {self.observacao}'
            else:
                content = f'Sua solicitação de acesso ao Arbonotifica foi negada'
            email = Email(to=obj.email, subject="Arbonotifica - Autorização de Acesso", content=content)
            email.send()


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
    positivo = models.BooleanField(verbose_name='Positivo', default=False)

    class Meta:
        verbose_name = "Classificação de Infecção"
        verbose_name_plural = "Classificações de Infecção"

    def __str__(self):
        return self.nome


class CriterioConfirmacao(models.Model):
    EM_INVESTIGACAO = 3

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
    EM_INVESTIGACAO = 5

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
        icon = "hospital-symbol"
        verbose_name = "Hospital"
        verbose_name_plural = "Hospitais"

    def __str__(self):
        return self.nome


class NotificacaoIndividualQuerySet(models.QuerySet):
    def all(self):
        return (
            self.search("cpf", "nome", "cartao_sus", "numero")
            .fields("numero", "notificante", "data", "cpf", "nome", "data_primeiros_sintomas", "data_envio", "validada", "get_status", "get_resultado_exame")
            .filters("doenca", "municipio", "unidade", "notificante", "status", "validada",)
            .lookup("administrador")
            .lookup("gm", unidade__municipio__gestores__cpf='username')
            .lookup("regulador", unidade__municipio__reguladores__cpf='username')
            .lookup("gu", unidade__gestores__cpf='username')
            .lookup("supervisor", unidade__municipio__supervisores__cpf='username')
            .lookup("agente", unidade__municipio__agentes__cpf='username')
            .lookup("notificante", unidade__equipe__notificantes__cpf='username')
        ).distinct()
    
    def aguardando_envio(self):
        return (
            self.all()
            .filter(data_envio__isnull=True).exclude(devolvida=True)
            .filter(notificante__cpf=self.request.user.username)
            .actions(
                "notificacaoindividual.visualizar", "notificacaoindividual.imprimir"
            )
        )
    
    def bloqueios(self):
        return self.all().filters("doenca", "municipio", "unidade", "notificante", "status", "validada").filter(validada=True).fields(
            'id', 'numero', 'data', 'data_primeiros_sintomas',
            'get_qtd_dias_infectado', 'nome', 'get_endereco',
            'unidade', 'responsavel_bloqueio', 'get_status', 'get_bloqueio', 'data_bloqueio'
        ).actions('notificacaoindividual.atribuirbloqueio', 'notificacaoindividual.registrarbloqueio', 'notificacaoindividual.justificarperdaprazobloqueio').xlsx(
            'numero', 'data', 'data_primeiros_sintomas',
            'get_qtd_dias_infectado_exportacao', 'nome', 'get_endereco',
            'unidade', 'status', 'responsavel_bloqueio', 'bloqueio', 'data_bloqueio', 'tipo_bloqueio'
        )
    
    def em_periodo_bloqueio(self):
        sete_dias_atras = datetime.today().date() - timedelta(days=7)
        return self.bloqueios().filter(data_primeiros_sintomas__gte=sete_dias_atras)
    
    def aguardando_justificativa_perda_prazo(self):
        sete_dias_atras = datetime.today().date() - timedelta(days=7)
        return self.bloqueios().filter(data_primeiros_sintomas__lt=sete_dias_atras, motivo_perda_prazo_bloqueio__isnull=True)
    
    def aguardando_responsavel_bloqueio(self):
        return self.em_periodo_bloqueio().filter(responsavel_bloqueio__isnull=True)
    
    def aguardando_bloqueio(self):
        return self.em_periodo_bloqueio().filter(responsavel_bloqueio__isnull=False, bloqueio__isnull=True)

    def aguardando_validacao(self):
        return (
            self.all()
            .filter(validada__isnull=True, data_envio__isnull=False).exclude(devolucao__isnull=False, devolucao__observacao_correcao__isnull=True)
            .actions("notificacaoindividual.visualizar", "notificacaoindividual.imprimir")
        )
    
    def aguardando_correcao(self):
        return (
            self.all()
            .filter(devolucao__isnull=False, devolucao__observacao_correcao__isnull=True)
            .actions("notificacaoindividual.visualizar", "notificacaoindividual.imprimir")
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
    
    @meta("Total por Bairro")
    def get_total_por_bairro(self):
        return self.counter("bairro")
    

    @meta("Dourados/MS")
    def get_mapa(self):
        map = GeoMap(
            -54.815434332605591,
            -22.251316151125515,
            zoom=13,
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
                    descricao = f"Notificação {notificacao.numero} - {notificacao.nome} ({notificacao.cpf or notificacao.cartao_sus}) - {notificacao.data_primeiros_sintomas.strftime('%d/%m/%Y')}. Endereço: {notificacao.get_endereco()}"
                    map.add_point(
                        notificacao.longitude, notificacao.latitude, descricao
                    )
            return map


class NotificacaoIndividual(models.Model):
    # Dados Gerais
    numero = models.CharField(verbose_name='Número', max_length=10, null=True, db_index=True)
    doenca = models.ForeignKey(
        Doenca, verbose_name="Doença", on_delete=models.CASCADE, pick=True
    )
    data = models.DateField(verbose_name="Data do Cadastro")
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
    cpf = models.CharField(verbose_name="CPF", null=True, blank=True)
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

    # Surto
    data_primeiros_sintomas_surto = models.DateField(
        verbose_name="Data dos 1º Sintomas do 1º Caso Suspeito",
        null=True,
        blank=True,
    )
    numero_casos_suspeitos_surto = models.CharField(
        verbose_name="Número de Casos Suspeitos/Expostos",
        null=True,
        blank=True,
    )
    tipo_local_surto = models.ForeignKey(
        TipoLocal,
        verbose_name="Local Inicial da Ocorrência",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        pick=True,
    )

    # Dados Residenciais
    endereco = models.ForeignKey('api.Endereco', verbose_name='Endereço Pré-cadastrado', on_delete=models.CASCADE, null=True, blank=True)
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
        blank=True,
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
        blank=True,
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
    resultado_exame = models.FileField(verbose_name='Resultado do Exame', upload_to='resultados_exames', null=True, blank=True)

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
    validada = models.BooleanField(verbose_name="Validada", null=True, blank=True, choices=[['', 'Pendente de Avaliação'], [False, 'Não'], [True, 'Sim']])

    # Bloqueio
    bloqueio = models.BooleanField(verbose_name='Bloqueio', null=True, blank=False, choices=[['', ''], [False, 'Não'], [True, 'Sim']])
    tipo_bloqueio = models.CharField(verbose_name='Tipo de Bloqueio', choices=[['Mecânico', 'Mecânico'], ['Químico', 'Químico'], ['Mecânico e Químico', 'Mecânico e Químico']], null=True, blank=True, pick=True)
    responsavel_bloqueio = models.ForeignKey(Agente, verbose_name='Responsável pelo Bloqueio', on_delete=models.CASCADE, null=True)
    data_bloqueio = models.DateTimeField(verbose_name='Data do Bloqueio', null=True, blank=True)
    motivo_perda_prazo_bloqueio = models.ForeignKey(MotivoPerdaPrazoBloqueio, verbose_name='Motivo da Perda de Prazo', on_delete=models.CASCADE, null=True, blank=False, pick=True)
    observacao_bloqueio = models.TextField(verbose_name='Observação', help_text='Informe algo que considera relevante durante a realização do bloqueio', null=True, blank=True)

    # Token
    data_envio = models.DateField(verbose_name='Data do Envio', null=True, blank=True)
    devolvida = models.BooleanField(verbose_name='Devolvida', null=True)
    token = models.CharField(verbose_name="Token", null=True, blank=True)
    status = models.CharField(verbose_name="Status", default='Em Análise', choices=[['Em Análise', 'Em Análise'], ['Positivo', 'Positivo'], ['Negativo', 'Negativo']])

    objects = NotificacaoIndividualQuerySet()

    class Meta:
        icon = "person"
        verbose_name = "Notificação Individual"
        verbose_name_plural = "Notificações Individuais"

    @meta("Status")
    def get_status(self):
        if self.status == 'Positivo':
            return Badge('#4caf50', 'Positivo', 'check')
        elif self.status == 'Negativo':
            return Badge('red', 'Negativo', 'x')
        return Badge('#2196f3', 'Em Análise', 'eyedropper')
    
    @meta('Endereço')
    def get_endereco(self):
        endereco = [
            self.logradouro,
            self.numero_residencia,
            self.complemento,
            self.bairro,
            self.cep,
            self.distrito,
            self.municipio_residencia,
            f'Zona {self.zona}' if self.zona else None,
            ]
        return ', '.join(str(info) for info in endereco if info)

    @meta('Histórico de Evolução')
    def get_historico_evolucao(self):
        return self.evolucao_set.all().ignore('notificacao')
    
    @meta('Histórico de Devolução')
    def get_historico_devolucao(self):
        return self.devolucao_set.ignore('notificacao')
    
    @meta('Qtd. de Dias Infectado')
    def get_qtd_dias_infectado(self, apenas_numero=False):
        total = (datetime.today().date() - self.data_primeiros_sintomas).days
        if apenas_numero:
            return total
        return Badge('gray' if total > 7 else 'green', f'{total} dia' if total == 1 else f'{total} dias')
    
    @meta('Qtd. de Dias Infectado')
    def get_qtd_dias_infectado_exportacao(self, apenas_numero=False):
        return self.get_qtd_dias_infectado(True)

    def pode_registrar_bloqueio(self):
        return self.get_qtd_dias_infectado(apenas_numero=True) < 8

    def get_bloqueio(self):
        if self.bloqueio is None:
            return Badge('gray', 'Pendente') if self.pode_registrar_bloqueio() else Badge('red', 'Prazo Perdido', icon='user-check' if self.motivo_perda_prazo_bloqueio else 'question')
        elif not self.bloqueio:
            return Badge('red', 'Não')
        elif self.tipo_bloqueio == 'Mecânico':
            return Badge('#2196f3', 'Mecânico', 'house-circle-xmark')
        elif self.tipo_bloqueio == 'Químico':
            return Badge('#2196f3', 'Químico', 'skull-crossbones')
        elif self.tipo_bloqueio == 'Mecânico e Químico':
            return Badge('#2196f3', 'Mecânico/Químico')

    @transaction.atomic
    def clonar(self, doenca):
        m2m = [field for field in type(self)._meta.get_fields()  if isinstance(field, models.ManyToManyField)]
        objects = {}
        for field in m2m:
            objects[field.name] = list(getattr(self, field.name).values_list('pk', flat=True))
        self.pk = None
        prefix = self.numero.split('-')[0]
        tokens = NotificacaoIndividual.objects.filter(numero__startswith=prefix).order_by('numero').values_list('numero', flat=True).last().split('-')
        sequence = 1 if len(tokens) == 1 else int(tokens[-1]) + 1
        self.numero = '{}-{}'.format(self.numero.split('-')[0], sequence)
        self.doenca = doenca
        self.resultado_exame = None
        self.save()
        for name, pks in objects.items():
            getattr(self, name).set(pks)
        return self
    
    def save(self, *args, **kwargs):
        if self.data_encerramento and self.classificacao_infeccao:
            if self.classificacao_infeccao.positivo:
                self.status = 'Positivo'
            else:
                self.status = 'Negativo'
        else:
            self.status = 'Em Análise'
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
        if self.numero is None:
            self.numero = '{}'.format(str(self.id).rjust(5, "0"))
            super().save(*args, **kwargs)

    def get_idade(self):
        return age(self.data_nascimento)
    
    def pode_ser_enviada(self):
        return self.data_envio is None

    def enviar(self):
        self.data_envio = datetime.now()
        self.save()

    def pode_ser_devolvida(self):
        return self.validada is None and not self.devolvida
    
    def devolver(self, avaliador, motivo):
        self.devolvida = True
        self.save()
        self.devolucao_set.create(avaliador=avaliador, data=datetime.now(), motivo=motivo)
        
    def pode_ser_reenviada(self):
        return self.devolvida and self.devolucao_set.filter(observacao_correcao__isnull=True).exists()

    def reenviar(self, observacao):
        self.devolvida = False
        self.save()
        self.devolucao_set.filter(observacao_correcao__isnull=True).update(data_correcao=datetime.now(), observacao_correcao=observacao)

    def pode_ser_finalizada(self):
        return self.validada is None and not self.devolvida

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
                    "endereco",
                    "pais:pais.cadastrar",
                    ("cep", "bairro"),
                    ("municipio_residencia:notificacaoindividual.cadastrarmunicipio", "distrito"),
                    ("logradouro", "codigo_logradouro"),
                    ("numero_residencia", "complemento"),
                    "zona",
                    ("latitude", "longitude"),
                    "referencia",
                ),
            )
            .fieldset("Dados de Contato", (("telefone", "email"),))
            .fieldset("Investigação", (("data_investigacao", "ocupacao_investigacao:ocupacao.cadastrar"),))
            .fieldset(
                "Notificação de Surto",
                (
                    ("data_primeiros_sintomas_surto", "numero_casos_suspeitos_surto"),
                    "tipo_local_surto",
                ),
            )
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
                "Hospitalização", ("hospitalizacao", "data_hospitalizacao", "hospital:hospital.cadastrar")
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
                    ('resultado_exame',)
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
            .actions("notificacaoindividual.editar", "notificacaoindividual.imprimir", "notificacaoindividual.evoluircaso")
            .fieldset(
                "Dados Gerais",
                (
                    "numero",
                    ("doenca", "data"),
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
                    "endereco",
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
            .fieldset("Investigação", (("data_investigacao", "ocupacao_investigacao"),))
            .fieldset(
                "Notificação de Surto",
                (
                    ("data_primeiros_sintomas_surto", "numero_casos_suspeitos_surto"),
                    "tipo_local_surto",
                ),
            )
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
                    ("get_resultado_exame",)
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
            .fieldset("Dados do Bloqueio", (("bloqueio", "tipo_bloqueio"), ("responsavel_bloqueio", "data_bloqueio"), ("motivo_perda_prazo_bloqueio", "observacao_bloqueio")))
            .queryset("get_historico_evolucao")
            .queryset("get_registros_leitura_resultado")
            .fieldset("Outras Informações", ("observacao", ("data_envio", "validada")))
            .section('Dados do Envio da Ficha')
                .actions("notificacaoindividual.enviar", "notificacaoindividual.devolver", "notificacaoindividual.reenviar", "notificacaoindividual.finalizar")
                .queryset("get_historico_devolucao")
                .parent()
        )
    
    @meta('Histórico de Leitura do Resultado')
    def get_registros_leitura_resultado(self):
        return self.registroleituraresultado_set.all().fields('user', 'data')

    def __str__(self):
        return f"Notificação {self.numero} - {self.nome} ({self.cpf or self.cartao_sus}) - {self.data_primeiros_sintomas.strftime('%d/%m/%Y')}"

    def get_url_impressao(self):
        return f"{settings.SITE_URL}/api/notificacaoindividual/imprimir/{self.id}/?token={self.token}"

    @meta("Resultado do Exame")
    def get_resultado_exame(self):
        return FileLink(self.resultado_exame.url, modal=True, icon='file', callback=f'/api/notificacaoindividual/registrarleituraresultado/{self.pk}/') if self.resultado_exame else None

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

    def is_pendente_correcao(self):
        return self.devolucao_set.filter(observacao_correcao__isnull=True)


class RegistroLeituraResultado(models.Model):
    notificacao = models.ForeignKey(NotificacaoIndividual, verbose_name='Notificação', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='Usuário', on_delete=models.CASCADE)
    data = models.DateTimeField(verbose_name='Data/Hora')

    @meta('Usuário')
    def get_user(self):
        if self.user.first_name:
            return f'{self.user.first_name} ({self.user.username})'
        return self.user.username

class DevolucaoQuerySet(models.QuerySet):
    def all(self):
        return self


class Devolucao(models.Model):
    notificacao = models.ForeignKey(NotificacaoIndividual, verbose_name='Notificação', on_delete=models.CASCADE)
    avaliador = models.ForeignKey(User, verbose_name='Avaliador', on_delete=models.CASCADE)
    data = models.DateTimeField(verbose_name='Data')
    motivo = models.TextField(verbose_name='Motivo')
    data_correcao = models.DateTimeField(verbose_name='Data da Correção', null=True)
    observacao_correcao = models.TextField(verbose_name='Observação da Correção', null=True)

    class Meta:
        verbose_name = 'Devolução'
        verbose_name_plural = 'Devoluções'

    objects = DevolucaoQuerySet()

    def __str__(self):
        return f'Devolução {self.id}'

    def get_avaliador(self):
        if self.avaliador:
            if self.avaliador.first_name:
                return f'{self.avaliador.first_name} ({self.avaliador.username})'
            return self.avaliador.username


class EvolucaoQuerySet(models.QuerySet):
    def all(self):
        return self.fields('notificacao', 'notificante', 'get_unidade', 'data', 'observacao')


class Evolucao(models.Model):

    notificacao = models.ForeignKey(NotificacaoIndividual, verbose_name='Notificação', on_delete=models.CASCADE)
    notificante = models.ForeignKey(User, verbose_name='Notificante', on_delete=models.CASCADE)
    data = models.DateTimeField(verbose_name='Data', auto_created=True)
    observacao = models.TextField(verbose_name='Motivo')

    class Meta:
        verbose_name = 'Evolução'
        verbose_name_plural = 'Evoluções'

    objects = EvolucaoQuerySet()

    def __str__(self):
        return f'Evolução {self.id}'
    
    def get_notificante(self):
        if self.notificante:
            if self.notificante.first_name:
                return f'{self.notificante.first_name} ({self.notificante.username})'
            return self.notificante.username

    @meta('Unidade')
    def get_unidade(self):
        if self.notificante:
            equipe = Equipe.objects.filter(notificantes__cpf=self.notificante.username).first()
            if equipe:
                return equipe.unidade


class CategoriaVideo(models.Model):
    nome = models.CharField(verbose_name='Nome')

    class Meta:
        verbose_name = 'Categoria de Video'
        verbose_name_plural = 'Categorias de Video'

    def __str__(self):
        return self.nome


class Video(models.Model):
    titulo = models.CharField(verbose_name='Título')
    categoria = models.ForeignKey(CategoriaVideo, verbose_name='Categoria', on_delete=models.CASCADE)
    codigo = models.CharField(verbose_name='Código')
    descricao = models.TextField(verbose_name='Descrição')

    class Meta:
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'

    def __str__(self):
        return self.titulo
    
    def get_embed_url(self):
        return f'https://www.youtube.com/embed/{self.codigo}'


class EnderecoQuerySet(models.QuerySet):
    def all(self):
        return self.fields('local', 'get_endereco')


class Endereco(models.Model):
    local = models.CharField(verbose_name='Local')
    # Dados Residenciais
    pais = models.ForeignKey(
        Pais,
        verbose_name="País",
        on_delete=models.CASCADE,
        null=True,
    )
    cep = models.CharField(verbose_name="CEP", null=True, blank=True)
    municipio = models.ForeignKey(
        Municipio,
        verbose_name="Município da Residência",
        on_delete=models.CASCADE,
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
    numero = models.CharField(
        verbose_name="Número da Residência", null=True, blank=True
    )
    complemento = models.CharField(verbose_name="Complemento", null=True, blank=True)
    latitude = models.CharField(verbose_name="Latitude", null=True, blank=True)
    longitude = models.CharField(verbose_name="Longitude", null=True, blank=True)
    referencia = models.CharField(
        verbose_name="Ponto de Referência", null=True, blank=True
    )

    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

    objects = EnderecoQuerySet()

    def __str__(self):
        return self.get_endereco()

    def formfactory(self):
        return (
            super()
            .formfactory()
            .fieldset(
                "Dados Gerais",
                (
                    "local",
                ),
            )
            .fieldset(
                "Dados do Endereço",
                (
                    "pais:pais.cadastrar",
                    ("cep", "bairro"),
                    ("municipio", "distrito"),
                    ("logradouro", "codigo_logradouro"),
                    ("numero", "complemento"),
                    "zona",
                    ("latitude", "longitude"),
                    "referencia",
                ),
            )
        )
    
    def serializer(self):
        return (
            super()
            .serializer()
            .fieldset(
                "Dados Gerais",
                (
                    "local",
                ),
            )
            .fieldset(
                "Dados Residenciais",
                (
                    "pais:pais.cadastrar",
                    ("cep", "bairro"),
                    ("municipio", "distrito"),
                    ("logradouro", "codigo_logradouro"),
                    ("numero", "complemento"),
                    "zona",
                    ("latitude", "longitude"),
                    "referencia",
                ),
            )
        )

    @meta('Endereço')
    def get_endereco(self):
        endereco = [
            self.logradouro,
            self.numero,
            self.complemento,
            self.bairro,
            self.cep,
            self.distrito,
            self.municipio,
            f'Zona {self.zona}' if self.zona else None,
            ]
        return ', '.join(str(info) for info in endereco if info)
