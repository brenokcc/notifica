from slth import endpoints
from slth.components import TemplateContent

class QuemSomos(endpoints.PublicEndpoint):
    
    class Meta:
        icon = "info-circle"
        modal = False
        verbose_name = "Quem somos"

    def get(self):
        return TemplateContent("quemsomos.html", locals())
    
    def check_permission(self):
        return not self.request.user.is_authenticated
