from slth import endpoints
from ..models import *
from datetime import date, timedelta
from slth.serializer import serialize
from django.conf import settings


class Fila(endpoints.Endpoint):

    def get(self):
        return [
            {k:serialize(v) for k, v in x.items()} for x in 
            NotificacaoIndividual.objects
            # .filter(data_primeiros_sintomas__gte=date.today() - timedelta(days=15))
            .filter(status_infeccao='Positivo', doenca=2, unidade_referencia__codigo=self.request.GET['cnes'])
            .values('nome', 'cpf', 'cartao_sus', 'sexo__nome', 'data_nascimento', 'email', 'telefone', 'ocupacao_investigacao__nome')
            .order_by('data_primeiros_sintomas')
        ]
    
    def check_permission(self):
        if 'HTTP_AUTHORIZATION' in self.request.META:
            token = self.request.META['HTTP_AUTHORIZATION'].split()[1]
            return token == settings.SECRET_KEY[-20:]
        return False
