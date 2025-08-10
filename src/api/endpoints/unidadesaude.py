from slth import endpoints
from ..models import *


class UnidadesSaude(endpoints.ListEndpoint[UnidadeSaude]):
    class Meta:
        verbose_name = "Unidades de Saúde"

    def get(self):
        return (
            super()
            .get()
            .actions(
                "unidadesaude.visualizar", "unidadesaude.cadastrar", "unidadesaude.editar", "unidadesaude.excluir"
            )
        )

    def check_permission(self):
        return self.check_role("regulador", "administrador", "gm", "gu")


class Visualizar(endpoints.ViewEndpoint[UnidadeSaude]):
    class Meta:
        modal = False
        verbose_name = "Visualizar Unidade de Saúde"

    def check_permission(self):
        return self.check_role("regulador", "administrador", "gm", "gu")


class Cadastrar(endpoints.AddEndpoint[UnidadeSaude]):
    class Meta:
        verbose_name = "Cadastrar Unidade de Saúde"

    def check_permission(self):
        return self.check_role("regulador", "administrador", "gm")
    
    def get_municipio_queryset(self, queryset):
        return queryset.lookup("gm", gestores__cpf="username")


class Editar(endpoints.EditEndpoint[UnidadeSaude]):
    class Meta:
        icon = 'pencil'
        verbose_name = "Editar Unidade de Saúde"

    def check_permission(self):
        return self.check_role("regulador", "administrador", "gm")


class Excluir(endpoints.DeleteEndpoint[UnidadeSaude]):
    class Meta:
        verbose_name = "Excluir Unidade de Saúde"


class AddEquipe(endpoints.RelationEndpoint[Equipe]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Adicionar Equipe'
    
    def formfactory(self):
        return (
            super()
            .formfactory().fields(unidade=self.source)
            .fieldset("Dados Gerais", ("unidade", ("codigo", "nome"), "notificantes:notificante.cadastrar"))
        )
