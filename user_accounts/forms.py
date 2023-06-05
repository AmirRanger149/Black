'''
Users Accounts form and fields
developer: #ABS
'''

# Import all requirements
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm, ReadOnlyPasswordHashField, AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate, login as DjangoLogin
from allauth.account.forms import SignupForm , ChangePasswordForm
from wagtail.users.forms import UserEditForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import UsernameField
from django.shortcuts import render, redirect
from .utils import validate_Opassword
from .models import user_accounts
from django.db.models import Q
from django import forms
  
   
# Custom User Creation Form class
class CustomUserCreationForm(SignupForm):
    phoneNumber = forms.CharField(
        label='شماره تماس',
        widget=forms.TextInput(attrs={'placeholder': 'شماره تماس به همراه صفر ابتدایی مانند :‌۰۹۱۲۱۲۳۴۵۶۷'})
    )
    password1 = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور'})
    )
    password2 = forms.CharField(
        label='تکرار رمز عبور',
        widget=forms.PasswordInput(attrs={'placeholder': 'تکرار رمز عبور'})
    )

    # اضافه کردن بررسی شماره تلفن
    def clean_phoneNumber(self):
        phoneNumber = self.cleaned_data.get("phoneNumber")

        # بررسی تعداد ارقام شماره تلفن
        if len(phoneNumber) != 11:
            raise forms.ValidationError("شماره تلفن باید ۱۱ رقم باشد مانند ۰۹۱۲۱۲۳۴۵۶۷")

        return phoneNumber


    class Meta:
        model = user_accounts
        fields = ('phoneNumber', 'password1', 'password2')
        exclude = ('email',)

    def clean_password2(self):
        # بررسی تطابق رمز عبور
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("رمز عبور وارد شده مطابقت ندارند")
        return password2

    def save(self, request):
        user = super().save(request)
        user.set_password(self.cleaned_data["password1"])
        user.save()
        return user


# Custom User authentication Form class
class LoginForm(AuthenticationForm):
    username = UsernameField(
        label='نام کاربری',
        widget=forms.TextInput(attrs={'placeholder': 'شماره تلفن / ایمل / نام کاربری'}))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # Check if user exists with username, email, or phone number
            try:
                user = user_accounts.objects.get(
                    Q(username=username) | Q(email=username) | Q(phoneNumber=username)
                )
            except user_accounts.DoesNotExist:
                raise forms.ValidationError('نام کاربری، ایمیل یا شماره تماس نامعتبر است')

            if user.has_new_password:
                auth = authenticate(request=self.request, username=username, password=password)
                if not auth:
                    raise forms.ValidationError('نام کاربری یا رمز عبور نامعتبر است')
                elif auth:
                    self.confirm_login_allowed(auth)
                    DjangoLogin(self.request, auth)
            else:
                WOPass = user.WPOPass
                is_valid_password = validate_Opassword(password, user.WPOPass)
                if is_valid_password:
                    user.has_new_password = True
                    new_password_hash = make_password(password, salt='PDHTwqLLv7nIsw60zr767s')
                    user.password = new_password_hash
                    user.save(update_fields=['password', 'has_new_password'])
                    user = authenticate(request=self.request, username=username, password=password)
                    self.confirm_login_allowed(user)
                    DjangoLogin(self.request, user)
                else:
                    raise forms.ValidationError('نام کاربری یا رمز عبور نامعتبر است')

            # Check if password is valid
            if not user.check_password(password):
                raise forms.ValidationError('نام کاربری یا رمز عبور نامعتبر است')

        return self.cleaned_data


# Custom User Change Form
class CustomUserChangeForm(UserChangeForm):
    email = forms.EmailField(label='ایمیل')
    username = forms.CharField(label='نام کاربری')
    full_name = forms.CharField(label='نام کامل')
    phoneNumber = forms.CharField(label='شماره تماس')
    is_active = forms.BooleanField(label='فعال', required=False)
    is_staff = forms.BooleanField(label='کارمند', required=False)
    date_joined = forms.DateTimeField(label='تاریخ عضویت', widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = user_accounts
        fields = ('email', 'username', 'full_name', 'phoneNumber', 'is_active', 'is_staff', 'date_joined')

    def clean_password(self):
        return self.initial["password"]
    

# Custom User Password Change Form
class CustomPasswordChangeForm(ChangePasswordForm):
    new_password1 = forms.CharField(
        label=_("رمز عبور جدید"),
        widget=forms.PasswordInput,
        strip=False,
        required=False,
    )
    new_password2 = forms.CharField(
        label=_("تأیید رمز عبور جدید"),
        strip=False,
        widget=forms.PasswordInput,
        required=False,
    )

    class Meta:
        model = user_accounts

    def clean(self):
        cleaned_data = super().clean()

        # بررسی اینکه کاربر جدید است و نیاز به رمز عبور قوی دارد
        if self.user.has_new_password:
            new_password1 = cleaned_data.get('new_password1')
            new_password2 = cleaned_data.get('new_password2')
            if not new_password1:
                raise forms.ValidationError(
                    _("شما باید یک رمز عبور جدید وارد کنید.")
                )
            if not validate_password(new_password1):
                raise forms.ValidationError(
                    _("رمز عبور باید حداقل ۸ کاراکتر باشد و شامل حروف بزرگ، حروف کوچک و اعداد باشد.")
                )
            if new_password1 != new_password2:
                raise forms.ValidationError(
                    _("دو فیلد رمز عبور با یکدیگر مطابقت ندارند.")
                )
        else:
            # بررسی اینکه کاربر تنها باید رمز عبور فعلی را تأیید کند
            old_password = cleaned_data.get('old_password')
            if not self.user.check_password(old_password):
                raise forms.ValidationError(
                    _("رمز عبور قدیمی شما به درستی وارد نشده است. لطفاً دوباره آن را وارد کنید.")
                )

            new_password1 = cleaned_data.get('new_password1')
            new_password2 = cleaned_data.get('new_password2')
            if new_password1 or new_password2:
                raise forms.ValidationError(
                    _("شما تنها می‌توانید رمز عبور خود را تغییر دهید اگر رمز عبور فعلی خود را به درستی وارد کنید.")
                )

        return cleaned_data