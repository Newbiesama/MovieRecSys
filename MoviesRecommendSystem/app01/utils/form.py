from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from app01 import models
from app01.utils.encrypt import md5
from app01.models import UserInfo, Admin
from app01.utils.bootstrap import BootStrapModelForm


class UserModelForm(BootStrapModelForm):
    """用户信息的ModelForm"""
    psw = forms.CharField(min_length=3, widget=forms.PasswordInput, label="密码")
    phone = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误')]
    )

    class Meta:
        model = UserInfo
        fields = ['name', 'psw', 'phone', 'create_time']

    def clean_phone(self):
        txt_phone = self.cleaned_data["phone"]
        temp = models.UserInfo.objects.filter(phone=txt_phone).exclude(id=self.instance.pk)
        if temp.exists():
            raise ValidationError("该手机号已存在")
        return txt_phone


class AdminModelForm(BootStrapModelForm):
    """管理员信息"""
    psw = forms.CharField(min_length=3, widget=forms.PasswordInput, label="管理员密码")
    confirm_psw = forms.CharField(min_length=3, widget=forms.PasswordInput, label="确认密码")

    class Meta:
        model = Admin
        fields = ['name', 'psw']

    def clean_psw(self):
        pwd = self.cleaned_data.get("psw")
        return md5(pwd)

    def clean_confirm_psw(self):
        psw = self.cleaned_data.get("psw")
        confirm = md5(self.cleaned_data.get("confirm_psw"))
        if psw != confirm:
            raise ValidationError("密码不一致")
        return confirm
