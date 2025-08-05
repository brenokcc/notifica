from slth import endpoints
from ..models import *


class Doencas(endpoints.ListEndpoint[Doenca]):

    def get(self):
        return (
            super().get().actions("doenca.cadastrar", "doenca.editar", "doenca.excluir")
        )

    def check_permission(self):
        return self.check_role("administrador")


class Cadastrar(endpoints.AddEndpoint[Doenca]):
    class Meta:
        verbose_name = "Cadastrar Cor"

    def check_permission(self):
        return self.check_role("administrador")


class Editar(endpoints.EditEndpoint[Doenca]):
    class Meta:
        verbose_name = "Editar Doença"

    def check_permission(self):
        return self.check_role("administrador")


class Excluir(endpoints.DeleteEndpoint[Doenca]):
    class Meta:
        verbose_name = "Excluir Doença"
