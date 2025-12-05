from slth import endpoints
from slth.components import TemplateContent
from api.models import CategoriaVideo

class QuemSomos(endpoints.PublicEndpoint):
    
    class Meta:
        icon = "info-circle"
        modal = False
        verbose_name = "Quem somos"

    def get(self):
        return TemplateContent("quemsomos.html", locals())
    
    def check_permission(self):
        return not self.request.user.is_authenticated


class videos(endpoints.PublicEndpoint):
    
    class Meta:
        icon = "display"
        modal = False
        verbose_name = "Videos"

    def get(self):
        categorias = CategoriaVideo.objects.all()
        return TemplateContent("videos.html", locals())
    
    def check_permission(self):
        return not self.request.user.is_authenticated
