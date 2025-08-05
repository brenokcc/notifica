from slth import endpoints
from ..models import *


class TiposNotificacao(endpoints.ListEndpoint[TipoNotificacao]):
    class Meta:
        verbose_name = "Tipos de Notificação"

    def get(self):
        return (
            super()
            .get()
            .actions(
                "tiponotificacao.cadastrar",
                "tiponotificacao.editar",
                "tiponotificacao.excluir",
            )
        )

    def check_permission(self):
        return self.check_role("administrador")


class Cadastrar(endpoints.AddEndpoint[TipoNotificacao]):
    class Meta:
        verbose_name = "Cadastrar Tipo de Notificação"

    def check_permission(self):
        return self.check_role("administrador")


class Editar(endpoints.EditEndpoint[TipoNotificacao]):
    class Meta:
        verbose_name = "Editar Tipo de Notificação"

    def check_permission(self):
        return self.check_role("administrador")


class Excluir(endpoints.DeleteEndpoint[TipoNotificacao]):
    class Meta:
        verbose_name = "Excluir Tipo de Notificação"
