from slth import endpoints
from ..models import *


class SinaisClinicos(endpoints.ListEndpoint[SinalClinico]):
    class Meta:
        verbose_name = "Sinais Clínicos"

    def get(self):
        return (
            super()
            .get()
            .actions(
                "sinalclinico.cadastrar", "sinalclinico.editar", "sinalclinico.excluir"
            )
        )

    def check_permission(self):
        return self.check_role("administrador")


class Cadastrar(endpoints.AddEndpoint[SinalClinico]):
    class Meta:
        verbose_name = "Cadastrar Sinal Clínico"

    def check_permission(self):
        return self.check_role("administrador")


class Editar(endpoints.EditEndpoint[SinalClinico]):
    class Meta:
        verbose_name = "Editar Sinal Clínico"

    def check_permission(self):
        return self.check_role("administrador")


class Excluir(endpoints.DeleteEndpoint[SinalClinico]):
    class Meta:
        verbose_name = "Excluir Sinal Clínico"
