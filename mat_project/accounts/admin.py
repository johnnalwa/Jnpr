from django.contrib import admin
from django.contrib import admin
from .models import  Client, Attendance, Sale, Commission, RoutePlan


admin.site.register(Client)
admin.site.register(Attendance)
admin.site.register(Sale)
admin.site.register(Commission)
admin.site.register(RoutePlan)