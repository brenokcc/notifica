from slth import endpoints
from datetime import date
from ..models import *
from slth.utils import age


class NotificacoesIndividuais(endpoints.ListEndpoint[NotificacaoIndividual]):
    class Meta:
        verbose_name = 'Notificações Individuais'

    def get(self):
        return (
            super().get()
            .actions('notificacaoindividual.cadastrar', 'notificacaoindividual.visualizar', 'notificacaoindividual.editar', 'notificacaoindividual.excluir')
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


class Mixin:
    def on_data_nascimento_change(self, controller, values):
        data_nascimento = values.get('data_nascimento')
        controller.set(idade=age(data_nascimento))

    def get_unidade_queryset(self, queryset, controller):
        return queryset.filter(notificantes__cpf=self.request.user.username)
    
    def on_doenca_change(self, controller, values):
        doenca = values.get('doenca')
        if doenca:
            is_dengue = doenca.nome == 'Dengue'
            controller.visible(is_dengue, 'sorologia-igm-dengue')
            controller.visible(not is_dengue, 'sorologia-igm-chikungunya')

    def on_sexo_change(self, controller, values):
        sexo = values.get('sexo')
        if sexo:
            print(sexo)
            if sexo.nome == "Masculino":
                controller.set(periodo_gestacao=PeriodoGestacao.objects.filter(nome='Não se aplica').first())
            else:
                controller.set(periodo_gestacao=None)


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
                unidade=self.get_unidade_inicial()
            )
        )
    
    def check_permission(self):
        return self.check_role('notificante')
    
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

