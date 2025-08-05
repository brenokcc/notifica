from slth import endpoints
from ..models import *


class Racas(endpoints.ListEndpoint[Raca]):
    class Meta:
        verbose_name = "Raças"

    def get(self):
        return super().get().actions("raca.cadastrar", "raca.editar", "raca.excluir")

    def check_permission(self):
        return self.check_role("administrador")


class Cadastrar(endpoints.AddEndpoint[Raca]):
    class Meta:
        verbose_name = "Cadastrar Raça"

    def check_permission(self):
        return self.check_role("administrador")


class Editar(endpoints.EditEndpoint[Raca]):
    class Meta:
        verbose_name = "Editar Raça"

    def check_permission(self):
        return self.check_role("administrador")


class Excluir(endpoints.DeleteEndpoint[Raca]):
    class Meta:
        verbose_name = "Excluir Raça"
