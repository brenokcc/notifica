from slth import endpoints
from ..models import *


class Videos(endpoints.ListEndpoint[Video]):
    class Meta:
        verbose_name = 'Videos'

    def get(self):
        return (
            super().get()
            .actions('video.cadastrar', 'video.visualizar', 'video.editar', 'video.excluir')
        )
    
    def check_permission(self):
        return self.check_role('administrador')


class Cadastrar(endpoints.AddEndpoint[Video]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Video'

    def check_permission(self):
        return self.check_role('administrador')

        
class Visualizar(endpoints.ViewEndpoint[Video]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Video'

    def check_permission(self):
        return self.check_role('administrador')
    

class Editar(endpoints.EditEndpoint[Video]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Video'

    def check_permission(self):
        return self.check_role('administrador')


class Excluir(endpoints.DeleteEndpoint[Video]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Video'

    def check_permission(self):
        return self.check_role('administrador')
