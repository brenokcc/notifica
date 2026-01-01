from slth import endpoints
from ..models import *


class Municipios(endpoints.ListEndpoint[Municipio]):
    class Meta:
        verbose_name = "Municípios"

    def get(self):
        return (
            super()
            .get()
            .actions("municipio.visualizar", "municipio.cadastrar", "municipio.editar", "municipio.excluir")
        )

    def check_permission(self):
        return self.check_role("administrador", "gm", "supervisor")
    
    def contribute(self, entrypoint):
        if entrypoint == 'menu':
            return not self.check_role('gm', 'supervisor', superuser=False)
        return super().contribute(entrypoint)


class Cadastrar(endpoints.AddEndpoint[Municipio]):
    class Meta:
        verbose_name = "Cadastrar Município"

    def check_permission(self):
        return self.check_role("notificante", "administrador")


class Visualizar(endpoints.ViewEndpoint[Municipio]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Município'

    def get(self):
        return (
            super().get()
        )
    
    def check_permission(self):
        return self.check_role("gm", "administrador", "supervisor")


class Editar(endpoints.EditEndpoint[Municipio]):
    class Meta:
        verbose_name = "Editar Município"

    def check_permission(self):
        return self.check_role("administrador", "gm")


class Excluir(endpoints.DeleteEndpoint[Municipio]):
    class Meta:
        verbose_name = "Excluir Município"


class AdicionarAgente(endpoints.InstanceEndpoint[Municipio]):
    agente = endpoints.forms.ModelChoiceField(Agente.objects, label="Agente")
    
    class Meta:
        icon = 'plus'
        verbose_name = "Vincular Agente de Endemia"

    def get(self):
        return super().formfactory().fields('agente:agente.cadastrar')

    def check_permission(self):
        return self.check_role("administrador", "gm", "supervisor")
    
    def post(self):
        self.instance.agentes.add(self.cleaned_data['agente'])
        return super().post()
    
    def get_agente_queryset(self, queryset):
        return queryset.nolookup()


