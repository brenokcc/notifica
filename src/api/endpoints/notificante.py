from slth import endpoints
from ..models import *


class Notificantes(endpoints.ListEndpoint[Notificante]):
    class Meta:
        verbose_name = "Notificantes"

    def get(self):
        return (
            super()
            .get()
            .actions(
                "notificante.editar", "notificante.excluir"
            )
        )

    def check_permission(self):
        return self.check_role("administrador")


class Cadastrar(endpoints.AddEndpoint[Notificante]):
    class Meta:
        verbose_name = "Cadastrar Notificante"

    def check_permission(self):
        return self.check_role("regulador", "administrador", "gm", "gu")


class Editar(endpoints.EditEndpoint[Notificante]):
    class Meta:
        verbose_name = "Editar Notificante"

    def check_permission(self):
        return self.check_role("administrador")


class Excluir(endpoints.DeleteEndpoint[Notificante]):
    class Meta:
        verbose_name = "Excluir Notificante"
