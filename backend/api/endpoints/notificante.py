from slth import endpoints
from ..models import *


class Notificantes(endpoints.ListEndpoint[Notificante]):
    class Meta:
        verbose_name = 'Notificantes'

    def get(self):
        return (
            super().get()
            .actions('notificante.cadastrar', 'notificante.editar', 'notificante.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[Notificante]):
    class Meta:
        verbose_name = 'Cadastrar Notificante'

    def get(self):
        return (
            super().get()
        )
    
    def check_permission(self):
        return self.check_role('regulador')
    

class Editar(endpoints.EditEndpoint[Notificante]):
    class Meta:
        verbose_name = 'Editar Notificante'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[Notificante]):
    class Meta:
        verbose_name = 'Excluir Notificante'

    def get(self):
        return (
            super().get()
        )

