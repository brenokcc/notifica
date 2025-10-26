from slth import endpoints
from ..models import *


class Agentes(endpoints.ListEndpoint[Agente]):
    class Meta:
        verbose_name = 'Agentes'

    def get(self):
        return (
            super().get()
            .actions('agente.cadastrar', 'agente.visualizar', 'agente.editar', 'agente.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[Agente]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Agente'

    def get(self):
        return (
            super().get()
        )

        
class Visualizar(endpoints.ViewEndpoint[Agente]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Agente'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[Agente]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Agente'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[Agente]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Agente'

    def get(self):
        return (
            super().get()
        )

