from django.urls import path

from . import views

app_name = 'repartidores'

urlpatterns = [
    path('', views.lista_repartidores, name='lista'),
    path('crear/', views.crear_repartidor, name='crear'),
    path('<int:repartidor_id>/', views.detalle_repartidor, name='detalle'),
    path('<int:repartidor_id>/editar/', views.editar_repartidor, name='editar'),
    path('<int:repartidor_id>/eliminar/', views.eliminar_repartidor, name='eliminar'),
    path('<int:repartidor_id>/estado/', views.cambiar_estado, name='cambiar_estado'),
]
