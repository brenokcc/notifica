from slth import endpoints
from ..models import *


class Sinaisalarme(endpoints.ListEndpoint[SinalAlarme]):
    class Meta:
        verbose_name = 'Sinais de Alarme'

    def get(self):
        return (
            super().get()
            .actions('sinalalarme.cadastrar', 'sinalalarme.visualizar', 'sinalalarme.editar', 'sinalalarme.excluir')
        )
    
    def check_permission(self):
        return self.check_role('administrador')


class Cadastrar(endpoints.AddEndpoint[SinalAlarme]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Sinal de Alarme'

    def check_permission(self):
        return self.check_role('administrador')

        
class Visualizar(endpoints.ViewEndpoint[SinalAlarme]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Sinal de Alarme'

    def check_permission(self):
        return self.check_role('administrador')
    

class Editar(endpoints.EditEndpoint[SinalAlarme]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Sinal de Alarme'

    def check_permission(self):
        return self.check_role('administrador')


class Excluir(endpoints.DeleteEndpoint[SinalAlarme]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Sinal de Alarme'

