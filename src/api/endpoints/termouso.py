from slth import endpoints
from ..models import TermoUso
from datetime import datetime


class Checar(endpoints.Endpoint):
    def get(self):
        self.redirect('/app/termouso/aceitar/')

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
        return super().post()
    
    def check_permission(self):
        return self.request.user.is_authenticated

    
