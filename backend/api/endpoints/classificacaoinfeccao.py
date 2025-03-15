from slth import endpoints
from ..models import *


class Classificacoesinfeccao(endpoints.ListEndpoint[ClassificacaoInfeccao]):
    class Meta:
        verbose_name = 'Classificações de Infecção'

    def get(self):
        return (
            super().get()
            .actions('classificacaoinfeccao.cadastrar', 'classificacaoinfeccao.visualizar', 'classificacaoinfeccao.editar', 'classificacaoinfeccao.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[ClassificacaoInfeccao]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Classificação de Infecção'

    def get(self):
        return (
            super().get()
        )

        
class Visualizar(endpoints.ViewEndpoint[ClassificacaoInfeccao]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Classificação de Infecção'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[ClassificacaoInfeccao]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Classificação de Infecção'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[ClassificacaoInfeccao]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Classificação de Infecção'

    def get(self):
        return (
            super().get()
        )

