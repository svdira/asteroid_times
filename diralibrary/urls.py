from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
	path('add-persona/', views.addPersona, name='addpersona'),
	path('persona/<persona_id>', views.persona, name='persona'),
	path('edit-persona/<persona_id>', views.editPersona, name='editPersona'),
	path('add-titulo/', views.addTitulo, name='addTitulo'),
	path('titulo/<titulo_id>', views.titulo, name='titulo'),
	path('comenzar/<titulo_id>', views.comenzar, name='comenzar'),
	path('inicio/', views.inicio, name='inicio'),
	path('cola/', views.cola, name='cola'),
	path('terminar/', views.terminarLectura, name='terminar'),
	path('comentar/', views.aggNota, name='comentar'),
	path('agg-credito/<titulo>', views.aggCredito, name='aggCredito'),
	path('nota/<nota>/<tipo>', views.editNota, name='editNota'),
	path('perfiles/', views.perfiles, name='perfiles'),
]