from django import forms
from django.contrib.auth.models import User
from django.forms import Form, ModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from app01 import models
from app01.models import UserInfo


def index(request):
    """ 主页 """
    return render(request, "index.html")


def login(request):
    """ 登录页 """
    if request.method == "GET":
        return render(request, "login.html")
    print(request.POST)
    return HttpResponse("OK")


def user_list(request):
    """ 用户管理 """
    queryset = models.UserInfo.objects.all()
    # 修改日期格式
    for each in queryset:
        each.create_time = each.create_time.strftime("%Y-%m-%d")
    return render(request, "user_list.html", {'user_list': queryset})


class UserAddForm(ModelForm):
    psw = forms.CharField(min_length=3, widget=forms.PasswordInput, label="密码")

    class Meta:
        model = UserInfo
        fields = ['name', 'psw', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {'class': "form-control", 'placeholder': field.label}


def user_add(request):
    if request.method == "GET":
        form = UserAddForm()  # 生成实例
        return render(request, "user_add.html", {"form": form})
    # POST
    form = UserAddForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect("/user/list")
    else:
        return render(request, "user_add.html", {"form": form})


def user_edit(request):

    return redirect("/user/list")