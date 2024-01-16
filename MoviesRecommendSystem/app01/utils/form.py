from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from app01 import models
from app01.utils.encrypt import md5
from app01.models import UserInfo, Admin
from app01.utils.bootstrap import BootStrapForm, BootStrapModelForm


class UserModelForm(BootStrapModelForm):
    """用户信息的ModelForm"""
    psw = forms.CharField(min_length=3, widget=forms.PasswordInput, label="密码")
    email = forms.CharField(
        label="邮箱",
        validators=[RegexValidator(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', '邮箱格式错误')]
    )

    class Meta:
        model = UserInfo
        fields = ['name', 'psw', 'email']

    def clean_email(self):
        txt_email = self.cleaned_data["email"]
        temp = models.UserInfo.objects.filter(email=txt_email).exclude(id=self.instance.pk)
        if temp.exists():
            raise ValidationError("该邮箱已存在")
        return txt_email

    def clean_psw(self):
        """将输入的密码转为密文"""
        password = self.cleaned_data.get("psw")
        return md5(password)


class AdminModelForm(BootStrapModelForm):
    """管理员信息"""
    psw = forms.CharField(min_length=3, widget=forms.PasswordInput, label="管理员密码")
    confirm_psw = forms.CharField(min_length=3, widget=forms.PasswordInput, label="确认密码")

    class Meta:
        model = Admin
        fields = ['name', 'psw']

    def clean_psw(self):
        """将输入的密码转为密文"""
        pwd = self.cleaned_data.get("psw")
        return md5(pwd)

    def clean_confirm_psw(self):
        psw = self.cleaned_data.get("psw")
        confirm = md5(self.cleaned_data.get("confirm_psw"))
        if psw != confirm:
            raise ValidationError("密码不一致")
        return confirm


class LoginForm(BootStrapForm):
    name = forms.CharField(
        label="用户名",
        widget=forms.TextInput,
        required=True,
    )
    psw = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(render_value=True),
        required=True,
    )
    code = forms.CharField(
        label="验证码",
        widget=forms.TextInput,
        required=True,
    )

    def clean_password(self):
        """将输入的密码转为密文"""
        password = self.cleaned_data.get("psw")
        return md5(password)


class AdminLoginForm(BootStrapForm):
    name = forms.CharField(
        label="管理员名",
        widget=forms.TextInput,
        required=True,
    )
    psw = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(render_value=True),
        required=True,
    )

    def clean_password(self):
        """将输入的密码转为密文"""
        password = self.cleaned_data.get("psw")
        return md5(password)
