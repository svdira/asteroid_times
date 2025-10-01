from django.contrib import admin
from .models import *

admin.site.register(Category)
admin.site.register(Item)
admin.site.register(AttrItem)
admin.site.register(AttrImage)
admin.site.register(AttrDate)
admin.site.register(AttrInteger)
admin.site.register(AttrText)

