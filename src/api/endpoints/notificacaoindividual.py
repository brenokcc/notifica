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
                "notificacaoindividual.cadastrar",
                "notificacaoindividual.visualizar",
                "notificacaoindividual.editar",
                "notificacaoindividual.excluir",
                "notificacaoindividual.imprimir",
            )
        )

    def check_permission(self):
        return self.check_role("notificante", "regulador", "administrador")


class AguardandoEnvio(endpoints.QuerySetEndpoint[NotificacaoIndividual]):
    class Meta:
        modal = False
        icon = "bell"
        verbose_name = "Notificações Individuais Aguardando Envio"

    def get_queryset(self):
        return (
            super().get_queryset().all()
            .filter(data_envio__isnull=True)
            .filter(notificante__cpf=self.request.user.username)
            .actions(
                "notificacaoindividual.visualizar", "notificacaoindividual.imprimir"
            )
        )

    def check_permission(self):
        return self.check_role("notificante", "administrador") and self.get_queryset().exists()

class AguardandoCorrecao(endpoints.QuerySetEndpoint[NotificacaoIndividual]):
    class Meta:
        modal = False
        icon = "bell"
        verbose_name = "Notificações Individuais Aguardando Correção"

    def get_queryset(self):
        return (
            super().get_queryset().all()
            .filter(data_envio__isnull=False).filter(devolucao__isnull=False, devolucao__observacao_correcao__isnull=True)
            .filter(notificante__cpf=self.request.user.username)
            .actions(
                "notificacaoindividual.visualizar", "notificacaoindividual.imprimir"
            )
        )

    def check_permission(self):
        return self.check_role("notificante", "administrador") and self.get_queryset().exists()

class Enviar(endpoints.InstanceEndpoint[NotificacaoIndividual]):
    class Meta:
        icon = 'right-long'
        verbose_name = 'Enviar'

    def get(self):
        return self.formfactory(self.instance).fields().info('Após o envio não será mais possível editar os dados da ficha.')
    
    def post(self):
        self.instance.data_envio = datetime.now()
        self.instance.save()
        return super().post()

    def check_permission(self):
        return self.instance.data_envio is None and (self.check_role('administrador') or self.instance.notificante.cpf == self.request.user.username)


class AguardandoValidacao(endpoints.QuerySetEndpoint[NotificacaoIndividual]):
    class Meta:
        modal = False
        icon = "bell"
        verbose_name = "Notificações Individuais Aguardando Validação"

    def get_queryset(self):
        return (
            super().get_queryset().all()
            .filter(validada__isnull=True, data_envio__isnull=False).exclude(devolucao__isnull=False, devolucao__observacao_correcao__isnull=True)
            .actions(
                "notificacaoindividual.visualizar", "notificacaoindividual.imprimir"
            )
        )

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
        return self.check_role("notificante", "regulador", "administrador")


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
            self.check_role("notificante", "regulador", "administrador")
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


class Cadastrar(endpoints.AddEndpoint[NotificacaoIndividual], Mixin):
    class Meta:
        modal = False
        icon = "plus"
        verbose_name = "Cadastrar Notificação Individual"

    def get(self):
        return (
            super()
            .get()
            .initial(
                data=date.today(),
                municipio=Municipio.objects.first(),
                notificante=Notificante.objects.filter(
                    cpf=self.request.user.username
                ).first(),
                unidade=self.get_unidade_inicial(),
                pais=Pais.objects.order_by("id").first(),
                pais_infeccao=Pais.objects.order_by("id").first(),
            )
        )

    def check_permission(self):
        return self.check_role("notificante", "regulador", "administrador")

    def on_cep_change(self, cep):
        self.form.controller.set(
            **buscar_endereco(cep, municipio="municipio_residencia")
        )

    def on_numero_residencia_change(self, numero):
        logradouro, numero, municipio = self.form.controller.get(
            "logradouro", "numero_residencia", "municipio_residencia"
        )
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
        print(value)
        print(self.form.controller.values())
        self.form.controller.set(observacao=str(value))


class Editar(endpoints.EditEndpoint[NotificacaoIndividual], Mixin):
    class Meta:
        icon = 'pencil'
        modal = False
        verbose_name = "Editar Notificação Individual"

    def check_permission(self):
        return (
            self.request.user.is_superuser
            or self.instance.notificante.cpf == self.request.user.username
        ) and self.instance.validada is None


class Excluir(endpoints.DeleteEndpoint[NotificacaoIndividual]):
    class Meta:
        verbose_name = "Excluir Notificação Individual"

    def get(self):
        return super().get()


class Devolver(endpoints.InstanceEndpoint[NotificacaoIndividual]):
    motivo = endpoints.forms.CharField(label="Motivo", widget=endpoints.forms.Textarea())

    class Meta:
        icon = 'left-long'
        verbose_name = "Devolver"

    def get(self):
        return self.formfactory(self.instance).fields("motivo")
    
    def post(self):
        self.instance.devolucao_set.create(avaliador=self.request.user, data=datetime.now(), motivo=self.cleaned_data['motivo'])
        return super().post()

    def check_permission(self):
        return self.check_role("regulador", "administrador") and self.instance.validada is None


class Corrigir(endpoints.InstanceEndpoint[NotificacaoIndividual]):
    observacao_correcao = endpoints.forms.CharField(label="Observação da Correção", widget=endpoints.forms.Textarea())

    class Meta:
        icon = 'right-long'
        verbose_name = "Reenviar"

    def get(self):
        return self.formfactory(self.instance).fields("observacao_correcao")
    
    def post(self):
        self.instance.devolucao_set.filter(observacao_correcao__isnull=True).update(data_correcao=datetime.now(), observacao_correcao=self.cleaned_data['observacao_correcao'])
        return super().post()

    def check_permission(self):
        return self.check_role("notificante") and self.instance.notificante.cpf == self.request.user.username and self.instance.devolucao_set.filter(observacao_correcao__isnull=True).exists()


class Finalizar(endpoints.InstanceEndpoint[NotificacaoIndividual]):

    class Meta:
        icon = "check"
        verbose_name = "Finalizar"

    def get(self):
        return self.formfactory(self.instance).fields("validada")

    def check_permission(self):
        return self.check_role("regulador", "administrador") and self.instance.validada is None
