from slth import endpoints
from ..models import *


class Motivosperdaprazobloqueio(endpoints.ListEndpoint[MotivoPerdaPrazoBloqueio]):
    class Meta:
        verbose_name = 'Motivos de Perda de Prazo de Bloqueio'

    def get(self):
        return (
            super().get()
            .actions('motivoperdaprazobloqueio.cadastrar', 'motivoperdaprazobloqueio.visualizar', 'motivoperdaprazobloqueio.editar', 'motivoperdaprazobloqueio.excluir')
        )
    
    def check_permission(self):
        return self.check_role('administrador')


class Cadastrar(endpoints.AddEndpoint[MotivoPerdaPrazoBloqueio]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Motivo de Perda de Prazo de Bloqueio'

    def check_permission(self):
        return self.check_role('administrador')
        
class Visualizar(endpoints.ViewEndpoint[MotivoPerdaPrazoBloqueio]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Motivo de Perda de Prazo de Bloqueio'

    def check_permission(self):
        return self.check_role('administrador')

class Editar(endpoints.EditEndpoint[MotivoPerdaPrazoBloqueio]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Motivo de Perda de Prazo de Bloqueio'

    def check_permission(self):
        return self.check_role('administrador')


class Excluir(endpoints.DeleteEndpoint[MotivoPerdaPrazoBloqueio]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Motivo de Perda de Prazo de Bloqueio'
