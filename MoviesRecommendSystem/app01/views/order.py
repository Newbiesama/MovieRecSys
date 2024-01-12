import random
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from app01 import models
from app01.utils.bootstrap import BootStrapModelForm
from app01.utils.pagination import Pagination


class OrderModelForm(BootStrapModelForm):
    class Meta:
        model = models.Order
        exclude = ['oid', 'admin']


def order_list(request):
    queryset = models.Order.objects.all().order_by("id")
    page_object = Pagination(request, queryset)
    form = OrderModelForm()
    context = {
        'form': form,
        'queryset': page_object.page_queryset,  # 搜素结果进行分页
        'page_string': page_object.html(),  # 生成页标的 html
    }
    return render(request, "order_list.html", context)


@csrf_exempt
def order_add(request):
    """新建订单(AJAX请求)"""
    form = OrderModelForm(request.POST)
    if form.is_valid():
        # 添加 oid 字段
        form.instance.oid = datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(1000, 9999))
        # 自动设置管理员为当前登录的用户
        form.instance.admin_id = request.session['info']['id']
        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "errors": form.errors})


def order_delete(request):
    """删除订单"""
    uid = request.GET.get("uid")
    if not models.Order.objects.filter(id=uid).exists():
        return JsonResponse({"status": False, "error": "删除失败，数据不存在"})
    models.Order.objects.filter(id=uid).delete()
    return JsonResponse({"status": True})


def order_detail(request):
    """根据ID获取订单详细"""
    uid = request.GET.get("uid")
    # 直接获取对象数据构成的字典
    row_dict = models.Order.objects.filter(id=uid).values("title", "price", "status").first()
    if not row_dict:
        return JsonResponse({"status": False, "error": "数据不存在"})
    result = {
        "status": True,
        "data": row_dict
    }
    return JsonResponse(result)


@csrf_exempt
def order_edit(request):
    """编辑订单"""
    uid = request.GET.get("uid")
    row_object = models.Order.objects.filter(id=uid).first()
    if not row_object:
        return JsonResponse({"status": False, "tips": "数据不存在"})
    form = OrderModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "errors": form.errors})

