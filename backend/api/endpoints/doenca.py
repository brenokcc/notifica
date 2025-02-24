from slth import endpoints
from ..models import *


class Doencas(endpoints.ListEndpoint[Doenca]):

    def get(self):
        return (
            super().get()
            .actions('doenca.cadastrar', 'doenca.editar', 'doenca.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[Doenca]):
    class Meta:
        verbose_name = 'Cadastrar Cor'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[Doenca]):
    class Meta:
        verbose_name = 'Editar Doença'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[Doenca]):
    class Meta:
        verbose_name = 'Excluir Doença'

    def get(self):
        return (
            super().get()
        )
