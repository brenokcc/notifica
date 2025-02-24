from slth import endpoints
from ..models import *


class Sexos(endpoints.ListEndpoint[Sexo]):
    class Meta:
        verbose_name = 'Sexos'

    def get(self):
        return (
            super().get()
            .actions('sexo.cadastrar', 'sexo.editar', 'sexo.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[Sexo]):
    class Meta:
        verbose_name = 'Cadastrar Sexo'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[Sexo]):
    class Meta:
        verbose_name = 'Editar Raça'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[Sexo]):
    class Meta:
        verbose_name = 'Excluir Raça'

    def get(self):
        return (
            super().get()
        )

