from slth import endpoints
from ..models import *


class Zonas(endpoints.ListEndpoint[Zona]):
    class Meta:
        verbose_name = 'Zonas'

    def get(self):
        return (
            super().get()
            .actions('zona.cadastrar', 'zona.editar', 'zona.excluir')
        )
    
    def check_permission(self):
        return self.check_role('administrador')


class Cadastrar(endpoints.AddEndpoint[Zona]):
    class Meta:
        verbose_name = 'Cadastrar Zona'
    
    def check_permission(self):
        return self.check_role('administrador')
    

class Editar(endpoints.EditEndpoint[Zona]):
    class Meta:
        verbose_name = 'Editar Zona'

    def check_permission(self):
        return self.check_role('administrador')


class Excluir(endpoints.DeleteEndpoint[Zona]):
    class Meta:
        verbose_name = 'Excluir Zona'
