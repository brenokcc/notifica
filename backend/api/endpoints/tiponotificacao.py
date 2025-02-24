from slth import endpoints
from ..models import *


class TiposNotificacao(endpoints.ListEndpoint[TipoNotificacao]):
    class Meta:
        verbose_name = 'Tipos de Notificação'

    def get(self):
        return (
            super().get()
            .actions('tiponotificacao.cadastrar', 'tiponotificacao.editar', 'tiponotificacao.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[TipoNotificacao]):
    class Meta:
        verbose_name = 'Cadastrar Tipo de Notificação'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[TipoNotificacao]):
    class Meta:
        verbose_name = 'Editar Tipo de Notificação'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[TipoNotificacao]):
    class Meta:
        verbose_name = 'Excluir Tipo de Notificação'

    def get(self):
        return (
            super().get()
        )

