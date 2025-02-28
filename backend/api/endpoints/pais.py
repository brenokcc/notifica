from slth import endpoints
from ..models import *


class Paises(endpoints.ListEndpoint[Pais]):
    class Meta:
        verbose_name = 'País'

    def get(self):
        return (
            super().get()
            .actions('pais.cadastrar', 'pais.editar', 'pais.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[Pais]):
    class Meta:
        verbose_name = 'Cadastrar País'

    def get(self):
        return (
            super().get()
        )
    
    def check_permission(self):
        return self.check_role('notificante')
    

class Editar(endpoints.EditEndpoint[Pais]):
    class Meta:
        verbose_name = 'Editar País'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[Pais]):
    class Meta:
        verbose_name = 'Excluir País'

    def get(self):
        return (
            super().get()
        )

