import psutil
import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from .models import *
from .forms import *
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .decorators import *
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from decimal import Decimal
import calendar
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver
import channels.layers
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
import datetime  
from .utils import get_logged_in_users


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

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')  # Display login error message
        return super().form_invalid(form)

    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:
            users_info = get_logged_in_users()
            self.request.session['logged_in_users'] = users_info  # Store info in session

            if user.is_member:
                messages.success(self.request, 'Welcome to the member dashboard.')
                return reverse('member_dashboard')
            elif user.is_management:
                messages.success(self.request, 'Welcome to the management dashboard.')
                return reverse('management_dashboard')
        
        # Redirect unauthenticated users to the login page with an error message
        messages.error(self.request, 'You are not authenticated. Please log in.')
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

    # Retrieve monthly sales data for the line chart
    sales_data = get_monthly_sales_data(current_user)

    return render(request, 'member/dashboard.html', {
        'commission': user_commission,
        'total_clients': total_clients,
        'user_routes': user_routes,  # Pass the user's routes to the template
        'sales_data': sales_data,
    })

def get_monthly_sales_data(user):
    current_month = datetime.date.today().month
    sales = Sale.objects.filter(agent=user, date_paid__month=current_month).order_by('date_paid')

    labels = [sale.date_paid.strftime('%Y-%m-%d') for sale in sales]
    data = [sale.loan_amount_paid for sale in sales]

    return {'labels': labels, 'data': data}


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
            messages.success(request, 'Sale added successfully.')
            return redirect('add_sale')  # Redirect to clear the form after successful submission
    else:
        form = SaleForm()

    # Check if a sale_id is provided for deletion
    sale_id = request.POST.get('sale_id')
    if sale_id:
        try:
            sale_to_delete = Sale.objects.get(pk=sale_id)
            sale_to_delete.delete()
            messages.success(request, 'Sale deleted successfully.')
            return redirect('add_sale')

        except Sale.DoesNotExist:
            messages.error(request, 'Sale not found for deletion.')

    sales = Sale.objects.all()

    return render(request, 'management/add_sale.html', {'form': form, 'sales': sales})


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
            messages.success(request, 'Route created successfully!')
            return redirect('create_route_plan')

    else:
        form = RoutePlanForm()

    # Fetch all routes
    routes = RoutePlan.objects.all()

    return render(request, 'management/create_route_plan.html', {'form': form, 'routes': routes})


@login_required
@management_required
def delete_route_plan(request, route_id):
    route = get_object_or_404(RoutePlan, id=route_id)
    route.delete()
    messages.success(request, 'Route deleted successfully!')
    return redirect('create_route_plan')

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

@login_required
@member_required
def mark_attendance(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            user = request.user
            latitude = form.cleaned_data['latitude']
            longitude = form.cleaned_data['longitude']
            current_time = form.cleaned_data['time']
            current_date = timezone.now().date()  # Get the current date

            # Check if attendance record already exists for the current user and date
            if Attendance.objects.filter(user=user, date=current_date).exists():
                messages.error(request, 'Attendance for today has already been marked!')
            else:
                # Save attendance record to the database with timestamp and date
                Attendance.objects.create(user=user, latitude=latitude, longitude=longitude, time=current_time, date=current_date)

                # Display a success message
                messages.success(request, 'Attendance recorded successfully!')

            # Redirect to a different page or use the same page
            return redirect('mark_attendance')  # Change 'your_redirect_view_name' to the actual view name

    else:
        form = AttendanceForm()

    # Get the attendance records for the current user
    user = request.user
    attendance_records = Attendance.objects.filter(user=user).order_by('-date')

    return render(request, 'member/mark_attendance.html', {'form': form, 'attendance_records': attendance_records})



@login_required
@management_required
def display_attendance(request):
    # Query to get all distinct users and their latest attendance date
    user_attendance_dates = Attendance.objects.values('user').annotate(latest_date=models.Max('date'))

    # Collect attendance records for each user on their latest date
    attendance_records = []
    for record in user_attendance_dates:
        user_id = record['user']
        user = User.objects.get(pk=user_id)
        
        # Get the latest attendance record for the user
        latest_attendance = Attendance.objects.filter(user=user).first()

        if latest_attendance:
            attendance_records.append({
                'user': user.username,
                'time': latest_attendance.time,
                'latitude': latest_attendance.latitude,
                'longitude': latest_attendance.longitude,
            })

    # Pass the attendance records to the template
    context = {'attendance_records': attendance_records}
    return render(request, 'management/display_attendance.html', context)


# Decorator to check if the user is a superior user
def is_superior_user(user):
    return user.is_authenticated and user.is_management

@login_required
@user_passes_test(is_superior_user)
def view_all_clients(request):
    # Fetch all clients for all users
    all_clients = Client.objects.all()

    # You can customize this based on your requirements
    context = {'all_clients': all_clients}

    return render(request, 'management/view_all_clients.html', context)

    
def logged_in_users_info(request):
    # Fetch information about currently logged-in users
    users_info = get_logged_in_users()

    # Prepare data for rendering
    context = {
        'users_info': users_info
    }

    return render(request, 'logged_in_users_info.html', context)