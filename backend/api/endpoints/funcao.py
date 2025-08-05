from slth import endpoints
from ..models import *


class Funcoes(endpoints.ListEndpoint[Funcao]):
    class Meta:
        verbose_name = 'Funções'

    def get(self):
        return (
            super().get()
            .actions('funcao.cadastrar', 'funcao.editar', 'funcao.excluir')
        )
    
    def check_permission(self):
        return self.check_role('administrador')


class Cadastrar(endpoints.AddEndpoint[Funcao]):
    class Meta:
        verbose_name = 'Cadastrar Função'

    def check_permission(self):
        return self.check_role('administrador')
    

class Editar(endpoints.EditEndpoint[Funcao]):
    class Meta:
        verbose_name = 'Editar Função'

    def check_permission(self):
        return self.check_role('administrador')


class Excluir(endpoints.DeleteEndpoint[Funcao]):
    class Meta:
        verbose_name = 'Excluir Função'

