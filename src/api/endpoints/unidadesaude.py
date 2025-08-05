from slth import endpoints
from ..models import *


class UnidadesSaude(endpoints.ListEndpoint[UnidadeSaude]):
    class Meta:
        verbose_name = "Unidades de Saúde"

    def get(self):
        return (
            super()
            .get()
            .actions(
                "unidadesaude.cadastrar", "unidadesaude.editar", "unidadesaude.excluir"
            )
        )

    def check_permission(self):
        return self.check_role("regulador", "administrador")


class Cadastrar(endpoints.AddEndpoint[UnidadeSaude]):
    class Meta:
        verbose_name = "Cadastrar Unidade de Saúde"

    def check_permission(self):
        return self.check_role("regulador", "administrador")


class Editar(endpoints.EditEndpoint[UnidadeSaude]):
    class Meta:
        verbose_name = "Editar Unidade de Saúde"

    def check_permission(self):
        return self.check_role("regulador", "administrador")


class Excluir(endpoints.DeleteEndpoint[UnidadeSaude]):
    class Meta:
        verbose_name = "Excluir Unidade de Saúde"
