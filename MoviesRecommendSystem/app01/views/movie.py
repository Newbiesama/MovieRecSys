from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from app01.models import Movie, Genre
from app01.utils.pagination import Pagination


def movie_detail(request, nid):
    """电影详情页"""
    obj = Movie.objects.get(id=nid)
    obj.actors = ", ".join(obj.actors.split("|"))
    context = {
        "movie": obj
    }
    return render(request, "movie_detail.html", context)


def movie_genre(request, gid):
    if request.method == "GET":
        genres = Genre.objects.all()
        queryset = Movie.objects.filter(genre__name=genres.values()[gid - 1]['name'])
        page_object = Pagination(request, queryset, page_size=30)
        context = {
            'gid': gid,
            'genres': genres,
            'queryset': page_object.page_queryset,  # 搜素结果进行分页
            'page_string': page_object.html(),  # 生成页标的 html
        }
        return render(request, "movie_genre.html", context)
