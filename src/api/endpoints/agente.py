from slth import endpoints
from ..models import *


class Agentes(endpoints.ListEndpoint[Agente]):
    class Meta:
        verbose_name = 'Agentes de Endemias'

    def get(self):
        return (
            super().get()
            .actions('agente.visualizar', 'agente.editar', 'agente.excluir')
        )
    
    def check_permission(self):
        return self.check_role('administrador')


class Cadastrar(endpoints.AddEndpoint[Agente]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Agente de Endemias'

    def get(self):
        return (
            super().get()
        )
    
    def check_permission(self):
        return self.check_role("administrador", "gm", "supervisor")

        
class Visualizar(endpoints.ViewEndpoint[Agente]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Agente de Endemias'

    def check_permission(self):
        return self.check_role('administrador')


class Editar(endpoints.EditEndpoint[Agente]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Agente de Endemias'

    def check_permission(self):
        return self.check_role('administrador')


class Excluir(endpoints.DeleteEndpoint[Agente]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Agente de Endemias'


class Desvincular(endpoints.InstanceEndpoint[Agente]):
    class Meta:
        icon = 'minus'
        verbose_name = 'Desvincular'

    def get(self):
        return self.formfactory().fields().info('Ao confirmar o agente será desvinculado do município.')
    
    def check_permission(self):
        return self.check_role("administrador", "gm", "supervisor")
    
    def post(self):
        self.instance.municipio_set.first().agentes.remove(self.instance)
        return super().post()
