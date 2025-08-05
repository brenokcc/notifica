from slth import endpoints
from ..models import *


class SinaisComprometimentoOrgaos(endpoints.ListEndpoint[SinalComprometimentoOrgao]):
    class Meta:
        verbose_name = "Sinais de Comprometimento dos Órgãos"

    def get(self):
        return (
            super()
            .get()
            .actions(
                "sinalcomprometimentoorgao.cadastrar",
                "sinalcomprometimentoorgao.visualizar",
                "sinalcomprometimentoorgao.editar",
                "sinalcomprometimentoorgao.excluir",
            )
        )

    def check_permission(self):
        return self.check_role("administrador")


class Cadastrar(endpoints.AddEndpoint[SinalComprometimentoOrgao]):
    class Meta:
        icon = "plus"
        verbose_name = "Cadastrar Sinal de Comprometimento dos Órgãos"

    def check_permission(self):
        return self.check_role("administrador")


class Visualizar(endpoints.ViewEndpoint[SinalComprometimentoOrgao]):
    class Meta:
        modal = False
        icon = "eye"
        verbose_name = "Visualizar Sinal de Comprometimento dos Órgãos"

    def check_permission(self):
        return self.check_role("administrador")


class Editar(endpoints.EditEndpoint[SinalComprometimentoOrgao]):
    class Meta:
        icon = "pen"
        verbose_name = "Editar Sinal de Comprometimento dos Órgãos"

    def check_permission(self):
        return self.check_role("administrador")


class Excluir(endpoints.DeleteEndpoint[SinalComprometimentoOrgao]):
    class Meta:
        icon = "trash"
        verbose_name = "Excluir Sinal de Comprometimento dos Órgãos"
