from slth import endpoints
from ..models import *


class Racas(endpoints.ListEndpoint[Raca]):
    class Meta:
        verbose_name = 'Raças'

    def get(self):
        return (
            super().get()
            .actions('raca.cadastrar', 'raca.editar', 'raca.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[Raca]):
    class Meta:
        verbose_name = 'Cadastrar Raça'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[Raca]):
    class Meta:
        verbose_name = 'Editar Raça'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[Raca]):
    class Meta:
        verbose_name = 'Excluir Raça'

    def get(self):
        return (
            super().get()
        )

