from slth import endpoints
from ..models import *


class PeriodosGestacao(endpoints.ListEndpoint[PeriodoGestacao]):
    class Meta:
        verbose_name = 'Períodos de Gestação'

    def get(self):
        return (
            super().get()
            .actions('periodogestacao.cadastrar', 'periodogestacao.editar', 'periodogestacao.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[PeriodoGestacao]):
    class Meta:
        verbose_name = 'Cadastrar Período de Gestação'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[PeriodoGestacao]):
    class Meta:
        verbose_name = 'Editar Período de Gestação'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[PeriodoGestacao]):
    class Meta:
        verbose_name = 'Excluir Período de Gestação'

    def get(self):
        return (
            super().get()
        )

