import requests
from slth.models import Role
from slth import endpoints
from datetime import date, timedelta
from ..models import *
from ..utils import buscar_endereco
from slth.integrations.google import places
from slth.utils import age
from slth.components import FileViewer
from requests.exceptions import Timeout
from django.core.cache import cache

from ..exportacao import CAMPOS

class NotificacoesIndividuais(endpoints.QuerySetEndpoint[NotificacaoIndividual]):
    class Meta:
        icon = "file-export"
        verbose_name = "Exportar Notificações Individuais"

    def get(self):
        return (
            super()
            .get()
            .lookup("administrador")
            .lookup("gu", unidade__gestores__cpf='username')
            .lookup("gm", unidade__municipio__gestores__cpf='username')
            .fields('numero', 'doenca', 'unidade', "notificante", "data", "cpf", "nome")
            .xlsx(*CAMPOS)
            .order_by("-numero")
        )

    def check_permission(self):
        return self.check_role("administrador", "gu", "gm")
