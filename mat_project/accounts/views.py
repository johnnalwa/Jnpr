import json
from django.shortcuts import render
from django.shortcuts import redirect, render
from django.views.generic import CreateView
from .models import *
from .forms import *
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .decorators import *
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render, get_object_or_404
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
import datetime
from .models import Attendance, Client, Commission, Sale
from .forms import AttendanceForm, ClientForm, LoginForm, RoutePlanForm, SaleForm 
import calendar
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver
import channels.layers
from django.contrib import messages





def update_commissions():
    current_month = datetime.date.today().month
    sales_for_current_month = Sale.objects.filter(date_paid__month=current_month)
    
    allowances = {
        (0, 19000): 0,
        (20000, 100000): 1500,
        (101000, 200000): 4000,
        (201000, 250000): 10000,
        (251000, 550000): 12000,
        (551000, 850000): 15000,
    }

    for sale in sales_for_current_month:
        total_amount_paid = sale.loan_amount_paid
        allowance = 0

        for amount_range, allowance_value in allowances.items():
            if amount_range[0] <= total_amount_paid <= amount_range[1]:
                allowance = allowance_value

        commission = (total_amount_paid * Decimal('0.05')) + Decimal(allowance)
        sale.commission = commission
        sale.save()

def login(request):
    form = LoginForm
    context = {
        'form': form
    }
    return render(request, 'login.html', context)


class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_member:
                return reverse('member_dashboard')
            elif user.is_management:
                return reverse('management_dashboard')
            
        else:
            return reverse('login')
        


class RegisterMemberView(CreateView):
    model = User
    form_class = MemberSignUpForm
    template_name = 'member/register.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'member'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        #login(self.request, user)
        return redirect('login')
  
    
class RegisterManagementView(CreateView):
    model = User
    form_class = ManagementSignUpForm
    template_name = 'management/register.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'management'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        #login(self.request, user)
        return redirect('login')
    
@login_required
@member_required
def MemberDashboard(request):
   # Call the update_commissions function to update commissions first
    update_commissions()

    # Retrieve the logged-in user's commission for the current month
    current_user = request.user
    current_month = datetime.date.today().month
    user_commission = Sale.objects.filter(agent=current_user, date_paid__month=current_month).aggregate(total=Sum('commission'))['total'] or 0

    # Count the total number of clients for the current user
    total_clients = Client.objects.filter(user=current_user).count()

    # Retrieve the routes for the currently logged-in user
    user_routes = RoutePlan.objects.filter(user=current_user)

    return render(request, 'member/dashboard.html', {
        'commission': user_commission,
        'total_clients': total_clients,
        'user_routes': user_routes  # Pass the user's routes to the template
    })
    

@login_required
@management_required
def ManagementDashboard(request):
    current_user = request.user
    total_clients = Client.objects.filter(user=current_user).count()
   
    return render(request, 'management/dashboard.html', {
        'total_clients': total_clients,
    })


