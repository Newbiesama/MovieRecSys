import os.path

from django.contrib import messages
from identicons import generate
from identicons import save

from app01 import models


def gen_icon(text):
    """生成头像"""
    try:
        icon = generate(str(text))
        static_url = '/Volumes/HY/PythonProjects/MoviesRecommendSystem/MoviesRecommendSystem/app01/static'
        fn = os.path.join(static_url, 'icons', f"icon_{str(text).replace(' ', '_')}.png")
        save(icon, fn, 500, 500)
        return True
    except Exception as e:
        return e


def set_icons(*uid):
    try:
        if not uid:
            q_set = models.UserInfo.objects.all().values_list('id')
            for uid in q_set:
                uid = uid[0]
                gen_icon(uid)
                fn = f"icon_{uid}.png"
                models.UserInfo.objects.filter(id=uid).update(icon_url=fn)
        else:
            for uid in uid:
                gen_icon(uid)
                fn = f"icon_{uid}.png"
                models.UserInfo.objects.filter(id=uid).update(icon_url=fn)
        return True
    except Exception as e:
        print(e)
        return False
