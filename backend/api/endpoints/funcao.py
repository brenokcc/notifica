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


class Cadastrar(endpoints.AddEndpoint[Funcao]):
    class Meta:
        verbose_name = 'Cadastrar Função'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[Funcao]):
    class Meta:
        verbose_name = 'Editar Função'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[Funcao]):
    class Meta:
        verbose_name = 'Excluir Função'

    def get(self):
        return (
            super().get()
        )

