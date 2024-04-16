from django.shortcuts import HttpResponse, render, redirect
from django.contrib import messages

from app01.utils.pagination import Pagination
from app01.utils.recommend import Recommend_User, Recommend_Item
from app01.models import Movie, Movie_similarity, UserInfo, User_rec
from app01.utils.timer import timer


@timer
def user_based(request, silent=False):
    """基于用户的协同过滤推荐的视图函数"""
    q_set = UserInfo.objects.all().values_list('id')
    try:
        User_rec.objects.all().delete()
        rec_to_create = []
        for uid in q_set:
            uid = uid[0]
            rec = Recommend_User(uid)
            recs = rec.UserIIF()    # [(mid, score), ...]
            for _ in recs:
                rec_to_create.append(User_rec(user_id_id=uid, movie_id_id=_[0], score=_[1]))
        User_rec.objects.bulk_create(rec_to_create)
        if not silent:
            messages.success(request, '计算成功')
    except Exception as e:
        if not silent:
            messages.error(request, str(e))
    return render(request, 'admin_page.html')


@timer
def item_based(request, silent=False):
    """基于物品的协同过滤推荐的视图函数"""
    rec = Recommend_Item()
    try:
        Movie_similarity.objects.all().delete()
        res = rec.ItemCF_Norm()
        sim_to_create = []
        for mid, ll in res.items():
            for _ in ll:
                sim_to_create.append(Movie_similarity(movie_id1_id=mid, movie_id2_id=list(_)[0], score=list(_)[1]))
        Movie_similarity.objects.bulk_create(sim_to_create)
        if not silent:
            messages.success(request, '计算成功')
    except Exception as e:
        if not silent:
            messages.error(request, str(e))
    return render(request, 'admin_page.html')
