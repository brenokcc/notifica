from slth import endpoints
from ..models import *


class Administradores(endpoints.ListEndpoint[Administrador]):
    class Meta:
        verbose_name = "Administradores"

    def get(self):
        return (
            super()
            .get()
            .actions(
                "administrador.cadastrar",
                "administrador.visualizar",
                "administrador.editar",
                "administrador.excluir",
            )
        )


class Cadastrar(endpoints.AddEndpoint[Administrador]):
    class Meta:
        icon = "plus"
        verbose_name = "Cadastrar Administrador"


class Visualizar(endpoints.ViewEndpoint[Administrador]):
    class Meta:
        modal = False
        icon = "eye"
        verbose_name = "Visualizar Administrador"


class Editar(endpoints.EditEndpoint[Administrador]):
    class Meta:
        icon = "pen"
        verbose_name = "Editar Administrador"


class Excluir(endpoints.DeleteEndpoint[Administrador]):
    class Meta:
        icon = "trash"
        verbose_name = "Excluir Administrador"
