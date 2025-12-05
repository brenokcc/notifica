from slth import endpoints
from ..models import *
from datetime import datetime


class TermosUso(endpoints.ListEndpoint[TermoUso]):
    class Meta:
        verbose_name = 'Termos de Uso'

    def get(self):
        return (
            super().get()
            .actions('termouso.cadastrar', 'termouso.visualizar', 'termouso.editar', 'termouso.excluir')
        )


class Cadastrar(endpoints.AddEndpoint[TermoUso]):
    class Meta:
        icon = 'plus'
        verbose_name = 'Cadastrar Termo de Uso'

    def get(self):
        return (
            super().get()
        )

        
class Visualizar(endpoints.ViewEndpoint[TermoUso]):
    class Meta:
        modal = False
        icon = 'eye'
        verbose_name = 'Visualizar Termo de Uso'

    def get(self):
        return (
            super().get()
        )
    

class Editar(endpoints.EditEndpoint[TermoUso]):
    class Meta:
        icon = 'pen'
        verbose_name = 'Editar Termo de Uso'


class Excluir(endpoints.DeleteEndpoint[TermoUso]):
    class Meta:
        icon = 'trash'
        verbose_name = 'Excluir Termo de Uso'


class Checar(endpoints.Endpoint):
    def get(self):
        self.redirect('/app/termouso/aceitar/')
        return {}

    def check_permission(self):
        return self.request.user.is_authenticated and not TermoUso.objects.filter(user=self.request.user, aceito=True).exists()


class Aceitar(endpoints.Endpoint):
    
    class Meta:
        modal = False
        verbose_name = "Termo de Uso"
        submit_label = 'Aceitar termo e continuar'
        submit_icon = 'thumbs-up'

    def get(self):
        termo_uso = TermoUso.objects.get_or_create(user=self.request.user, defaults=dict(aceito=False))[0]
        return self.formfactory(termo_uso).fields().display(None, ('get_termo_consentimento_digital',))
    
    def post(self):
        termo_uso = TermoUso.objects.get(user=self.request.user)
        termo_uso.aceito = True
        termo_uso.data_assinatura = datetime.now()
        termo_uso.save()
        self.redirect('/app/dashboard/')
    
    def check_permission(self):
        return self.request.user.is_authenticated
