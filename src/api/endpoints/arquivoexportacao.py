from slth import endpoints
from ..models import *


class ArquivosExportacao(endpoints.ListEndpoint[ArquivoExportacao]):
    class Meta:
        verbose_name = 'Arquivos de Exportação'

    def get(self):
        return (
            super().get()
            .actions('arquivoexportacao.cadastrar', 'arquivoexportacao.visualizar', 'arquivoexportacao.editar', 'arquivoexportacao.excluir')
        )
    
    def check_permission(self):
        return self.check_role("notificante")


class Cadastrar(endpoints.AddEndpoint[ArquivoExportacao]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Gerar Arquivo de Exportação'

    def get(self):
        return (
            super().get()
        )
    
    def check_permission(self):
        return self.check_role("notificante")

        
class Visualizar(endpoints.ViewEndpoint[ArquivoExportacao]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Arquivo de Exportação'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[ArquivoExportacao]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Arquivo de Exportação'

    def get(self):
        return (
            super().get()
        )


class Excluir(endpoints.DeleteEndpoint[ArquivoExportacao]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Arquivo de Exportação'

    def get(self):
        return (
            super().get()
        )

