from slth import endpoints
from ..models import *


class SemanasEpidemiologicas(endpoints.ListEndpoint[SemanaEpidemiologica]):
    class Meta:
        verbose_name = 'Semanas Epidemiológicas'

    def get(self):
        return (
            super().get()
            .actions('semanaepidemiologica.cadastrar', 'semanaepidemiologica.visualizar', 'semanaepidemiologica.editar', 'semanaepidemiologica.excluir')
        )
    
    def check_permission(self):
        return self.check_role("administrador")


class Cadastrar(endpoints.AddEndpoint[SemanaEpidemiologica]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Semana Epidemiológica'

    def get(self):
        return (
            super().get()
        )
    
    def check_permission(self):
        return self.check_role("administrador")

        
class Visualizar(endpoints.ViewEndpoint[SemanaEpidemiologica]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Semana Epidemiológica'

    def get(self):
        return (
            super().get()
        )
    
    def check_permission(self):
        return self.check_role("administrador")
    

class Editar(endpoints.EditEndpoint[SemanaEpidemiologica]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Semana Epidemiológica'

    def get(self):
        return (
            super().get()
        )
    
    def check_permission(self):
        return self.check_role("administrador")


class Excluir(endpoints.DeleteEndpoint[SemanaEpidemiologica]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Semana Epidemiológica'

    def get(self):
        return (
            super().get()
        )
    
    def check_permission(self):
        return self.check_role("administrador")

