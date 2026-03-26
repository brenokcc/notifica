from slth import endpoints
from datetime import timedelta, date
from ..models import NotificacaoIndividual


class Painel(endpoints.PublicEndpoint):

    class Meta:
        icon = "map-marked"
        verbose_name = "Painel de Monitoramento"

    def get(self):
        if not self.request.GET:
            self.request.GET._mutable = True
            self.request.GET.update(data__gte=(date.today() - timedelta(days=7)).strftime('%Y-%m-%d'))
            self.request.GET._mutable = False
        return NotificacaoIndividual.objects.all().filter(data_envio__isnull=False).filters(
            "doenca", "municipio", "unidade", "unidade_referencia", "notificante", "status", "status_infeccao", "validada", "tipo_bloqueio", "situacao_hospitalar", "data__lte", "data__gte", "data_primeiros_sintomas__lte", "data_nascimento__gte", "data_nascimento__lte", "data_primeiros_sintomas__gte", "registrado_sinan", "semana_epidemiologica"
        ).bi(
            ("get_total", "get_total_notificantes", "get_total_pacientes"),
            ("get_total_por_unidade", "get_total_por_sexo"),
            "get_mapa",
            "get_total_por_bairro",
        )

    def check_permission(self):
        return self.check_role("administrador", "gm",  "regulador", "ru", "agente", "supervisor", "gu", "notificante")
