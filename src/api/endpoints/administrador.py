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
    
    def check_permission(self):
        return self.check_role('administrador')


class Cadastrar(endpoints.AddEndpoint[Administrador]):
    class Meta:
        icon = "plus"
        verbose_name = "Cadastrar Administrador"

    def check_permission(self):
        return self.check_role('administrador')


class Visualizar(endpoints.ViewEndpoint[Administrador]):
    class Meta:
        modal = False
        icon = "eye"
        verbose_name = "Visualizar Administrador"

    def check_permission(self):
        return self.check_role('administrador')


class Editar(endpoints.EditEndpoint[Administrador]):
    class Meta:
        icon = "pen"
        verbose_name = "Editar Administrador"

    def check_permission(self):
        return self.check_role('administrador')


class Excluir(endpoints.DeleteEndpoint[Administrador]):
    class Meta:
        icon = "trash"
        verbose_name = "Excluir Administrador"

    def check_permission(self):
        return self.check_role('administrador')
