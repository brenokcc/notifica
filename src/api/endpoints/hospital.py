from slth import endpoints
from ..models import *


class Hospitais(endpoints.ListEndpoint[Hospital]):
    class Meta:
        verbose_name = "Hospitais"

    def get(self):
        return (
            super()
            .get()
            .actions("hospital.cadastrar", "hospital.editar", "hospital.excluir")
        )

    def check_permission(self):
        return self.check_role("regulador", "administrador")


class Cadastrar(endpoints.AddEndpoint[Hospital]):
    class Meta:
        verbose_name = "Cadastrar Hospital"

    def check_permission(self):
        return self.check_role("regulador", "administrador")


class Editar(endpoints.EditEndpoint[Hospital]):
    class Meta:
        verbose_name = "Editar Hospital"

    def check_permission(self):
        return self.check_role("regulador", "administrador")


class Excluir(endpoints.DeleteEndpoint[Hospital]):
    class Meta:
        verbose_name = "Excluir Hospital"
