from slth import endpoints
from ..models import *


class GestoresMunicipais(endpoints.ListEndpoint[GestorMunicipal]):
    class Meta:
        verbose_name = 'Gestores Municipais'

    def get(self):
        return (
            super().get()
            .actions('gestormunicipal.cadastrar', 'gestormunicipal.visualizar', 'gestormunicipal.editar', 'gestormunicipal.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[GestorMunicipal]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Gestor de Municipal'

    def get(self):
        return (
            super().get()
        )

        
class Visualizar(endpoints.ViewEndpoint[GestorMunicipal]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Gestor de Municipal'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[GestorMunicipal]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Gestor de Municipal'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[GestorMunicipal]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Gestor de Municipal'

    def get(self):
        return (
            super().get()
        )

