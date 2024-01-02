from django.contrib import admin
from .models import User, ManagementAdmin, Member, Client, Attendance, Sale, Commission, RoutePlan, Notification


# admin.py

from django.contrib import admin

admin.site.site_header = 'Matunda African Capital ADMIN PANEL'
admin.site.site_title = 'MATUNDA'
admin.site.index_title = 'MATUNDA AC ADMIN'

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_member', 'is_management')
    search_fields = ('username', 'email')

@admin.register(ManagementAdmin)
class ManagementAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'gender', 'national_id', 'telephone', 'created_at')
    search_fields = ('user__username', 'user__email', 'first_name', 'last_name', 'national_id')

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'physical_address', 'national_id', 'primary_phone_number', 'create_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'first_name', 'last_name', 'national_id')

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('client_fullname', 'id_number', 'phone_number', 'ministry', 'type', 'pf_number', 'amount', 'comment', 'date_field')
    search_fields = ('client_fullname', 'id_number', 'phone_number')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'latitude', 'longitude', 'time', 'date')
    search_fields = ('user__username', 'user__email')

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('agent', 'client_name', 'loan_amount_paid', 'date_paid', 'commission')
    search_fields = ('agent__username', 'agent__email', 'client_name')

@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('agent', 'commission_amount')
    search_fields = ('agent__username', 'agent__email')

@admin.register(RoutePlan)
class RoutePlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'agent', 'institution', 'location')
    search_fields = ('user__username', 'user__email', 'agent', 'institution', 'location')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'timestamp')
    search_fields = ('user__username', 'user__email', 'message')
