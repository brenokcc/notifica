from django.urls import path, re_path, include
from slth import urls
from django.conf import settings
from slth.views import dispatcher, index, service_worker, media
from django.conf.urls.static import static
from .views import consultar_cpf

urlpatterns = [
    path("", index),
    path("service-worker.js", service_worker),
    re_path(r"^app/(?P<path>.*)/$", index),
    path("api/", include(urls)),
    path("", dispatcher),
    path("media/<path:file_path>/", media, name="secure_media"),
    path("consultar_cpf/<str:cpf>/", consultar_cpf, name="consulta_cpf"),
]
