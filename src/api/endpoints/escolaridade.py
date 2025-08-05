from slth import endpoints
from ..models import *


class Escolaridades(endpoints.ListEndpoint[Escolaridade]):
    class Meta:
        verbose_name = "Escolaridades"

    def get(self):
        return (
            super()
            .get()
            .actions(
                "escolaridade.cadastrar", "escolaridade.editar", "escolaridade.excluir"
            )
        )

    def check_permission(self):
        return self.check_role("administrador")


class Cadastrar(endpoints.AddEndpoint[Escolaridade]):
    class Meta:
        verbose_name = "Cadastrar Escolaridade"

    def check_permission(self):
        return self.check_role("administrador")


class Editar(endpoints.EditEndpoint[Escolaridade]):
    class Meta:
        verbose_name = "Editar Escolaridade"

    def check_permission(self):
        return self.check_role("administrador")


class Excluir(endpoints.DeleteEndpoint[Escolaridade]):
    class Meta:
        verbose_name = "Excluir Escolaridade"
