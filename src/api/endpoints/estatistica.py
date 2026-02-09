from slth import endpoints
from ..models import NotificacaoIndividual


class Painel(endpoints.PublicEndpoint):

    class Meta:
        icon = "map-marked"
        verbose_name = "Painel de Monitoramento"

    def get(self):
        return NotificacaoIndividual.objects.all().filter(data_envio__isnull=False).filters(
            "doenca",
            "unidade",
            "notificante",
            "sexo",
            "data_primeiros_sintomas__gte",
            "data_primeiros_sintomas__lte",
            "status",
            "status_infeccao",
        ).bi(
            ("get_total", "get_total_notificantes", "get_total_pacientes"),
            ("get_total_por_unidade", "get_total_por_sexo"),
            "get_mapa",
            "get_total_por_bairro",
        )

    def check_permission(self):
        return self.check_role("administrador", "gm",  "regulador", "ru", "agente", "supervisor", "gu", "notificante")
