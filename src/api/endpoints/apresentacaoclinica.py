from slth import endpoints
from ..models import *


class Apresentacoesclinicas(endpoints.ListEndpoint[ApresentacaoClinica]):
    class Meta:
        verbose_name = "Apresentações Clínicas"

    def get(self):
        return (
            super()
            .get()
            .actions(
                "apresentacaoclinica.cadastrar",
                "apresentacaoclinica.visualizar",
                "apresentacaoclinica.editar",
                "apresentacaoclinica.excluir",
            )
        )

    def check_permission(self):
        return self.check_role("administrador")


class Cadastrar(endpoints.AddEndpoint[ApresentacaoClinica]):
    class Meta:
        icon = "plus"
        verbose_name = "Cadastrar Apresentação Clínica"

    def check_permission(self):
        return self.check_role("administrador")


class Visualizar(endpoints.ViewEndpoint[ApresentacaoClinica]):
    class Meta:
        modal = False
        icon = "eye"
        verbose_name = "Visualizar Apresentação Clínica"

    def check_permission(self):
        return self.check_role("administrador")


class Editar(endpoints.EditEndpoint[ApresentacaoClinica]):
    class Meta:
        icon = "pen"
        verbose_name = "Editar Apresentação Clínica"

    def check_permission(self):
        return self.check_role("administrador")


class Excluir(endpoints.DeleteEndpoint[ApresentacaoClinica]):
    class Meta:
        icon = "trash"
        verbose_name = "Excluir Apresentação Clínica"
