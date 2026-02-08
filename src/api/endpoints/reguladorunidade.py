from slth import endpoints
from ..models import *


class ReguladoresUnidade(endpoints.ListEndpoint[ReguladorUnidade]):
    class Meta:
        verbose_name = "Reguladores de Unidade"

    def get(self):
        return (
            super()
            .get()
            .actions(
                "regulador.visualizar",
                "regulador.editar",
                "regulador.excluir",
            )
        )

    def check_permission(self):
        return self.check_role("administrador")


class Cadastrar(endpoints.AddEndpoint[ReguladorUnidade]):
    class Meta:
        icon = "plus"
        verbose_name = "Cadastrar Regulador de Unidade"

    def check_permission(self):
        return self.check_role("administrador", "gm")


class Visualizar(endpoints.ViewEndpoint[ReguladorUnidade]):
    class Meta:
        modal = False
        icon = "eye"
        verbose_name = "Visualizar Regulador de Unidade"

    def check_permission(self):
        return self.check_role("administrador")


class Editar(endpoints.EditEndpoint[ReguladorUnidade]):
    class Meta:
        icon = "pen"
        verbose_name = "Editar Regulador de Unidade"

    def check_permission(self):
        return self.check_role('administrador')


class Excluir(endpoints.DeleteEndpoint[ReguladorUnidade]):
    class Meta:
        icon = "trash"
        verbose_name = "Excluir Regulador de Unidade"
