from django.shortcuts import render, redirect

from app01 import models
from app01.utils.pagination import Pagination
from app01.utils.form import AdminModelForm


def admin_list(request):
    """管理员列表"""
    # 检查用户是否已登录，已登录，继续想下走。未登录，跳转回登录页面。
    # 用户发来请求，获取cookie随机字符串，拿着随机字符串看看session中有没有。
    info = request.session.get("info")
    if not info:
        return redirect("/login/")
    data_dict = {}  # 用于放搜索内容
    search_data = request.GET.get("q", "")  # 获取传入的 q 参数，默认为空字符串
    if search_data:  # 如果有搜索
        data_dict["name__contains"] = search_data
    # 搜索结果
    queryset = models.Admin.objects.filter(**data_dict)
    # 实现分页
    page_object = Pagination(request, queryset)

    context = {
        "search_data": search_data,
        "page_queryset": page_object.page_queryset,
        "page_string": page_object.html()
    }
    return render(request, "admin_list.html", context)


def admin_add(request):
    """添加管理员"""
    info = "添加管理员"
    if request.method == "GET":
        form = AdminModelForm()
        return render(request, "change.html", {'form': form, 'info': info})
    # POST
    form = AdminModelForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect("/admin/list/")
    return render(request, "change.html", {'form': form, 'info': info})


def admin_edit(request, nid):
    """编辑管理员"""
    info = "编辑管理员"
    # 是否存在对象
    row_object = models.Admin.objects.filter(id=nid).first()
    if not row_object:
        return render(request, "error.html", {'msg': "对象不存在"})
    if request.method == "GET":
        form = AdminModelForm(instance=row_object)
        return render(request, "change.html", {'form': form, 'info': info})
    form = AdminModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect("/admin/list/")
    return render(request, "change.html", {'form': form, 'info': info})


def admin_delete(request, nid):
    """删除管理员"""
    row_object = models.Admin.objects.filter(id=nid).first()
    if not row_object:
        return render(request, "error.html", {'msg': "对象不存在"})
    models.Admin.objects.filter(id=nid).delete()
    return redirect("/admin/list/")
