from django.shortcuts import HttpResponse, render
from django.contrib import messages

from app01.utils.pagination import Pagination
from app01.utils.recommend import Recommend_User, Recommend_Item
from app01.models import Movie, Movie_similarity, User_rec
from app01.utils.timer import timer


def user_based(request):
    """基于用户的协同过滤推荐的视图函数"""
    uid = request.session['info']['id']
    rec = Recommend_User(uid)
    recs = rec.UserIIF()
    mid = []
    for a, _ in recs:
        mid.append(a)
    queryset = Movie.objects.filter(id__in=mid)
    page_object = Pagination(request, queryset, page_size=30)
    context = {
        'queryset': page_object.page_queryset,  # 搜素结果进行分页
        'page_string': page_object.html(),  # 生成页标的 html
    }
    return render(request, 'movie_recommend.html', context)


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
        # with open(r'logs/recommend.log', 'w+') as df:
        #     df.write(str(rec.ItemCF_Norm()))
        if not silent:
            messages.success(request, '计算成功')
    except Exception as e:
        if not silent:
            messages.error(request, str(e))
    return render(request, 'admin_page.html')
