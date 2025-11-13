from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
	path('', views.homepage, name='homepage'),
	path('add-item/', views.addItem, name='addItem'),
	path('search-page/', views.searchPage, name='searchPage'),
	path('add-child-item/<parent>', views.addChildItem, name='addChildItem'),
	path('edit-item/<i>', views.editItem, name='editItem'),
	path('item/<i>', views.item, name='item'),
	path('category/<c>', views.categoria, name='categoria'),
	path('start-consumo/<i>', views.startConsumo, name='startConsumo'),
	path('book-history/', views.bookHistory, name='bookHistory'),
	path('movie-history/', views.movieHistory, name='movieHistory'),
	path('movie-queue/', views.movieQueue, name='movieQueue'),
	path('book-queue/', views.bookQueue, name='bookQueue'),
	path('related-items/<item>', views.relatedItems, name='relatedItems'),
	path('print-html/<cid>', views.printHTML, name='printHTML'),
	path('add-contrato/<equipo>', views.addContrato, name='addContrato'),
	path('equipo/<equipo>', views.equipo, name='equipo'),
	path('liga/<liga>', views.liga, name='liga'),
	path('add-match/<liga>', views.addMatch, name='addMatch'),
	path('partido/<p>', views.partido, name='partido'),
	path('futbol/<p>', views.futbol, name='futbol'),
	path('reg-gol/', views.regGol, name='regGol'),
	path('add-teams/<liga>', views.addTeams, name='addTeams'),
	path('alineacion/<partido>/<equipo>', views.alineacion, name='alineacion'),
	path('journal/', views.journal, name='journal'),
	path('gallery/<item_id>', views.gallery, name='gallery'),
	path('photo/<photo_id>', views.photo, name='photo'),
	path('addtweet/', views.addTweet, name='addTweet'),
	]