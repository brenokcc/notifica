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
                "notificacaoindividual.clonar",
            )
            .order_by("numero")
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
        return self.check_role("notificante", "administrador")
    

class AguardandoResponsavelBloqueio(endpoints.QuerySetEndpoint[NotificacaoIndividual]):
    class Meta:
        modal = False
        icon = "bell"
        verbose_name = "Aguardando atributição de responsável pelo bloqueio"

    def get_queryset(self):
        return super().get_queryset().aguardando_responsavel_bloqueio()

    def check_permission(self):
        return self.check_role("supervisor")


class AguardandoBloqueio(endpoints.QuerySetEndpoint[NotificacaoIndividual]):
    class Meta:
        modal = False
        icon = "bell"
        verbose_name = "Aguardando Bloqueio"

    def get_queryset(self):
        return super().get_queryset().aguardando_bloqueio().filter(responsavel_bloqueio__cpf=self.request.user.username)

    def check_permission(self):
        return self.check_role("agente")
    

class AguardandoJustificativaPerdaPrazoBloqueio(endpoints.QuerySetEndpoint[NotificacaoIndividual]):
    class Meta:
        modal = False
        icon = "bell"
        verbose_name = "Aguardando justificativa de perda de prazo"

    def get_queryset(self):
        return super().get_queryset().aguardando_justificativa_perda_prazo().filter(responsavel_bloqueio__cpf=self.request.user.username).actions('notificacaoindividual.justificarperdaprazobloqueio')

    def check_permission(self):
        return self.check_role("agente")


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
        return self.check_role("notificante", "administrador", "regulador")


class AguardandoValidacao(endpoints.QuerySetEndpoint[NotificacaoIndividual]):
    class Meta:
        modal = False
        icon = "bell"
        verbose_name = "Notificações individuais aguardando validação"

    def get_queryset(self):
        return super().get_queryset().aguardando_validacao()

    def check_permission(self):
        return self.check_role("regulador", "administrador")



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
        return self.check_role("notificante", "regulador", "administrador", "gu", "gm")# and self.check_instance()


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


class Clonar(endpoints.InstanceEndpoint[NotificacaoIndividual]):
    nova_doenca = endpoints.forms.ModelChoiceField(Doenca.objects, label="Doença")
    
    class Meta:
        icon = "copy"
        modal = True
        verbose_name = "Clonar"

    def get(self):
        return self.formfactory().fields('nova_doenca')

    def post(self):
        clone = self.instance.clonar(self.cleaned_data['nova_doenca'])
        return self.redirect(f'/app/notificacaoindividual/visualizar/{clone.pk}/')
    
    def check_permission(self):
        return self.check_role("regulador", "administrador")


class Mixin:

    # def on_criterio_confirmacao_change(self, criterio_confirmacao):
    #     em_investigacao = criterio_confirmacao and criterio_confirmacao.nome == 'Em investigação' or False
    #     self.form.controller.visible(not em_investigacao, 'data_encerramento')

    def clean_data_encerramento(self, data):
        data_encerramento = data.get('data_encerramento')
        criterio_confirmacao = data.get('criterio_confirmacao')
        if data_encerramento and criterio_confirmacao and criterio_confirmacao.id == CriterioConfirmacao.EM_INVESTIGACAO:
            raise ValidationError('A data do encerramento não pode ser informada para casos em investigação')
        return data_encerramento

    def clean_cpf(self, data):
        cpf = data.get('cpf')
        data_primeiros_sintomas = data['data_primeiros_sintomas']
        limite_inferior = data_primeiros_sintomas - timedelta(days=30)
        limite_superior= data_primeiros_sintomas + timedelta(days=30)
        anterior = NotificacaoIndividual.objects.filter(cpf=cpf, data_primeiros_sintomas__gte=limite_inferior, data_primeiros_sintomas__lte=data_primeiros_sintomas).exclude(pk=self.instance.pk).first()
        if anterior and not self.instance.pk:
            raise ValidationError(f'Existe uma notificação anterior ({anterior.numero}) realizada a menos de um mês para esse CPF.')
        posterior = NotificacaoIndividual.objects.filter(cpf=cpf, data_primeiros_sintomas__lte=limite_superior, data_primeiros_sintomas__gte=data_primeiros_sintomas).exclude(pk=self.instance.pk).first()
        if posterior and not self.instance.pk:
            raise ValidationError(f'Existe uma notificação posterior ({posterior.numero}) realizada a menos de um mês para esse CPF.')
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
    
    def get_municipio_infeccao_queryset(self, queryset):
        return queryset.nolookup()


