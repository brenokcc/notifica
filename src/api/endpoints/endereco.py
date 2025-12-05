from slth import endpoints
from ..models import *


class Enderecos(endpoints.ListEndpoint[Endereco]):
    class Meta:
        verbose_name = 'Endereços'

    def get(self):
        return (
            super().get()
            .actions('endereco.cadastrar', 'endereco.visualizar', 'endereco.editar', 'endereco.excluir')
        )
    
    def check_permission(self):
        return self.check_role('administrador')


class Cadastrar(endpoints.AddEndpoint[Endereco]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Endereço'

    def check_permission(self):
        return self.check_role('administrador')

        
class Visualizar(endpoints.ViewEndpoint[Endereco]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Endereço'

    def check_permission(self):
        return self.check_role('administrador')
    

class Editar(endpoints.EditEndpoint[Endereco]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Endereço'

    def check_permission(self):
        return self.check_role('administrador')


class Excluir(endpoints.DeleteEndpoint[Endereco]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Endereço'

