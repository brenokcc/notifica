from slth import endpoints
from ..models import *


class SinaisSangramentoGrave(endpoints.ListEndpoint[SinalSangramentoGrave]):
    class Meta:
        verbose_name = "Sinais de Sangramento Grave"

    def get(self):
        return (
            super()
            .get()
            .actions(
                "sinalsangramentograve.cadastrar",
                "sinalsangramentograve.visualizar",
                "sinalsangramentograve.editar",
                "sinalsangramentograve.excluir",
            )
        )

    def check_permission(self):
        return self.check_role("administrador")


class Cadastrar(endpoints.AddEndpoint[SinalSangramentoGrave]):
    class Meta:
        icon = "plus"
        verbose_name = "Cadastrar Sinal de Sangramento Grave"


class Visualizar(endpoints.ViewEndpoint[SinalSangramentoGrave]):
    class Meta:
        modal = False
        icon = "eye"
        verbose_name = "Visualizar Sinal de Sangramento Grave"

    def check_permission(self):
        return self.check_role("administrador")


class Editar(endpoints.EditEndpoint[SinalSangramentoGrave]):
    class Meta:
        icon = "pen"
        verbose_name = "Editar Sinal de Sangramento Grave"

    def check_permission(self):
        return self.check_role("administrador")


class Excluir(endpoints.DeleteEndpoint[SinalSangramentoGrave]):
    class Meta:
        icon = "trash"
        verbose_name = "Excluir Sinal de Sangramento Grave"
