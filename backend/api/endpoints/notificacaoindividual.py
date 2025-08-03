from slth import endpoints
from datetime import date
from ..models import *
from ..utils import buscar_endereco
from slth.integrations.google import places
from slth.utils import age
from slth.components import FileViewer


class NotificacoesIndividuais(endpoints.ListEndpoint[NotificacaoIndividual]):
    class Meta:
        verbose_name = 'Notificações Individuais'

    def get(self):
        return (
            super().get()
            .actions('notificacaoindividual.cadastrar', 'notificacaoindividual.visualizar', 'notificacaoindividual.editar', 'notificacaoindividual.excluir', 'notificacaoindividual.imprimir')
        )
    
    def check_permission(self):
        return self.check_role('notificante', 'regulador')


class AguardandoValidacao(endpoints.QuerySetEndpoint[NotificacaoIndividual]):
    class Meta:
        icon = 'bell'
        verbose_name = 'Notificações Individuais - Aguardando Validação'

    def get(self):
        return super().get().all().filter(validada__isnull=True).actions('notificacaoindividual.visualizar')

    def check_permission(self):
        return self.check_role('regulador')


class Visualizar(endpoints.ViewEndpoint[NotificacaoIndividual]):
    class Meta:
        modal = False
        verbose_name = 'Visualizar Notificação Individual'

    def get(self):
        return (
            super().get()
        )
    
    def check_permission(self):
        return self.check_role('notificante', 'regulador')


class Imprimir(endpoints.InstanceEndpoint[NotificacaoIndividual]):
    class Meta:
        icon = 'file-pdf'
        modal = True
        verbose_name = 'Imprimir Notificação Individual'

    def get(self):
        if self.request.GET.get('token'):
            return self.render(dict(obj=self.instance), self.instance.doenca.modelo_ficha, pdf=True)
        else:
            return FileViewer(self.get_api_url(self.instance.pk) + '?token=' + self.instance.token)
    
    def check_permission(self):
        return self.check_role('notificante') or self.request.GET.get("token") == self.instance.token

class Mixin:
    def on_data_nascimento_change(self, data_nascimento):
        self.form.controller.set(idade=age(data_nascimento))

    def get_unidade_queryset(self, queryset):
        return queryset.filter(notificantes__cpf=self.request.user.username)
    
    def on_doenca_change(self, doenca):
        if doenca:
            is_dengue = doenca.nome == 'Dengue'
            self.form.controller.visible(is_dengue, 'sorologia-igm-dengue')
            self.form.controller.visible(not is_dengue, 'sorologia-igm-chikungunya')

    def on_sexo_change(self, sexo):
        if sexo:
            print(sexo)
            if sexo.nome == "Masculino":
                self.form.controller.set(periodo_gestacao=PeriodoGestacao.objects.filter(nome='Não se aplica').first())
            else:
                self.form.controller.set(periodo_gestacao=None)


class Cadastrar(endpoints.AddEndpoint[NotificacaoIndividual], Mixin):
    class Meta:
        modal = False
        icon = 'plus'
        verbose_name = 'Cadastrar Notificação Individual'

    def get(self):
        return (
            super().get()
            .initial(
                data=date.today(),
                municipio=Municipio.objects.first(),
                notificante=Notificante.objects.filter(cpf=self.request.user.username).first(),
                unidade=self.get_unidade_inicial(),
                pais=Pais.objects.order_by('id').first(),
                pais_infeccao=Pais.objects.order_by('id').first(),
            )
        )
    
    def check_permission(self):
        return self.check_role('notificante')
    
    def on_cep_change(self, cep):
        self.form.controller.set(**buscar_endereco(cep, municipio='municipio_residencia'))

    def on_numero_residencia_change(self, numero):
        logradouro, numero, municipio = self.form.controller.get('logradouro', 'numero_residencia', 'municipio_residencia')
        if logradouro and numero and municipio:
            geolocation = places.geolocation('{}, {}, {}'.format(logradouro, numero, municipio))
            if geolocation:
                self.form.controller.set(latitude=geolocation[0], longitude=geolocation[1])
        print(self.form.controller.values())
    
    def get_unidade_inicial(self):
        qs = UnidadeSaude.objects.filter(notificantes__cpf=self.request.user.username)
        return qs.first()  if qs.count() == 1 else None 
    
    def on_dengue_grave_change(self, value):
        print(value)
        print(self.form.controller.values())
        self.form.controller.set(observacao=str(value))
        
    

class Editar(endpoints.EditEndpoint[NotificacaoIndividual], Mixin):
    class Meta:
        modal = False
        verbose_name = 'Editar Notificação Individual'

    def get(self):
        return (
            super().get()
        )

    def check_permission(self):
        return self.request.user.is_superuser or self.instance.notificante.cpf == self.request.user.username

class Excluir(endpoints.DeleteEndpoint[NotificacaoIndividual]):
    class Meta:
        verbose_name = 'Excluir Notificação Individual'

    def get(self):
        return (
            super().get()
        )


class Validar(endpoints.InstanceEndpoint[NotificacaoIndividual]):

    class Meta:
        icon = "check"
        verbose_name = "Validar"

    def get(self):
        return self.formfactory(self.instance).fields('validada')
    
    def check_permission(self):
        return self.check_role('regulador')
