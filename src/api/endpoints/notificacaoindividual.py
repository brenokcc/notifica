import requests
from slth import endpoints
from datetime import date, timedelta
from ..models import *
from ..utils import buscar_endereco
from slth.integrations.google import places
from slth.utils import age
from slth.components import FileViewer


class NotificacoesIndividuais(endpoints.ListEndpoint[NotificacaoIndividual]):
    class Meta:
        verbose_name = "Notificações Individuais"

    def get(self):
        return (
            super()
            .get()
            .actions(
                "notificacaoindividual.checar",
                "notificacaoindividual.visualizar",
                "notificacaoindividual.editar",
                "notificacaoindividual.excluir",
                "notificacaoindividual.imprimir",
            )
        )

    def check_permission(self):
        return self.check_role("notificante", "regulador", "administrador", "gu", "gm")


class AguardandoEnvio(endpoints.QuerySetEndpoint[NotificacaoIndividual]):
    class Meta:
        modal = False
        icon = "bell"
        verbose_name = "Notificações individuais aguardando envio"

    def get_queryset(self):
        return super().get_queryset().aguardando_envio()

    def check_permission(self):
        return self.check_role("notificante", "administrador") and self.get_queryset().exists()

class AguardandoCorrecao(endpoints.QuerySetEndpoint[NotificacaoIndividual]):
    class Meta:
        modal = False
        icon = "bell"
        verbose_name = "Notificações individuais aguardando correção"

    def get_queryset(self):
        queryset = super().get_queryset().aguardando_correcao()
        if self.check_role("regulador"):
            return queryset
        return queryset.filter(notificante__cpf=self.request.user.username)

    def check_permission(self):
        return self.check_role("notificante", "administrador", "regulador") and self.get_queryset().exists()


class AguardandoValidacao(endpoints.QuerySetEndpoint[NotificacaoIndividual]):
    class Meta:
        modal = False
        icon = "bell"
        verbose_name = "Notificações individuais aguardando validação"

    def get_queryset(self):
        return super().get_queryset().aguardando_validacao()

    def check_permission(self):
        return self.check_role("regulador", "administrador") and self.get_queryset().exists()



class Visualizar(endpoints.ViewEndpoint[NotificacaoIndividual]):
    class Meta:
        modal = False
        verbose_name = "Visualizar Notificação Individual"

    def get(self):
        serializer = super().get()
        motivo_correcao = self.instance.devolucao_set.filter(observacao_correcao__isnull=True).values_list('motivo', flat=True).first()
        if motivo_correcao: serializer.info(f"Aguardando correção: {motivo_correcao}")
        return serializer

    def check_permission(self):
        return self.check_role("notificante", "regulador", "administrador", "gu", "gm") and self.check_instance()


class Imprimir(endpoints.InstanceEndpoint[NotificacaoIndividual]):
    class Meta:
        icon = "file-pdf"
        modal = True
        verbose_name = "Imprimir Notificação Individual"

    def get(self):
        if self.request.GET.get("token"):
            return self.render(
                dict(obj=self.instance), self.instance.doenca.modelo_ficha, pdf=True
            )
        else:
            return FileViewer(
                self.get_api_url(self.instance.pk) + "?token=" + self.instance.token
            )

    def check_permission(self):
        return (
            (self.check_role("notificante", "regulador", "administrador", "gu", "gm") and self.check_instance() and self.instance.data_envio)
            or self.request.GET.get("token") == self.instance.token
        )


class Mixin:

    def clean_cpf(self, data):
        cpf = data.get('cpf')
        data_primeiros_sintomas = data['data_primeiros_sintomas']
        limite_inferior = data_primeiros_sintomas - timedelta(days=30)
        limite_superior= data_primeiros_sintomas + timedelta(days=30)
        anterior = NotificacaoIndividual.objects.filter(cpf=cpf, data_primeiros_sintomas__gte=limite_inferior, data_primeiros_sintomas__lte=data_primeiros_sintomas).exclude(pk=self.instance.pk).first()
        if anterior:
            raise ValidationError(f'Existe uma notificação anterior ({anterior.get_numero()}) realizada a menos de um mês para esse CPF.')
        posterior = NotificacaoIndividual.objects.filter(cpf=cpf, data_primeiros_sintomas__lte=limite_superior, data_primeiros_sintomas__gte=data_primeiros_sintomas).exclude(pk=self.instance.pk).first()
        if posterior:
            print(data_primeiros_sintomas, limite_superior, posterior.data_primeiros_sintomas)
            raise ValidationError(f'Existe uma notificação posterior ({posterior.get_numero()}) realizada a menos de um mês para esse CPF.')
        return cpf

    def on_data_nascimento_change(self, data_nascimento):
        self.form.controller.set(idade=age(data_nascimento))

    def on_doenca_change(self, doenca):
        if doenca:
            is_dengue = doenca.nome == "Dengue"
            self.form.controller.visible(is_dengue, "sorologia-igm-dengue")
            self.form.controller.visible(not is_dengue, "sorologia-igm-chikungunya")

    def on_sexo_change(self, sexo):
        if sexo:
            print(sexo)
            if sexo.nome == "Masculino":
                self.form.controller.set(
                    periodo_gestacao=PeriodoGestacao.objects.filter(
                        nome="Não se aplica"
                    ).first()
                )
            else:
                self.form.controller.set(periodo_gestacao=None)

    
    def get_municipio_residencia_queryset(self, queryset):
        return queryset.nolookup()


