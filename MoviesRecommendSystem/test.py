from django.shortcuts import HttpResponse, render, redirect
from django.contrib import messages

from app01.utils.pagination import Pagination
from app01.utils.recommend import Recommend_User, Recommend_Item
from app01.models import Movie, Movie_similarity, UserInfo, User_rec
from app01.utils.timer import timer


def user_based(request, silent=False):
    """基于用户的协同过滤推荐的视图函数"""
    User_rec.objects.all().delete()
    return HttpResponse('ok.')
