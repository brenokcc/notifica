from slth import endpoints
from ..models import *


class Apresentacoesclinicas(endpoints.ListEndpoint[ApresentacaoClinica]):
    class Meta:
        verbose_name = 'Apresentações Clínicas'

    def get(self):
        return (
            super().get()
            .actions('apresentacaoclinica.cadastrar', 'apresentacaoclinica.visualizar', 'apresentacaoclinica.editar', 'apresentacaoclinica.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[ApresentacaoClinica]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Apresentação Clínica'

    def get(self):
        return (
            super().get()
        )

        
class Visualizar(endpoints.ViewEndpoint[ApresentacaoClinica]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Apresentação Clínica'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[ApresentacaoClinica]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Apresentação Clínica'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[ApresentacaoClinica]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Apresentação Clínica'

    def get(self):
        return (
            super().get()
        )