@login_required
@management_required
def add_sale(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sales')
    else:
        form = SaleForm()
    return render(request, 'management/add_sale.html', {'form': form})

def display_sales(request):
    sales = Sale.objects.all()
    return render(request, 'management/display_sales.html', {'sales': sales})

def monthly_sales(request):
    monthly_totals = Sale.objects.annotate(
        month=TruncMonth('date_paid')
    ).values('month').annotate(total_amount_paid=Sum('loan_amount_paid')).order_by('month')

    return render(request, 'member/monthly_sales.html', {'monthly_totals': monthly_totals})



@login_required
def monthly_sales(request):
    current_user = request.user  # Get the currently logged-in user

    monthly_totals = Sale.objects.filter(agent=current_user).annotate(
        month=TruncMonth('date_paid')
    ).values('month').annotate(total_amount_paid=Sum('loan_amount_paid')).order_by('month')

    # Define allowances for different ranges of total amount paid
    allowances = {
        (0, 19000): 0,
        (20000, 100000): 1500,
        (101000, 200000): 4000,
        (201000, 250000): 10000,
        (251000, 550000): 12000,
        (551000, 850000): 15000,
    }

    # Calculate and update the commission for each sale
    for entry in monthly_totals:
        total_amount_paid = entry['total_amount_paid']
        for amount_range, allowance in allowances.items():
            if amount_range[0] <= total_amount_paid <= amount_range[1]:
                commission = (total_amount_paid * Decimal('0.05')) + Decimal(allowance)
                entry['commission'] = commission

    return render(request, 'member/monthly_sales.html', {'monthly_totals': monthly_totals})


@login_required
def add_client(request):
    total_clients = Client.objects.count()  # Get the count of clients
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.user = request.user
            client.save()
            return redirect('success_page')
        
    else:
        form = ClientForm()

    return render(request, 'member/add_client.html', {'form': form, 'total_clients': total_clients})


def calendar_view(request):
    # Create a calendar object
    cal = calendar.HTMLCalendar(calendar.SUNDAY)

    # Generate the HTML for the current month's calendar
    html_calendar = cal.formatmonth(2023, 10)

    # You can customize the year and month as needed
    # Replace 2023 and 10 with the desired year and month values

    return render(request, 'member/record_attendance.html', {'calendar': html_calendar})

@login_required
def record_attendance(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            user = request.user
            date = datetime.date.today()
            latitude = form.cleaned_data['latitude']
            longitude = form.cleaned_data['longitude']
            timestamp = datetime.datetime.now()

            try:
                Attendance.objects.create(user=user, date=date, location=f"({latitude}, {longitude})", latitude=latitude, longitude=longitude, timestamp=timestamp)
                # Display a JavaScript alert
                return render(request, 'member/record_attendance.html', {'form': form, 'success_message': 'Attendance recorded successfully!'})
            except Exception as e:
                error_message = f"Error occurred: {str(e)}"
                return render(request, 'member/record_attendance.html', {'form': form, 'error_message': error_message})
    else:
        form = AttendanceForm()

    return render(request, 'member/record_attendance.html', {'form': form})

def success_view(request):
    return render(request, 'member/success.html')

@login_required
def user_clients(request):
    # Display clients added by the currently logged-in user
    clients = Client.objects.filter(user=request.user)
    return render(request, 'member/user_clients.html', {'clients': clients})

@login_required
@management_required
def client_list_view(request):
    clients = Client.objects.all()
    context = {'clients': clients}
    return render(request, 'management/client_list.html', context)

def client_details(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'member/client_details.html', {'client': client})

def attendance_success(request):
    return render(request, 'attendance_success.html')

def charts(request):
    return render(request, 'member/chats.html')

def commission_page(request):
    # Retrieve the agent's commission and sales data
    agent = request.user
    commission = Commission.objects.get(agent=agent)
    sales = Sale.objects.filter(agent=agent)

    return render(request, 'member/commission_page.html', {'commission': commission, 'sales': sales})

@login_required
@management_required
def create_route_plan(request):
    if request.method == 'POST':
        form = RoutePlanForm(request.POST)
        if form.is_valid():
            route_plan = form.save(commit=False)
            route_plan.user = request.user
            route_plan.save()
            return redirect('create_route_plan')

    else:
        form = RoutePlanForm()

    return render(request, 'management/create_route_plan.html', {'form': form})

@receiver(post_save, sender=RoutePlan)
def send_notification_to_agent(sender, instance, **kwargs):
    # Get the agent associated with the route plan
    agent_username = instance.agent

    # Find the agent user object
    agent_user = User.objects.get(username=agent_username)

    # Send a notification to the agent using Django Channels
    channel_layer = channels.layers.get_channel_layer()

    async def send_notification():
        message = {
            'type': 'notification',
            'content': f'A new route plan has been created by {instance.user.username}.',
        }
        await channel_layer.group_send(f"agent_{agent_user.id}", {
            'type': 'send_notification',
            'message': json.dumps(message),
        })

    # Make the function asynchronous and run it in the event loop
    async_to_sync(send_notification)()

def get_notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')[:5]
        return {'notifications': notifications}
    return {}


@login_required
def client_list(request):
    # Filter clients based on the currently logged-in user
    clients = Client.objects.filter(user=request.user)
     

    # Select phone number, full name, and ministry
    client_data = clients.values('phone_number', 'client_fullname', 'ministry')

    return render(request, 'member/contacts.html', {'client_data': client_data})


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = MemberUpdateForm(request.POST, request.FILES, instance=request.user.member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('update_profile')
        else:
            messages.error(request, 'Error updating profile. Please check the form.')
    else:
        form = MemberUpdateForm(instance=request.user.member)

    return render(request, 'member/update_profile.html', {'form': form})