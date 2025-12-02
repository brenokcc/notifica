from slth import endpoints
from ..models import *


class Supervisores(endpoints.ListEndpoint[Supervisor]):
    class Meta:
        verbose_name = 'Supervisores de Endemia'

    def get(self):
        return (
            super().get()
            .actions('supervisor.cadastrar', 'supervisor.visualizar', 'supervisor.editar', 'supervisor.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[Supervisor]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Supervisor de Endemia'

    def check_permission(self):
        return self.check_role("administrador", "gm")


class Visualizar(endpoints.ViewEndpoint[Supervisor]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Supervisor de Endemia'

    def check_permission(self):
        return self.check_role('administrador')


class Editar(endpoints.EditEndpoint[Supervisor]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Supervisor de Endemia'

    def check_permission(self):
        return self.check_role('administrador')


class Excluir(endpoints.DeleteEndpoint[Supervisor]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Supervisor de Endemia'

