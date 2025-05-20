from slth import endpoints
from ..models import *


class Gestores(endpoints.ListEndpoint[Gestor]):
    class Meta:
        verbose_name = 'Gestores'

    def get(self):
        return (
            super().get()
            .actions('gestor.cadastrar', 'gestor.visualizar', 'gestor.editar', 'gestor.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[Gestor]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Gestor'

    def get(self):
        return (
            super().get()
        )

        
class Visualizar(endpoints.ViewEndpoint[Gestor]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Gestor'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[Gestor]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Gestor'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[Gestor]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Gestor'

    def get(self):
        return (
            super().get()
        )

