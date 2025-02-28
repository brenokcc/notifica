from slth import endpoints
from ..models import *


class Ocupacoes(endpoints.ListEndpoint[Ocupacao]):
    class Meta:
        verbose_name = 'Ocupações'

    def get(self):
        return (
            super().get()
            .actions('ocupacao.cadastrar', 'ocupacao.editar', 'ocupacao.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[Ocupacao]):
    class Meta:
        verbose_name = 'Cadastrar Ocupação'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[Ocupacao]):
    class Meta:
        verbose_name = 'Editar Ocupação'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[Ocupacao]):
    class Meta:
        verbose_name = 'Excluir Ocupação'

    def get(self):
        return (
            super().get()
        )

