from slth import endpoints
from ..models import *


class Escolaridades(endpoints.ListEndpoint[Escolaridade]):
    class Meta:
        verbose_name = 'Escolaridades'

    def get(self):
        return (
            super().get()
            .actions('escolaridade.cadastrar', 'escolaridade.editar', 'escolaridade.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[Escolaridade]):
    class Meta:
        verbose_name = 'Cadastrar Escolaridade'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[Escolaridade]):
    class Meta:
        verbose_name = 'Editar Escolaridade'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[Escolaridade]):
    class Meta:
        verbose_name = 'Excluir Escolaridade'

    def get(self):
        return (
            super().get()
        )

