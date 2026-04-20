from django.contrib import admin
from .models import *

admin.site.register(Persona)
admin.site.register(Tipo)
admin.site.register(Titulo)
admin.site.register(MetaData)
admin.site.register(Credito)
admin.site.register(Consumo)
admin.site.register(Cubiertas)

admin.site.register(Comentario)