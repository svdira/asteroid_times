from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
	path('', views.homepage, name='homepage'),
	path('add-item/', views.addItem, name='addItem'),
	path('edit-item/<i>', views.editItem, name='editItem'),
	path('item/<i>', views.item, name='item'),
	]