class Checar(endpoints.Endpoint):
    cpf = endpoints.forms.CharField(label="CPF")
    cadastrar_nova = endpoints.forms.BooleanField(label="Forçar cadastro de nova ficha", help_text="Marqe \"Sim\" caso deseje cadastrar uma nova ficha ainda que exista outra cadastrada para esse CPF nos últimos 30 dias.", required=False)

    class Meta:
        modal = False
        icon = "plus"
        verbose_name = "Cadastrar Notificação Individual"

    def get(self):
        return (
            self.formfactory()
            .info("Informe o CPF para verificarmos se já existe alguma ficha cadastrada para o cidadão nos últimos 30 dias.")
            .fields('cpf', 'cadastrar_nova')
            .initial(cadastrar_nova=False)
        )
    
    def post(self):
        cpf = self.cleaned_data['cpf']
        cadastrar_nova = self.cleaned_data['cadastrar_nova']
        data_limite = datetime.today() - timedelta(days=30)
        qs = NotificacaoIndividual.objects.filter(cpf=cpf, data__gte=data_limite)
        if qs.exists() and not cadastrar_nova:
            raise ValidationError(f'Já existe uma ficha cadastrada para o CPF {cpf} nos últimos 30 dias. É necessário forçar o cadastro de uma nova ficha para prosseguir.')
        else:
            return self.redirect(f'/app/notificacaoindividual/cadastrar/?cpf={cpf}')

    def check_permission(self):
        return self.check_role("notificante", "administrador")


class Cadastrar(endpoints.AddEndpoint[NotificacaoIndividual], Mixin):
    class Meta:
        modal = False
        icon = "plus"
        verbose_name = "Cadastrar Notificação Individual"

    def get(self):
        cpf = self.request.GET.get('cpf')
        initial = dict(
            cpf=cpf,
            data=date.today(),
            municipio=Municipio.objects.first(),
            notificante=Notificante.objects.filter(
                cpf=self.request.user.username
            ).first(),
            unidade=self.get_unidade_inicial(),
            pais=Pais.objects.order_by("id").first(),
            pais_infeccao=Pais.objects.order_by("id").first(),
        )
        data_atualizado_cadsus = None
        esus_api_url = os.environ.get('ESUS_API_URL', 'http://localhost:8000')
        esus_api_token = os.environ.get('ESUS_API_TOKEN', '')
        headers = {'Authorization': f'Token {esus_api_token}'}
        response = requests.get('{}/consultar_cpf/{}/'.format(esus_api_url, cpf), headers=headers)
        dados = response.status_code == 200 and response.json() or {}
        if dados:
            sexo = Sexo.objects.filter(codigo=(dados['sexo'].upper()[0])).first() if dados['sexo'] else None
            data_nascimento = datetime.strptime(dados['dt_nascimento'], "%Y-%m-%d").date() if dados['dt_nascimento'] else None
            raca = Raca.objects.filter(nome__iexact=dados['raca_cor']).first() if dados['raca_cor'] else None
            escolaridade = Escolaridade.objects.filter(nome__iexact=dados['escolaridade']).first() if dados['escolaridade'] else None
            municipio = Municipio.objects.filter(nome__iexact=dados['municipio']).first() if dados['municipio'] else None
            data_atualizado_cadsus = datetime.strptime(dados['dt_atualizado_cadsus'], "%Y-%m-%d").date() if dados['dt_atualizado_cadsus'] else None
            initial.update(
                nome=dados['cidadao'],
                sexo=sexo,
                data_nascimento=data_nascimento,
                raca=raca,
                escolaridade=escolaridade,
                nome_mae=dados['mae'],
                cartao_sus=dados['cns'].strip() if dados['cns'] else '',
                telefone=dados['celular'],
                email=dados['email'],
                logradouro=dados['logradouro'],
                numero_residencia=dados['numero'],
                complemento=dados['complemento'],
                bairro=dados['bairro'],
                cep=dados['cep'],
                municipio_residencia=municipio,
                latitude=dados['latitude'],
                longitude=dados['longitude'],
            )
        info = None
        if data_atualizado_cadsus:
            info = "A data de atualização no CadSUS é {}.".format(data_atualizado_cadsus.strftime("%d/%m/%Y"))
        return super().get().initial(**initial).info(info)

    def check_permission(self):
        return self.check_role("notificante", "administrador")

    def on_cep_change(self, cep):
        self.form.controller.set(
            **buscar_endereco(cep, municipio="municipio_residencia")
        ) if not self.form.controller.get('bairro') else None

    def on_numero_residencia_change(self, numero):
        logradouro, numero, municipio, latitude, lontigude = self.form.controller.get(
            "logradouro", "numero_residencia", "municipio_residencia", "latitude", "lontigude"
        )
        if not latitude or not lontigude:
            if logradouro and numero and municipio:
                geolocation = places.geolocation(
                    "{}, {}, {}".format(logradouro, numero, municipio)
                )
                if geolocation:
                    self.form.controller.set(
                        latitude=geolocation[0], longitude=geolocation[1]
                    )

    def get_unidade_inicial(self):
        qs = UnidadeSaude.objects.filter(equipe__notificantes__cpf=self.request.user.username)
        return qs.first() if qs.count() == 1 else None

    def on_dengue_grave_change(self, value):
        self.form.controller.set(observacao=str(value))


