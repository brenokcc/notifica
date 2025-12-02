from slth import endpoints
from ..models import *


class GestoresUnidade(endpoints.ListEndpoint[GestorUnidade]):
    class Meta:
        verbose_name = "Gestores de Unidade"

    def get(self):
        return (
            super()
            .get()
            .actions(
                "gestorunidade.visualizar",
                "gestorunidade.editar",
                "gestorunidade.excluir",
            )
        )

    def check_permission(self):
        return self.check_role("administrador")


class Cadastrar(endpoints.AddEndpoint[GestorUnidade]):
    class Meta:
        icon = "plus"
        verbose_name = "Cadastrar Gestor de Unidade"

    def check_permission(self):
        return self.check_role("regulador", "administrador", "gm", "gu")


class Visualizar(endpoints.ViewEndpoint[GestorUnidade]):
    class Meta:
        modal = False
        icon = "eye"
        verbose_name = "Visualizar Gestor de Unidade"

    def check_permission(self):
        return self.check_role("administrador")


class Editar(endpoints.EditEndpoint[GestorUnidade]):
    class Meta:
        icon = "pen"
        verbose_name = "Editar Gestor de Unidade"

    def check_permission(self):
        return self.check_role("administrador")


class Excluir(endpoints.DeleteEndpoint[GestorUnidade]):
    class Meta:
        icon = "trash"
        verbose_name = "Excluir Gestor de Unidade"

