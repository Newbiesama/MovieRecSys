from django.shortcuts import HttpResponse, render
from app01.utils.recommend import Recommend_User


def user_cf(request):
    uid = request.session['info']['id']
    rec = Recommend_User(uid)
    print(rec.UserCF())
    print(rec.UserIIF())
    return HttpResponse("ok")
