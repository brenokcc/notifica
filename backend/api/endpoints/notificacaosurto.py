from slth import endpoints
from ..models import *


class NotificacoesSurto(endpoints.ListEndpoint[NotificacaoSurto]):
    class Meta:
        verbose_name = 'Notificaçõe de Surto'

    def get(self):
        return (
            super().get()
            .actions('notificacaosurto.cadastrar', 'notificacaosurto.editar', 'notificacaosurto.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[NotificacaoSurto]):
    class Meta:
        modal = False
        verbose_name = 'Cadastrar Notificação'
    

class Editar(endpoints.EditEndpoint[NotificacaoSurto]):
    class Meta:
        modal = False
        verbose_name = 'Editar Notificação'


class Excluir(endpoints.DeleteEndpoint[NotificacaoSurto]):
    class Meta:
        verbose_name = 'Excluir Notificação'


