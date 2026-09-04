from slth import endpoints
from ..models import *


class Bairros(endpoints.ListEndpoint[Bairro]):
    class Meta:
        verbose_name = 'Bairros'

    def get(self):
        return (
            super().get().search('nome', 'codigo').filters('municipio')
            .actions('bairro.cadastrar', 'bairro.visualizar', 'bairro.editar', 'bairro.excluir')
        )

    def check_permission(self):
        return self.check_role('administrador')


class Cadastrar(endpoints.AddEndpoint[Bairro]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Bairro'

    def get(self):
        return (
            super().get()
        )

    def check_permission(self):
        return self.check_role('administrador')

        
class Visualizar(endpoints.ViewEndpoint[Bairro]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Bairro'

    def get(self):
        return (
            super().get()
        )

    def check_permission(self):
        return self.check_role('administrador')
    

class Editar(endpoints.EditEndpoint[Bairro]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Bairro'

    def get(self):
        return (
            super().get()
        )

    def check_permission(self):
        return self.check_role('administrador')


class Excluir(endpoints.DeleteEndpoint[Bairro]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Bairro'

    def get(self):
        return (
            super().get()
        )
