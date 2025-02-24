from slth import endpoints
from ..models import *


class Notificacoes(endpoints.ListEndpoint[Notificacao]):
    class Meta:
        verbose_name = 'Notificações'

    def get(self):
        return (
            super().get()
            .fields('tipo', 'doenca', 'data', 'notificante', 'unidade')
            .actions('notificacao.cadastrar', 'notificacao.editar', 'notificacao.excluir')
        )

class Mixin:

    def get_tipo_queryset(self, queryset, values):
        return queryset.filter(nome__in=["Individual", "Surto"])

    def on_tipo_change(self, controller, values):
        tipo = values.get('tipo')
        if tipo:
            if tipo.nome == "Individual":
                controller.show('detalhamento_individual')
                controller.hide('detalhamento_surto')
            if tipo.nome  == "Surto":
                controller.show('detalhamento_surto')
                controller.hide('detalhamento_individual')

    def on_detalhamento_individual__sexo_change(self, controller, values):
        print(888888)


class Cadastrar(endpoints.AddEndpoint[Notificacao], Mixin):
    class Meta:
        modal = False
        verbose_name = 'Cadastrar Notificação'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[Notificacao], Mixin):
    class Meta:
        modal = False
        verbose_name = 'Editar Notificação'

    def get(self):
        hidden = []
        if self.instance.tipo.nome == 'Individual':
            hidden.append('detalhamento_surto')
        if self.instance.tipo.nome == 'Surto':
            hidden.append('detalhamento_individual')
        return (
            super().get().hidden(*hidden)
        )


class Excluir(endpoints.DeleteEndpoint[Notificacao]):
    class Meta:
        verbose_name = 'Excluir Notificação'

    def get(self):
        return (
            super().get()
        )

