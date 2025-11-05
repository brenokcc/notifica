from slth import endpoints
from ..models import *


class Municipios(endpoints.ListEndpoint[Municipio]):
    class Meta:
        verbose_name = "Municípios"

    def get(self):
        return (
            super()
            .get()
            .actions("municipio.cadastrar", "municipio.editar", "municipio.excluir")
        )

    def check_permission(self):
        return self.check_role("administrador", "gm")
    
    def contribute(self, entrypoint):
        if entrypoint == 'menu':
            return not self.check_role('gm', superuser=False)
        return super().contribute(entrypoint)


class Cadastrar(endpoints.AddEndpoint[Municipio]):
    class Meta:
        verbose_name = "Cadastrar Município"

    def check_permission(self):
        return self.check_role("notificante", "administrador")


class Editar(endpoints.EditEndpoint[Municipio]):
    class Meta:
        verbose_name = "Editar Município"

    def check_permission(self):
        return self.check_role("administrador", "gm")


class Excluir(endpoints.DeleteEndpoint[Municipio]):
    class Meta:
        verbose_name = "Excluir Município"
