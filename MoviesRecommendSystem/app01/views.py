from django.http import HttpResponse
from django.shortcuts import render, redirect
from app01 import models
from app01.utils.form import UserModelForm
from app01.utils.pagination import Pagination


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
    data_dict = {}  # 用于放搜索内容
    search_data = request.GET.get("q", "")  # 获取传入的 q 参数，默认为空字符串
    if search_data:  # 如果有搜索
        data_dict["phone__contains"] = search_data
    # 搜索结果
    queryset = models.UserInfo.objects.filter(**data_dict)
    # 实现分页
    page_object = Pagination(request, queryset)
    page_queryset = page_object.page_queryset  # 搜素结果进行分页
    page_string = page_object.html()  # 生成页标的 html
    context = {
        'user_list': page_queryset,
        "search_data": search_data,
        'page_string': page_string
    }
    return render(request, "user_list.html", context)


def user_add(request):
    """添加用户"""
    if request.method == "GET":
        form = UserModelForm()  # 生成实例
        return render(request, "user_add.html", {"form": form})
    # POST
    form = UserModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect("/user/list")
    else:
        return render(request, "user_add.html", {"form": form})


def user_edit(request, nid):
    """编辑用户"""
    row_object = models.UserInfo.objects.filter(id=nid).first()
    if request.method == "GET":
        form = UserModelForm(instance=row_object)
        return render(request, "user_edit.html", {"form": form})

    form = UserModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect("/user/list")
    return render(request, "user_edit.html", {"form": form})


def user_delete(request, nid):
    """删除用户"""
    models.UserInfo.objects.filter(id=nid).delete()
    return redirect("/user/list")