class Checar(endpoints.Endpoint):

    ACAO_CHOICES = [
        ['alertar', 'Alertar sobre existência da ficha'],
        ['visualizar', 'Visualizar ficha existente'],
        ['cadastrar', 'Cadastrar nova ficha'],
    ]

    cpf = endpoints.forms.CharField(label="CPF", required=False)
    cns = endpoints.forms.CharField(label="CNS", required=False)
    acao = endpoints.forms.ChoiceField(label="Ação no caso de ficha já cadastrada", help_text="Indique o que deseja fazer caso exista outra ficha cadastrada para esse CPF/CNS nos últimos 30 dias.", choices=ACAO_CHOICES)

    class Meta:
        modal = False
        icon = "plus"
        verbose_name = "Cadastrar Notificação Individual"

    def get(self):
        return (
            self.formfactory()
            .info("Informe o CPF ou CNS para verificarmos se já existe alguma ficha cadastrada para o cidadão nos últimos 30 dias.")
            .fieldset(None, fields=(('cpf', 'cns'), 'acao'))
            .initial(acao='alertar')
        )
    
    def post(self):
        cpf = self.cleaned_data['cpf']
        cns = self.cleaned_data['cns']
        if not cpf and not cns:
            raise ValidationError(f'Informe o CPF ou CNS do paciente.')
        acao = self.cleaned_data['acao']
        data_limite = datetime.today() - timedelta(days=30)
        qs1 = NotificacaoIndividual.objects.filter(cpf=cpf, data__gte=data_limite)
        qs2 = NotificacaoIndividual.objects.filter(cartao_sus=cns, data__gte=data_limite)
        if (qs1.exists() or qs2.exists()):
            if acao == 'alertar':
                raise ValidationError(f'Já existe uma ficha cadastrada para o CPF {cpf} nos últimos 30 dias. É necessário forçar o cadastro de uma nova ficha para prosseguir.')
            if acao == 'visualizar':
                obj = qs1.first() or qs2.first()
                return self.redirect(f'/app/notificacaoindividual/visualizar/{obj.pk}/')
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
        hidden = []
        initial = dict(
            cpf=cpf,
            data=date.today(),
            municipio=self.get_municipio_inicial(),
            notificante=Notificante.objects.filter(
                cpf=self.request.user.username
            ).first(),
            unidade=self.get_unidade_inicial(),
            pais=Pais.objects.order_by("id").first(),
            pais_infeccao=Pais.objects.order_by("id").first(),
            criterio_confirmacao=CriterioConfirmacao.EM_INVESTIGACAO,
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
            latitude=dados['latitude']
            longitude=dados['longitude']
            logradouro=dados['logradouro']
            numero_residencia=dados['numero']
            if not latitude or not longitude:
                if logradouro and numero_residencia and municipio:
                    geolocation = places.geolocation("{}, {}, {}".format(logradouro, numero_residencia, municipio))
                    if geolocation:
                        latitude=geolocation[0]
                        longitude=geolocation[1]
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
                logradouro=logradouro,
                numero_residencia=numero_residencia,
                complemento=dados['complemento'],
                bairro=dados['bairro'],
                cep=dados['cep'],
                municipio_residencia=municipio,
                latitude=latitude,
                longitude=longitude,
            )
        info = None
        if data_atualizado_cadsus:
            info = "A data de atualização no CadSUS é {}.".format(data_atualizado_cadsus.strftime("%d/%m/%Y"))
        if self.instance.id is None or (self.instance.criterio_confirmacao and self.instance.criretorio_confirmacao.nome == "Em investigação"):
            hidden.append('data_encerramento')
        return super().get().initial(**initial).info(info) #.hidden(*hidden)

    def check_permission(self):
        return self.check_role("notificante", "administrador")

    def on_cep_change(self, cep):
        self.form.controller.set(
            **buscar_endereco(cep, municipio="municipio_residencia")
        ) if not self.form.controller.get('bairro') else None

    def on_numero_residencia_change(self, numero):
        logradouro, numero, municipio, latitude, longitude = self.form.controller.get(
            "logradouro", "numero_residencia", "municipio_residencia", "latitude", "longitude"
        )
        if not latitude or not longitude:
            if logradouro and numero and municipio:
                geolocation = places.geolocation(
                    "{}, {}, {}".format(logradouro, numero, municipio)
                )
                if geolocation:
                    self.form.controller.set(
                        latitude=geolocation[0], longitude=geolocation[1]
                    )

    def get_municipio_inicial(self):
        return UnidadeSaude.objects.filter(equipe__notificantes__cpf=self.request.user.username).values_list('municipio', flat=True).first()

    def get_unidade_inicial(self):
        qs = UnidadeSaude.objects.filter(equipe__notificantes__cpf=self.request.user.username)
        return qs.first() if qs.count() == 1 else None

    def on_dengue_grave_change(self, value):
        self.form.controller.set(observacao=str(value))

    def post(self):
        cpf = self.cleaned_data['cpf']
        cartao_sus = self.cleaned_data['cartao_sus']
        if not cpf and not cartao_sus:
            raise ValidationError('Informe o CPF ou Cartão SUS.')
        self.redirect('/app/notificacaoindividual/notificacoesindividuais/')

