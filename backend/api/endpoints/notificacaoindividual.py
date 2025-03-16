from slth import endpoints
from datetime import date
from ..models import *
from ..utils import buscar_endereco
from slth.integrations.google import places
from slth.utils import age


class NotificacoesIndividuais(endpoints.ListEndpoint[NotificacaoIndividual]):
    class Meta:
        verbose_name = 'Notificações Individuais'

    def get(self):
        return (
            super().get()
            .actions('notificacaoindividual.cadastrar', 'notificacaoindividual.visualizar', 'notificacaoindividual.editar', 'notificacaoindividual.excluir', 'notificacaoindividual.imprimir')
        )
    
    def check_permission(self):
        return self.check_role('notificante')


class Visualizar(endpoints.ViewEndpoint[NotificacaoIndividual]):
    class Meta:
        modal = False
        verbose_name = 'Visualizar Notificação Individual'

    def get(self):
        return (
            super().get()
        )
    
    def check_permission(self):
        return self.check_role('notificante')


class Imprimir(endpoints.InstanceEndpoint[NotificacaoIndividual]):
    class Meta:
        icon = 'pdf'
        modal = False
        verbose_name = 'Imprimir Notificação Individual'

    def get(self):
        return self.render(dict(obj=self), "ficha.html", pdf=True)
    
    def check_permission(self):
        return 1 or self.check_role('notificante')

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
            .values(nome='Carlos Breno')
        )
    
    def check_permission(self):
        return self.check_role('notificante')
    
    def on_cep_change(self, cep):
        self.form.controller.set(**buscar_endereco(cep, municipio='municipio_residencia'))

    def on_numero_residencia_change(self, numero):
        logradouro, numero, municipio = self.form.controller.get('logradouro', 'numero_residencia', 'municipio_residencia')
        if logradouro and numero and municipio:
            geolocation = places.geolocation('{}, {}, {}'.format(logradouro, numero, municipio))
            print(geolocation, 88888)
            if geolocation:
                self.form.controller.set(latitude=geolocation[0], longitude=geolocation[1])
        print(self.form.controller.values())
    
    def get_unidade_inicial(self):
        qs = UnidadeSaude.objects.filter(notificantes__cpf=self.request.user.username)
        return qs.first()  if qs.count() == 1 else None 
        
    

class Editar(endpoints.EditEndpoint[NotificacaoIndividual], Mixin):
    class Meta:
        modal = False
        verbose_name = 'Editar Notificação Individual'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[NotificacaoIndividual]):
    class Meta:
        verbose_name = 'Excluir Notificação Individual'

    def get(self):
        return (
            super().get()
        )

