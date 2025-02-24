from slth import endpoints
from ..models import *


class SinaisClinicos(endpoints.ListEndpoint[SinalClinico]):
    class Meta:
        verbose_name = 'Sinais Clínicos'

    def get(self):
        return (
            super().get()
            .actions('sinalclinico.cadastrar', 'sinalclinico.editar', 'sinalclinico.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[SinalClinico]):
    class Meta:
        verbose_name = 'Cadastrar Sinal Clínico'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[SinalClinico]):
    class Meta:
        verbose_name = 'Editar Sinal Clínico'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[SinalClinico]):
    class Meta:
        verbose_name = 'Excluir Sinal Clínico'

    def get(self):
        return (
            super().get()
        )

