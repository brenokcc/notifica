from slth import endpoints
from ..models import *


class SolicitacoesCadastroNotificante(endpoints.ListEndpoint[SolicitacaoCadastroNotificante]):
    class Meta:
        verbose_name = 'Solicitações de Cadastro'

    def get(self):
        return (
            super().get().filters('aprovada')
            .actions('solicitacaocadastronotificante.cadastrar', 'solicitacaocadastronotificante.visualizar', 'solicitacaocadastronotificante.avaliar', 'solicitacaocadastronotificante.excluir')
        )
    
    def check_permission(self):
        return self.check_role('gu')


class Cadastrar(endpoints.AddEndpoint[SolicitacaoCadastroNotificante]):
    class Meta:
        icon = 'user-plus'
        verbose_name = 'Cadastrar Solicitação de Cadastro'

    def get(self):
        return (
            super().get()
        )
    
    def check_permission(self):
        return not self.request.user.is_authenticated

        
class Visualizar(endpoints.ViewEndpoint[SolicitacaoCadastroNotificante]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Solicitação de Cadastro'


class Avaliar(endpoints.InstanceEndpoint[SolicitacaoCadastroNotificante]):
    class Meta:
        icon = 'check'
        verbose_name = 'Avaliar'

    def get(self):
        return (
            super().formfactory().fields('aprovada', 'observacao')
        )
    
    def post(self):
        self.instance.save()
        self.instance.processar()
        return super().post()
    
    def check_permission(self):
        return self.check_role('gu')


class Excluir(endpoints.DeleteEndpoint[SolicitacaoCadastroNotificante]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Solicitação de Cadastro'


