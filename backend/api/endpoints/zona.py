from slth import endpoints
from ..models import *


class Zonas(endpoints.ListEndpoint[Zona]):
    class Meta:
        verbose_name = 'Zonas'

    def get(self):
        return (
            super().get()
            .actions('zona.cadastrar', 'zona.editar', 'zona.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[Zona]):
    class Meta:
        verbose_name = 'Cadastrar Zona'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[Zona]):
    class Meta:
        verbose_name = 'Editar Zona'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[Zona]):
    class Meta:
        verbose_name = 'Excluir Zona'

    def get(self):
        return (
            super().get()
        )

