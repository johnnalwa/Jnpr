from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.db import transaction
from .models import *
from django import forms
from django.contrib.auth import get_user_model


User = get_user_model()

class MemberSignUpForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control radius-30 ps-5"}), label=("Email"))
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control radius-30 ps-5"}), label=("Username"))
    password1 = forms.CharField(label=("Password"), widget=forms.PasswordInput(attrs={"class": "form-control radius-30 ps-5"}))
    password2 = forms.CharField(label=("Confirm Password"), widget=forms.PasswordInput(attrs={"class": "form-control radius-30 ps-5"}))

    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control radius-30 ps-5"}), label="First Name")
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control radius-30 ps-5"}), label="Last Name")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')
    
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_member = True
        if commit:
            user.save()
        client = Member.objects.create(user=user, first_name=self.cleaned_data.get('first_name'), last_name=self.cleaned_data.get('last_name'))
        return user
    


class ManagementSignUpForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control radius-30 ps-5"}), label=("Email"))
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control radius-30 ps-5"}), label=("Username"))
    password1 = forms.CharField(label=("Password"), widget=forms.PasswordInput(attrs={"class": "form-control radius-30 ps-5"}))
    password2 = forms.CharField(label=("Confirm Password"), widget=forms.PasswordInput(attrs={"class": "form-control radius-30 ps-5"}))

    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control radius-30 ps-5"}), label="First Name")
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control radius-30 ps-5"}), label="Last Name")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')
    
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_management = True
        if commit:
            user.save()
        personell = ManagementAdmin.objects.create(user=user, first_name=self.cleaned_data.get('first_name'), last_name=self.cleaned_data.get('last_name'))
        return user
    


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control radius-30 ps-5"}), label=("Username"))
    password = forms.CharField(label=("Password"), widget=forms.PasswordInput(attrs={"class": "form-control radius-30 ps-5"}))
   
class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'

def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        self.fields['pf_number'].widget.attrs['disabled'] = True
        self.fields['amount'].widget.attrs['disabled'] = True
        self.fields['comment'].widget.attrs['disabled'] = True
        self.fields['pf_number_conversion'].widget.attrs['disabled'] = True
        self.fields['password'].widget.attrs['disabled'] = True
        self.fields['amount_applied'].widget.attrs['disabled'] = True
        self.fields['date_field'].widget.attrs['disabled'] = True
        self.fields['type_loan_qualify'].widget.attrs['disabled'] = True
        self.fields['comment_conversion'].widget.attrs['disabled'] = True
        
class AttendanceForm(forms.Form):
    latitude = forms.CharField(widget=forms.HiddenInput())
    longitude = forms.CharField(widget=forms.HiddenInput())
    
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['agent', 'client_name', 'loan_amount_paid', 'date_paid']
        
        
class RoutePlanForm(forms.ModelForm):
    agent = forms.ModelChoiceField(queryset=User.objects.all().order_by('username'))

    class Meta:
        model = RoutePlan
        fields = ['date', 'agent', 'institution', 'location']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'agent': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 40%;'}),
            'institution': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 40%;'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 40%;'}),
        }
        
class MemberUpdateForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'physical_address', 'national_id',
                  'primary_phone_number', 'profile_img']