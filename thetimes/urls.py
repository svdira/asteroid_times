from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
	path('', views.homepage, name='homepage'),
	path('add-item/', views.addItem, name='addItem'),
	path('edit-item/<i>', views.editItem, name='editItem'),
	path('item/<i>', views.item, name='item'),
	path('category/<c>', views.categoria, name='categoria'),
	path('start-consumo/<i>', views.startConsumo, name='startConsumo'),
	path('book-history/', views.bookHistory, name='bookHistory'),
	path('book-queue/', views.bookQueue, name='bookQueue'),
	path('related-items/<item>', views.relatedItems, name='relatedItems'),
	]