from slth import endpoints
from ..models import *


class SinaisExtravasamentoPlasma(endpoints.ListEndpoint[SinalExtravasamentoPlasma]):
    class Meta:
        verbose_name = 'Sinais de Extravasamento do Plasma'

    def get(self):
        return (
            super().get()
            .actions('sinalextravasamentoplasma.cadastrar', 'sinalextravasamentoplasma.visualizar', 'sinalextravasamentoplasma.editar', 'sinalextravasamentoplasma.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[SinalExtravasamentoPlasma]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Sinal de Extravasamento do Plasma'

    def get(self):
        return (
            super().get()
        )

        
class Visualizar(endpoints.ViewEndpoint[SinalExtravasamentoPlasma]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Sinal de Extravasamento do Plasma'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[SinalExtravasamentoPlasma]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Sinal de Extravasamento do Plasma'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[SinalExtravasamentoPlasma]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Sinal de Extravasamento do Plasma'

    def get(self):
        return (
            super().get()
        )

