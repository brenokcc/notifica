from slth import endpoints
from ..models import *


class Criteriosconfirmacao(endpoints.ListEndpoint[CriterioConfirmacao]):
    class Meta:
        verbose_name = 'Critérios de Confirmação'

    def get(self):
        return (
            super().get()
            .actions('criterioconfirmacao.cadastrar', 'criterioconfirmacao.visualizar', 'criterioconfirmacao.editar', 'criterioconfirmacao.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[CriterioConfirmacao]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Critério de Confirmação'

    def get(self):
        return (
            super().get()
        )

        
class Visualizar(endpoints.ViewEndpoint[CriterioConfirmacao]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Critério de Confirmação'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[CriterioConfirmacao]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Critério de Confirmação'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[CriterioConfirmacao]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Critério de Confirmação'

    def get(self):
        return (
            super().get()
        )

