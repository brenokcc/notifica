from slth import endpoints
from ..models import *


class DoencasPreExistentes(endpoints.ListEndpoint[DoencaPreExistente]):
    class Meta:
        verbose_name = 'Doenças Pré-Existentes'

    def get(self):
        return (
            super().get()
            .actions('doencapreexistente.cadastrar', 'doencapreexistente.editar', 'doencapreexistente.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[DoencaPreExistente]):
    class Meta:
        verbose_name = 'Cadastrar Doença Pré-Existente'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[DoencaPreExistente]):
    class Meta:
        verbose_name = 'Editar Doença Pré-Existente'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[DoencaPreExistente]):
    class Meta:
        verbose_name = 'Excluir Doença Pré-Existente'

    def get(self):
        return (
            super().get()
        )

