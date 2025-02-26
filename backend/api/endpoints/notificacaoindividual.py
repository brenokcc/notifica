from slth import endpoints
from ..models import *


class NotificacoesIndividuais(endpoints.ListEndpoint[NotificacaoIndividual]):
    class Meta:
        verbose_name = 'Notificações Individuais'

    def get(self):
        return (
            super().get()
            .actions('notificacaoindividual.cadastrar', 'notificacaoindividual.editar', 'notificacaoindividual.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[NotificacaoIndividual]):
    class Meta:
        modal = False
        verbose_name = 'Cadastrar Notificação Individual'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[NotificacaoIndividual]):
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

