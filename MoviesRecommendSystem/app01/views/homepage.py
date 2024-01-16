from django.http import HttpResponse
from django.shortcuts import render
from app01 import models
from app01.utils.pagination import Pagination


def index(request):
    """ 主页 """
    queryset = models.Movie.objects.filter(imdb_id__lte=1000)
    page_object = Pagination(request, queryset, page_size=50)
    context = {
        'queryset': page_object.page_queryset,  # 搜素结果进行分页
        'page_string': page_object.html(),  # 生成页标的 html
    }
    return render(request, "index.html", context)

