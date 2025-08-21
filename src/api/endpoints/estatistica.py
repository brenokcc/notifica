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
            "validada",
        ).bi(
            ("get_total", "get_total_notificantes", "get_total_pacientes"),
            ("get_total_por_unidade", "get_total_por_sexo"),
            "get_mapa",
        )

    def check_permission(self):
        return self.check_role("administrador", "gu", "gm")
