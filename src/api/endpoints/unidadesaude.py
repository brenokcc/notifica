import csv
from io import StringIO
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
                "unidadesaude.visualizar", "unidadesaude.cadastrar", "unidadesaude.editar", "unidadesaude.excluir", "unidadesaude.importar"
            )
        )

    def check_permission(self):
        return self.check_role("regulador", "administrador", "gm", "gu")


class Visualizar(endpoints.ViewEndpoint[UnidadeSaude]):
    class Meta:
        modal = False
        verbose_name = "Visualizar Unidade de Saúde"

    def check_permission(self):
        return self.check_role("regulador", "administrador", "gm", "gu") and self.check_instance()


class Cadastrar(endpoints.AddEndpoint[UnidadeSaude]):
    class Meta:
        verbose_name = "Cadastrar Unidade de Saúde"

    def check_permission(self):
        return self.check_role("administrador", "gm")
    
    def get_municipio_queryset(self, queryset):
        return queryset.lookup("gm", gestores__cpf="username")


class Editar(endpoints.EditEndpoint[UnidadeSaude]):
    class Meta:
        icon = 'pencil'
        verbose_name = "Editar Unidade de Saúde"

    def check_permission(self):
        return self.check_role("administrador", "gm") and self.check_instance()


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
            .fieldset("Dados Gerais", ("unidade", ("nome", "codigo"), "notificantes:notificante.cadastrar"))
        )

    def check_permission(self):
        return self.check_role("administrador", "gm")
    

class Importar(endpoints.Endpoint):
    arquivo = endpoints.forms.FileField(label="Arquivo CSV", extensions=["csv"])

    class Meta:
        icon = "upload"
        verbose_name = "Importar"

    def get(self):
        return self.formfactory().fields('arquivo')
    
    def post(self):
        content = StringIO(self.request.FILES['arquivo'].read().decode())
        for i, row in enumerate(csv.DictReader(content, delimiter=";")):
            municipio = Municipio.objects.filter(codigo=row["IBGE"]).first()
            cnes = row["CNES"]
            nome = row["NOME FANTASIA"]
            unidade = UnidadeSaude.objects.filter(codigo=cnes).first()
            if unidade is None:
                unidade = UnidadeSaude()
            unidade.codigo = cnes
            unidade.municipio = municipio
            unidade.nome = nome
            unidade.save()
        return super().post()
