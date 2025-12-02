from slth import endpoints
from ..models import *


class Sexos(endpoints.ListEndpoint[Sexo]):
    class Meta:
        verbose_name = "Sexos"

    def get(self):
        return super().get().actions("sexo.cadastrar", "sexo.editar", "sexo.excluir")

    def check_permission(self):
        return self.check_role("administrador")


class Cadastrar(endpoints.AddEndpoint[Sexo]):
    class Meta:
        verbose_name = "Cadastrar Sexo"

    def check_permission(self):
        return self.check_role("administrador")


class Editar(endpoints.EditEndpoint[Sexo]):
    class Meta:
        verbose_name = "Editar Sexo"

    def check_permission(self):
        return self.check_role("administrador")


class Excluir(endpoints.DeleteEndpoint[Sexo]):
    class Meta:
        verbose_name = "Excluir Sexo"
