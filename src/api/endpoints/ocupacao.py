from slth import endpoints
from ..models import *


class Ocupacoes(endpoints.ListEndpoint[Ocupacao]):
    class Meta:
        verbose_name = "Ocupações"

    def get(self):
        return (
            super()
            .get()
            .actions("ocupacao.cadastrar", "ocupacao.editar", "ocupacao.excluir")
        )


class Cadastrar(endpoints.AddEndpoint[Ocupacao]):
    class Meta:
        verbose_name = "Cadastrar Ocupação"

    def check_permission(self):
        return self.check_role("administrador", "notificante")


class Editar(endpoints.EditEndpoint[Ocupacao]):
    class Meta:
        verbose_name = "Editar Ocupação"

    def check_permission(self):
        return self.check_role("administrador")


class Excluir(endpoints.DeleteEndpoint[Ocupacao]):
    class Meta:
        verbose_name = "Excluir Ocupação"
