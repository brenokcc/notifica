from slth import endpoints
from ..models import *


class TiposEvolucao(endpoints.ListEndpoint[TipoEvolucao]):
    class Meta:
        verbose_name = 'Tipos de Evoluação'

    def get(self):
        return (
            super().get()
            .actions('tipoevolucao.cadastrar', 'tipoevolucao.visualizar', 'tipoevolucao.editar', 'tipoevolucao.excluir')
        )
    
    def check_permission(self):
        return self.check_role('administrador')


class Cadastrar(endpoints.AddEndpoint[TipoEvolucao]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Tipo de Evolução'

    def check_permission(self):
        return self.check_role('administrador')
        
class Visualizar(endpoints.ViewEndpoint[TipoEvolucao]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Tipo de Evolução'

    def check_permission(self):
        return self.check_role('administrador')
    

class Editar(endpoints.EditEndpoint[TipoEvolucao]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Tipo de Evolução'

    def check_permission(self):
        return self.check_role('administrador')


class Excluir(endpoints.DeleteEndpoint[TipoEvolucao]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Tipo de Evolução'
