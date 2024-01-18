from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from app01.models import Movie, Genre, Movie_rating
from app01.utils.pagination import Pagination


def movie_detail(request, nid):
    """电影详情页"""
    if request.method == 'GET':
        # 获取电影对象
        obj = Movie.objects.get(id=nid)
        # 修改显示格式
        obj.writers = ", ".join(obj.writers.split("|"))
        obj.actors = ", ".join(obj.actors.split("|"))
        # 获取用户的评分和评论
        uid = request.session['info']['id']
        keys = ['user_id', 'movie_id']
        values = [uid, nid]
        idx_info = dict(zip(keys, values))
        ratting_info = Movie_rating.objects.filter(**idx_info).first()
        # 电影对象与评分对象
        context = {
            'rating_info': ratting_info,
            "movie": obj
        }
        return render(request, "movie_detail.html", context)
    else:
        return HttpResponse("post")


def movie_genre(request, gid):
    """电影分类展示"""
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


@csrf_exempt
def movie_rating(request):
    """给电影评分"""
    movie_id = request.GET.get("movie_id")
    rating_score = request.POST['score']
    rating_comment = request.POST['comment']
    uid = request.session['info']['id']
    if int(float(rating_score)) == 0:
        return JsonResponse({"status": False, "msg": "评分不能为0!"})
    # 检测之前是否评分
    keys = ['user_id', 'movie_id']
    values = [uid, movie_id]
    idx_info = dict(zip(keys, values))
    rating_obj = Movie_rating.objects.filter(**idx_info).first()
    # 如果评分存在
    if rating_obj:
        rating_obj.score = rating_score
        rating_obj.comment = rating_comment
        rating_obj.save()
    # 如果不存在则添加
    else:
        rating_record = Movie_rating(user_id=uid, movie_id=movie_id, score=rating_score, comment=rating_comment)
        rating_record.save()
    return JsonResponse({"status": True})
