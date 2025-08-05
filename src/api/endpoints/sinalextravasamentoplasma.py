from slth import endpoints
from ..models import *


class SinaisExtravasamentoPlasma(endpoints.ListEndpoint[SinalExtravasamentoPlasma]):
    class Meta:
        verbose_name = "Sinais de Extravasamento do Plasma"

    def check_permission(self):
        return self.check_role("administrador")


class Cadastrar(endpoints.AddEndpoint[SinalExtravasamentoPlasma]):
    class Meta:
        icon = "plus"
        verbose_name = "Cadastrar Sinal de Extravasamento do Plasma"

    def check_permission(self):
        return self.check_role("administrador")


class Visualizar(endpoints.ViewEndpoint[SinalExtravasamentoPlasma]):
    class Meta:
        modal = False
        icon = "eye"
        verbose_name = "Visualizar Sinal de Extravasamento do Plasma"

    def check_permission(self):
        return self.check_role("administrador")


class Editar(endpoints.EditEndpoint[SinalExtravasamentoPlasma]):
    class Meta:
        icon = "pen"
        verbose_name = "Editar Sinal de Extravasamento do Plasma"

    def check_permission(self):
        return self.check_role("administrador")


class Excluir(endpoints.DeleteEndpoint[SinalExtravasamentoPlasma]):
    class Meta:
        icon = "trash"
        verbose_name = "Excluir Sinal de Extravasamento do Plasma"
