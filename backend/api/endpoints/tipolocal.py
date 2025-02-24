from slth import endpoints
from ..models import *


class TiposLocal(endpoints.ListEndpoint[TipoLocal]):
    class Meta:
        verbose_name = 'Tipos de Locais'

    def get(self):
        return (
            super().get()
            .actions('tipolocal.cadastrar', 'tipolocal.editar', 'tipolocal.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[TipoLocal]):
    class Meta:
        verbose_name = 'Cadastrar Tipo de Local'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[TipoLocal]):
    class Meta:
        verbose_name = 'Editar Tipo de Local'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[TipoLocal]):
    class Meta:
        verbose_name = 'Excluir Tipo de Local'

    def get(self):
        return (
            super().get()
        )

