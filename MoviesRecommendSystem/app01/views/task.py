import json

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from app01 import models
from app01.utils.bootstrap import BootStrapModelForm
from app01.utils.pagination import Pagination


class TaskModelForm(BootStrapModelForm):
    class Meta:
        model = models.Task
        fields = '__all__'


def task_t(request):
    """任务列表"""
    queryset = models.Task.objects.all().order_by("-id")
    form = TaskModelForm
    page_object = Pagination(request, queryset)
    context = {
        'form': form,
        'queryset': page_object.page_queryset,  # 搜素结果进行分页
        'page_string': page_object.html(),  # 生成页标的 html
    }
    return render(request, "task.html", context)


@csrf_exempt
def task_add(request):
    """添加任务"""
    # 1.用户发送过来的数据进行校验（ModelForm进行校验）
    form = TaskModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        data_dict = {"status": True}
        return HttpResponse(json.dumps(data_dict))
    data_dict = {"status": False, "errors": form.errors}
    return HttpResponse(json.dumps(data_dict))
