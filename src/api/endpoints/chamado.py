from slth import endpoints
from ..models import *


class Chamados(endpoints.ListEndpoint[Chamado]):
    class Meta:
        verbose_name = 'Chamados'

    def get(self):
        return (
            super().get()
            .actions('chamado.cadastrar', 'chamado.visualizar', 'chamado.classificar', 'chamado.atender', 'chamado.excluir')
        )
    
    def check_permission(self):
        return self.request.user.is_authenticated
    
    def get_queryset(self):
        if self.check_role('administrador'):
            return super().get_queryset()
        return super().get_queryset().filter(usuario=self.request.user)


class Cadastrar(endpoints.AddEndpoint[Chamado]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Abrir Chamado'

    def get(self):
        return super().get().fields('descricao').values(usuario=self.request.user)
    
    def check_permission(self):
        return self.request.user.is_authenticated

        
class Visualizar(endpoints.ViewEndpoint[Chamado]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Chamado'

    def check_permission(self):
        return self.check_role('administrador')
    

class Editar(endpoints.EditEndpoint[Chamado]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Chamado'

    def check_permission(self):
        return self.check_role('administrador')


class Excluir(endpoints.DeleteEndpoint[Chamado]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Chamado'

    def check_permission(self):
        return self.check_role('administrador')



class Classificar(endpoints.InstanceEndpoint[Chamado]):
    class Meta:
        verbose_name = 'Classificar'

    def get(self):
        return self.formfactory(self.instance).fields('classificacao')

    def check_permission(self):
        return self.check_role('administrador')


class Atender(endpoints.InstanceEndpoint[Chamado]):
    class Meta:
        verbose_name = 'Atender'

    def get(self):
        return self.formfactory(self.instance).values(atendente=self.request.user).fields('atendente', 'resolvido', 'observacao')

    def check_permission(self):
        return self.check_role('administrador')
    