class Editar(endpoints.EditEndpoint[NotificacaoIndividual], Mixin):
    class Meta:
        icon = 'pencil'
        modal = False
        verbose_name = "Editar Notificação Individual"

    def check_permission(self):
        return (self.check_role("regulador") and self.instance.data_envio and not self.instance.devolvida) or ((self.instance.data_envio is None or self.instance.devolvida) and self.instance.notificante.cpf == self.request.user.username)


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


class EvoluirCaso(endpoints.RelationEndpoint[Evolucao]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Evoluir Caso'

    def clean_data(self, data):
        data = data['data']
        if data.date() < self.source.data_primeiros_sintomas:
            raise ValidationError('A data deve ser maior do que a data dos primeiros sintomas.')
        ultima_evolucao = self.source.evolucao_set.order_by('data').last()
        if ultima_evolucao and data < ultima_evolucao.data:
            raise ValidationError('A data deve ser maior do que a data da última evolução.')
        return data
    
    def formfactory(self):
        return (
            super()
            .formfactory().fields(notificacao=self.source, notificante=self.request.user)
            .fieldset("Dados Gerais", ("notificacao", "notificante", "data", "observacao"))
            .initial(data=date.today())
        )

    def check_permission(self):
        return self.check_role("notificante") and self.source.validada and not self.source.data_encerramento


class Bloqueios(endpoints.QuerySetEndpoint[NotificacaoIndividual]):

    class Meta:
        modal = False
        icon = "store-slash"
        verbose_name = "Bloqueios"

    def get(self):
        return super().get().bloqueios()
    
    def check_permission(self):
        return self.check_role("agente", "regulador", "gm", "supervisor")


class AtribuirBloqueio(endpoints.InstanceEndpoint[NotificacaoIndividual]):

    class Meta:
        icon = "person"
        verbose_name = "Atribuir Responsável"

    def get(self):
        return self.formfactory().fields('responsavel_bloqueio')

    def check_permission(self):
        return self.check_role("supervisor") and self.instance.bloqueio is None
    
    def get_responsavel_bloqueio_queryset(self, queryset):
        return queryset.nolookup().filter(municipio=self.instance.unidade.municipio)


class RegistrarBloqueio(endpoints.InstanceEndpoint[NotificacaoIndividual]):

    class Meta:
        icon = "store-slash"
        verbose_name = "Bloqueio"

    def get(self):
        return self.formfactory().fields('bloqueio', 'tipo_bloqueio')
    
    def post(self):
        self.instance.data_bloqueio = datetime.now()
        self.instance.responsavel_bloqueio = Agente.objects.filter(cpf=self.request.user.username).first()
        self.instance.save()
        return super().post()
    
    def check_permission(self):
        return self.check_role("regulador") or (self.check_role("agente") and self.instance.pode_registrar_bloqueio())
    

class JustificarPerdaPrazoBloqueio(endpoints.InstanceEndpoint[NotificacaoIndividual]):

    class Meta:
        icon = "question"
        verbose_name = "Justificar"

    def get(self):
        return self.formfactory().fields('motivo_perda_prazo_bloqueio', 'observacao_bloqueio')
    
    def check_permission(self):
        return self.check_role("regulador") or (self.check_role("agente") and self.instance.motivo_perda_prazo_bloqueio is None and not self.instance.pode_registrar_bloqueio())