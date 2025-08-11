from slth import endpoints
from ..models import *


class Editar(endpoints.EditEndpoint[Equipe]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Equipe'
        
    def check_permission(self):
        return self.check_role("regulador", "administrador", "gm", "gu") and self.check_instance()


class Excluir(endpoints.DeleteEndpoint[Equipe]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Equipe'


