import os
import json
from django.conf import settings
from slth import endpoints
from slth.components import GeoMap
from ..models import NotificacaoIndividual


SAMPLE = [
    (-22.2191, -54.8056),
    (-22.2245, -54.7987),
    (-22.2132, -54.8123),
    (-22.2301, -54.7998),
    (-22.2178, -54.8074),
    (-22.2215, -54.8029),
    (-22.2156, -54.8092),
    (-22.2283, -54.8041),
    (-22.2199, -54.8005),
    (-22.2237, -54.8108),
    (-22.2164, -54.8033),
    (-22.2269, -54.7976),
    (-22.2125, -54.8067),
    (-22.2294, -54.8012),
    (-22.2182, -54.8089),
    (-22.2207, -54.7991),
    (-22.2143, -54.8115),
    (-22.2276, -54.8027),
    (-22.2169, -54.8008),
    (-22.2221, -54.8050),
    (-22.2137, -54.7983),
    (-22.2252, -54.8096),
    (-22.2173, -54.8021),
    (-22.2290, -54.8078),
    (-22.2150, -54.8045),
    (-22.2212, -54.7999),
    (-22.2129, -54.8102),
    (-22.2280, -54.8003),
    (-22.2187, -54.8060),
    (-22.2241, -54.8037)
]


class Geovisualizacao(endpoints.PublicEndpoint):

    class Meta:
        icon = "map-marked"
        verbose_name = "Geovisualização"

    def get(self):
        map = GeoMap(zoom=10.2, max_zoom=13, min_zoom=10, title="Geovisualização")
        with open(os.path.join(settings.BASE_DIR, "api", "dourados.json")) as file:
            features = json.loads(file.read()).get('features')
            for feature in features:
                feature["properties"]["info"] = feature["properties"]["ubsf"]
                map.add_polygon_feature(feature)
            for notificacao in NotificacaoIndividual.objects.all():
                map.add_point(-54.808435280682374, -22.252012218991808, notificacao)
            for x, y in SAMPLE:
                map.add_point(y, x, "Notificação 00001 - UBS Campo do Lago II (01/01/2025)")
            return map
    