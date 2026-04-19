from slth import endpoints
from ..models import *
from slth.serializer import serialize
from django.conf import settings


class Fila(endpoints.Endpoint):

    def get(self):
        return [
            {k:serialize(v) for k, v in x.items()} for x in 
            NotificacaoIndividual.objects
            .filter(status_infeccao='Positivo', doenca=2, unidade_referencia__codigo=self.request.GET['cnes'], data_obito__isnull=True)
            .values('nome', 'cpf', 'cartao_sus', 'sexo__nome', 'data_nascimento', 'email', 'telefone', 'ocupacao_investigacao__nome', 'ocupacao_investigacao__codigo', 'data_primeiros_sintomas', 'resumo_clinico')
            .order_by('data_primeiros_sintomas')
        ]
    
    def check_permission(self):
        if 'HTTP_AUTHORIZATION' in self.request.META:
            token = self.request.META['HTTP_AUTHORIZATION'].split()[1]
            return token == settings.SECRET_KEY[-20:]
        return False
