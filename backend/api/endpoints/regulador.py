from slth import endpoints
from ..models import *


class Reguladores(endpoints.ListEndpoint[Regulador]):
    class Meta:
        verbose_name = 'Reguladores'

    def get(self):
        return (
            super().get()
            .actions('regulador.cadastrar', 'regulador.visualizar', 'regulador.editar', 'regulador.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[Regulador]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Regulador'

    def get(self):
        return (
            super().get()
        )

        
class Visualizar(endpoints.ViewEndpoint[Regulador]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Regulador'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[Regulador]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Regulador'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[Regulador]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Regulador'

    def get(self):
        return (
            super().get()
        )

