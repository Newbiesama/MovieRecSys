from django.http import HttpResponse
from django.shortcuts import render, redirect
from app01 import models
from app01.utils.pagination import Pagination
from app01.views.recommend import user_based


def index(request):
    """ 主页 """
    queryset = models.Movie.objects.filter(imdb_id__lte=1000)
    page_object = Pagination(request, queryset, page_size=50)
    rec_movies = []
    try:
        rec_movies_id = models.User_rec.objects.filter(user_id_id=request.session['info']['id']).values_list(
            'movie_id_id')
        if rec_movies_id.count() == 0:
            rec_movies_id = models.Movie_ranking.objects.order_by('-rank_score')[:20].values_list('movie_id_id')
        rec_movies = [models.Movie.objects.filter(id=x[0]).first() for x in rec_movies_id]
    except Exception as e:
        print(e)
    context = {
        'queryset': page_object.page_queryset,  # 搜素结果进行分页
        'page_string': page_object.html(),  # 生成页标的 html
        'rec_movies': rec_movies
    }
    return render(request, "index.html", context)


def search(request):
    """搜索"""
    data_dict = {}  # 用于放搜索内容
    content = request.GET.get("search_content", "")  # 获取传入内容，默认为空字符串
    if content:  # 如果有搜索
        data_dict['name__contains'] = content
    else:
        return redirect('/')
    # 搜索结果
    queryset = models.Movie.objects.filter(**data_dict)
    if not queryset:
        return render(request, "search_results.html")
    page_object = Pagination(request, queryset, page_size=50)
    context = {
        'queryset': page_object.page_queryset,  # 搜素结果进行分页
        'page_string': page_object.html(),  # 生成页标的 html
    }
    return render(request, "search_results.html", context)
