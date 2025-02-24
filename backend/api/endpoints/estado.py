from slth import endpoints
from ..models import *


class Estados(endpoints.ListEndpoint[Estado]):
    class Meta:
        verbose_name = 'Estados'

    def get(self):
        return (
            super().get()
            .actions('estado.cadastrar', 'estado.editar', 'estado.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[Estado]):
    class Meta:
        verbose_name = 'Cadastrar Estado'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[Estado]):
    class Meta:
        verbose_name = 'Editar Estado'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[Estado]):
    class Meta:
        verbose_name = 'Excluir Estado'

    def get(self):
        return (
            super().get()
        )

