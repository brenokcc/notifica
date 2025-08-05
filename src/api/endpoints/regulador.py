from slth import endpoints
from ..models import *


class Reguladores(endpoints.ListEndpoint[Regulador]):
    class Meta:
        verbose_name = "Reguladores"

    def get(self):
        return (
            super()
            .get()
            .actions(
                "regulador.cadastrar",
                "regulador.visualizar",
                "regulador.editar",
                "regulador.excluir",
            )
        )

    def check_permission(self):
        return self.check_role("administrador")


class Cadastrar(endpoints.AddEndpoint[Regulador]):
    class Meta:
        icon = "plus"
        verbose_name = "Cadastrar Regulador"

    def check_permission(self):
        return self.check_role("administrador")


class Visualizar(endpoints.ViewEndpoint[Regulador]):
    class Meta:
        modal = False
        icon = "eye"
        verbose_name = "Visualizar Regulador"

    def check_permission(self):
        return self.check_role("administrador")


class Editar(endpoints.EditEndpoint[Regulador]):
    class Meta:
        icon = "pen"
        verbose_name = "Editar Regulador"


class Excluir(endpoints.DeleteEndpoint[Regulador]):
    class Meta:
        icon = "trash"
        verbose_name = "Excluir Regulador"
