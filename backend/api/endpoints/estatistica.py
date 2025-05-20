
from slth import endpoints
from ..models import NotificacaoIndividual


class Painel(endpoints.PublicEndpoint):

    class Meta:
        icon = "map-marked"
        verbose_name = "Painel de Monitoramento"
 
    def get(self):
        return (
            NotificacaoIndividual.objects
            .filters(
                'doenca', 'unidade', 'notificante', 'sexo', 'data_primeiros_sintomas__gte', 'data_primeiros_sintomas__lte', 'validada'
            )
            .bi(
                ('get_total', 'get_total_notificantes', 'get_total_pacientes'),
                ('get_total_por_unidade', 'get_total_por_sexo'),
                'get_mapa'
            )
        )