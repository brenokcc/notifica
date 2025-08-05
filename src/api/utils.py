import os
import requests
from .models import Estado, Municipio
from slth.integrations import viacep


def buscar_endereco(cep, **chaves):
    endereco = {}
    if cep:
        dados = viacep.consultar(cep)
        sigla, nome, codigo = dados["uf"], dados["estado"], dados["ibge"][0:2]
        estado = Estado.objects.get_or_create(
            sigla=sigla, defaults=dict(codigo=codigo, nome=nome)
        )[0]
        nome, codigo = dados["localidade"], dados["ibge"]
        municipio = Municipio.objects.filter(codigo=codigo).first()
        if municipio is None:
            municipio = Municipio.objects.get_or_create(
                estado=estado, codigo=codigo, nome=nome
            )[0]
        endereco.update(
            bairro=dados["bairro"], logradouro=dados["logradouro"], municipio=municipio
        )
        for k, v in chaves.items():
            endereco[v] = endereco.pop(k, None)
    return endereco
