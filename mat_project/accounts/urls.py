from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('',views.login, name="login"),
    path('login/', views.LoginView.as_view(), name="user_login"),
    path('logout/', auth_views.LogoutView.as_view(template_name="logout.html"), name="logout"),
    
    path('member/dashboard/',views.MemberDashboard, name="member_dashboard"),
    path('member/register/',views.RegisterMemberView.as_view(), name="register_member"),
    
    
    path('management/dashboard/',views.ManagementDashboard, name="management_dashboard"),
    path('management/register/',views.RegisterManagementView.as_view(), name="register_management"),
path('add_client/', views.add_client, name='add_client'),
    path('success/', views.success_view, name='success_page'),
    path('success/', views.attendance_success, name='attendance_success'),  
    
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('attendance/', views.record_attendance, name='record_attendance'),
    
    path('user-clients/', views.user_clients, name='user_clients'),
    # path('admin-clients/', views.admin_clients, name='admin_clients'),
    path('client/<int:pk>/', views.client_details, name='client_details'),
    path('charts/', views.charts, name='charts_page'),

    # path('add_sales/', views.enter_client_data, name='enter_client_data'),
    # path('agent-page/<int:agent_id>/', views.agent_page, name='agent_page'),
    # path('add-sale/', views.add_sale, name='add_sale'),
    path('commission/', views.commission_page, name='commission_page'),
    
    path('add_sale/', views.add_sale, name='add_sale'),
    path('sales/', views.display_sales, name='sales'),
    path('monthly_sales/', views.monthly_sales, name='monthly_sales'),
    # path('monthly_commissions/', views.monthly_commissions, name='monthly_commissions'),
    
   path('create_route_plan/', views.create_route_plan, name='create_route_plan'),
   path('contacts/', views.client_list, name='contacts_list'),
]