class Editar(endpoints.EditEndpoint[NotificacaoIndividual], Mixin):
    class Meta:
        icon = 'pencil'
        modal = False
        verbose_name = "Editar Notificação Individual"

    def check_permission(self):
        return (self.check_role("regulador") and self.instance.data_envio) or ((self.instance.data_envio is None or self.instance.devolvida) and self.instance.notificante.cpf == self.request.user.username)


class Excluir(endpoints.DeleteEndpoint[NotificacaoIndividual]):
    class Meta:
        verbose_name = "Excluir Notificação Individual"

    def get(self):
        return super().get()


class Enviar(endpoints.InstanceEndpoint[NotificacaoIndividual]):
    class Meta:
        icon = 'right-long'
        verbose_name = 'Enviar'

    def get(self):
        return self.formfactory(self.instance).fields().info('Após o envio não será mais possível editar os dados da notificação a não ser que ela seja devolvida.')
    
    def post(self):
        self.instance.enviar()
        return super().post()

    def check_permission(self):
        return (self.check_role('administrador') or self.instance.notificante.cpf == self.request.user.username) and self.instance.pode_ser_enviada()


class Devolver(endpoints.InstanceEndpoint[NotificacaoIndividual]):
    motivo = endpoints.forms.CharField(label="Motivo", widget=endpoints.forms.Textarea())

    class Meta:
        icon = 'left-long'
        verbose_name = "Devolver"

    def get(self):
        return self.formfactory(self.instance).fields("motivo")
    
    def post(self):
        self.instance.devolver(self.request.user, self.cleaned_data['motivo'])
        return super().post()

    def check_permission(self):
        return self.check_role("regulador", "administrador") and self.instance.pode_ser_devolvida()


class Reenviar(endpoints.InstanceEndpoint[NotificacaoIndividual]):
    observacao_correcao = endpoints.forms.CharField(label="Observação da Correção", widget=endpoints.forms.Textarea())

    class Meta:
        icon = 'right-long'
        verbose_name = "Reenviar"

    def get(self):
        return self.formfactory(self.instance).fields("observacao_correcao")
    
    def post(self):
        self.instance.reenviar(self.cleaned_data['observacao_correcao'])
        return super().post()

    def check_permission(self):
        return self.instance.notificante.cpf == self.request.user.username and self.instance.pode_ser_reenviada()


class Finalizar(endpoints.InstanceEndpoint[NotificacaoIndividual]):

    class Meta:
        icon = "check"
        verbose_name = "Finalizar"

    def get(self):
        return self.formfactory(self.instance).fields("validada")

    def check_permission(self):
        return self.check_role("regulador", "administrador") and self.instance.pode_ser_finalizada()


class CadastrarMunicipio(endpoints.AddEndpoint[Municipio]):
    class Meta:
        verbose_name = "Cadastrar Município"

    
    def get(self):
        return self.formfactory(self.instance).fieldset('Dados Gerais', (('codigo', 'nome'), 'estado'))

    def check_permission(self):
        return self.check_role("notificante", "administrador")