from slth import endpoints
from ..models import *


class Municipios(endpoints.ListEndpoint[Municipio]):
    class Meta:
        verbose_name = 'Municípios'

    def get(self):
        return (
            super().get()
            .actions('municipio.cadastrar', 'municipio.editar', 'municipio.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[Municipio]):
    class Meta:
        verbose_name = 'Cadastrar Município'

    def get(self):
        return (
            super().get()
        )
    
    def check_permission(self):
        return self.check_role('notificante')
    

class Editar(endpoints.EditEndpoint[Municipio]):
    class Meta:
        verbose_name = 'Editar Município'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[Municipio]):
    class Meta:
        verbose_name = 'Excluir Município'

    def get(self):
        return (
            super().get()
        )

