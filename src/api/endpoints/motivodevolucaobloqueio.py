from slth import endpoints
from ..models import *


class MotivosDevolucaoBloqueio(endpoints.ListEndpoint[MotivoDevolucaoBloqueio]):
    class Meta:
        verbose_name = 'Motivos para Devolução de Bloqueio'

    def get(self):
        return super().get().actions('motivodevolucaobloqueio.cadastrar', 'motivodevolucaobloqueio.visualizar', 'motivodevolucaobloqueio.editar', 'motivodevolucaobloqueio.excluir')

    def check_permission(self):
        return self.check_role('administrador')


class Cadastrar(endpoints.AddEndpoint[MotivoDevolucaoBloqueio]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Motivo para Devolução de Bloqueio'

    def check_permission(self):
        return self.check_role('administrador')

        
class Visualizar(endpoints.ViewEndpoint[MotivoDevolucaoBloqueio]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Motivo para Devolução de Bloqueio'

    def check_permission(self):
        return self.check_role('administrador')
    

class Editar(endpoints.EditEndpoint[MotivoDevolucaoBloqueio]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Motivo para Devolução de Bloqueio'

    def check_permission(self):
        return self.check_role('administrador')


class Excluir(endpoints.DeleteEndpoint[MotivoDevolucaoBloqueio]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Motivo para Devolução de Bloqueio'
