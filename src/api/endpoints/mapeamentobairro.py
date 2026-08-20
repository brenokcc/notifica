from slth import endpoints
from ..models import *


class MapeamentoBairros(endpoints.ListEndpoint[MapeamentoBairro]):
    class Meta:
        verbose_name = 'Mapeamento de Bairros'

    def get(self):
        return (
            super().get().search('nome').filters('bairro')
            .actions('mapeamentobairro.cadastrar', 'mapeamentobairro.visualizar', 'mapeamentobairro.editar', 'mapeamentobairro.excluir')
        )

    def check_permission(self):
        return self.check_role('administrador')


class Cadastrar(endpoints.AddEndpoint[MapeamentoBairro]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Mapeamento de Bairro'

    def get(self):
        return (
            super().get()
        )

    def check_permission(self):
        return self.check_role('administrador')

        
class Visualizar(endpoints.ViewEndpoint[MapeamentoBairro]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Mapeamento de Bairro'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[MapeamentoBairro]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Mapeamento de Bairro'

    def get(self):
        return (
            super().get().fieldset('Dados Gerais', ('bairro',))
        )

    def check_permission(self):
        return self.check_role('administrador')


class Excluir(endpoints.DeleteEndpoint[MapeamentoBairro]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Mapeamento de Bairro'

    def get(self):
        return (
            super().get()
        )

    def check_permission(self):
        return self.check_role('administrador')


class Pendentes(endpoints.QuerySetEndpoint[MapeamentoBairro]):
    class Meta:
        modal = False
        icon = "bell"
        verbose_name = "Mapeamentos de bairro pendentes"

    def get_queryset(self):
        return super().get_queryset().pendentes().search('nome').actions('mapeamentobairro.editar')

    def check_permission(self):
        return self.check_role('administrador')
