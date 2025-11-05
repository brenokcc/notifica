from slth import endpoints
from ..models import *


class GestoresMunicipais(endpoints.ListEndpoint[GestorMunicipal]):
    class Meta:
        verbose_name = "Gestores Municipais"

    def get(self):
        return (
            super()
            .get()
            .actions(
                "gestormunicipal.visualizar",
                "gestormunicipal.editar",
                "gestormunicipal.excluir",
            )
        )

    def check_permission(self):
        return self.check_role("administrador")


class Cadastrar(endpoints.AddEndpoint[GestorMunicipal]):
    class Meta:
        icon = "plus"
        verbose_name = "Cadastrar Gestor de Municipal"

    def check_permission(self):
        return self.check_role("administrador")


class Visualizar(endpoints.ViewEndpoint[GestorMunicipal]):
    class Meta:
        modal = False
        icon = "eye"
        verbose_name = "Visualizar Gestor de Municipal"

    def check_permission(self):
        return self.check_role("administrador")


class Editar(endpoints.EditEndpoint[GestorMunicipal]):
    class Meta:
        icon = "pen"
        verbose_name = "Editar Gestor de Municipal"

    def check_permission(self):
        return self.check_role("administrador")


class Excluir(endpoints.DeleteEndpoint[GestorMunicipal]):
    class Meta:
        icon = "trash"
        verbose_name = "Excluir Gestor de Municipal"

    def check_permission(self):
        return self.check_role("administrador")
