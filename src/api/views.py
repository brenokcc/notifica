import os
from django.http.response import JsonResponse
from . import esus

def consultar_cpf(request, cpf):
    esus_api_token = 'Token {}'.format(os.environ.get('ESUS_API_TOKEN'))
    if request.META.get('HTTP_AUTHORIZATION') == esus_api_token:
        return JsonResponse(esus.consulta_cpf(cpf))
    else:
        return JsonResponse({})
