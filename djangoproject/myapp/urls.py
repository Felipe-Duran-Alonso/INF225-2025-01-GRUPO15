from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name="index"),
    path('registro/', views.registro, name='registro'),
    path('requerimientos/', views.requerimientos, name='requerimientos'),
    path('ver_requerimientos/', views.get_requerimiento, name='ver_requerimientos'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('cerrar_sesion/', views.cerrar_sesion, name="cerrar_sesion"),
    path('ver_boletines/', views.ver_boletines, name="ver_boletines"),
    path('editar_boletines/', views.editar_boletines, name="editar_boletines"),
    path('subir_boletines/', views.subir_boletines, name="subir_boletines"),
    path('editar_requerimientos/', views.editar_requerimientos, name="editar_requerimientos"),
    path('modificar_configuraciones/', views.modificar_configuraciones, name="modificar_configuraciones"),
    path('estadisticas_boletines/', views.estadisticas_boletines, name="estadisticas_boletines"),
    path('administrar_fuentes/', views.administrar_fuentes, name="administrar_fuentes"),
    path('resumir_texto/', views.resumir_texto, name="resumir_texto"),
    path('revisar_resumen/', views.revisar_resumen, name="revisar_resumen")
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)