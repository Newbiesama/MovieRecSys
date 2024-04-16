import csv
import os

from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone

from app01 import models
from app01.utils.pagination import Pagination
from app01.utils.form import AdminModelForm, LoginForm
from app01.utils import data_procession, gen_icon
from django.http import JsonResponse
from apscheduler.schedulers.base import BaseScheduler

BASE = os.getcwd()


def admin_login(request):
    """ 登录页 """
    if request.method == "GET":
        form = LoginForm()
        return render(request, "admin_login.html", {'form': form})
    # Post
    form = LoginForm(request.POST)
    if form.is_valid():
        # 可以获得cleaned_data: {'name': 'admin', 'psw': '123', 'code': 'login'}
        # 验证码的校验
        # 把 code 从 cleaned_data 中 pop 掉，为了直接验证 name 和 psw
        input_code = form.cleaned_data.pop('code')
        session_code = request.session.get('image_code', "")
        if session_code.upper() != input_code.upper():
            form.add_error("code", "验证码错误")
            return render(request, "login.html", {'form': form})
        models.Admin.objects.filter(**form.cleaned_data).update(login_time=timezone.now())
        # 与数据库内容匹配，前提 Form 的键与数据库的键一致
        obj = models.Admin.objects.filter(**form.cleaned_data).first()
        # 错误
        if not obj:
            # 添加错误
            form.add_error("name", "用户名或密码错误")
            return render(request, "admin_login.html", {'form': form})

        # 正确
        # 网站生成随机字符串；写到用户浏览器的cookie中；再写入到session中；
        request.session["info"] = {'id': obj.id, 'name': obj.name, 'type': str(1)}
        # 重新设置 session 超时时间
        request.session.set_expiry(60 * 60 * 24 * 7)
        return redirect("/")
    form.add_error("name", "发生错误")
    return render(request, "admin_login.html", {'form': form})


def admin_page(request):
    """管理员页面"""
    info_dict = request.session.get('info')
    if not info_dict or info_dict['type'] is '0':
        return redirect("/myadmin/login/")
    from scheduledTasks.views import scheduler
    # print(scheduler.get_jobs())
    scheduler.print_jobs()
    # print(scheduler.running)
    jobs = scheduler.get_jobs()  # 获取所有任务
    job_list = []
    for job in jobs:
        next_time = 'null'
        if not job.pending:
            next_time = str(job.next_run_time)
        job_info = {
            'id': job.id,
            'trigger': job.trigger,
            'state': job.pending,
            'next_run_time': next_time
        }
        job_list.append(job_info)
    content = {
        'job_info': job_list
    }
    return render(request, "admin_page.html", content)


def admin_list(request):
    """管理员列表"""
    # 检查用户是否已登录，已登录，继续想下走。未登录，跳转回登录页面。
    # 用户发来请求，获取cookie随机字符串，拿着随机字符串看看session中有没有。
    info = request.session.get("info")
    if not info:
        return redirect("/login/")
    data_dict = {}  # 用于放搜索内容
    search_data = request.GET.get("q", "")  # 获取传入的 q 参数，默认为空字符串
    if search_data:  # 如果有搜索
        data_dict["name__contains"] = search_data
    # 搜索结果
    queryset = models.Admin.objects.filter(**data_dict)
    # 实现分页
    page_object = Pagination(request, queryset)

    context = {
        "search_data": search_data,
        "page_queryset": page_object.page_queryset,
        "page_string": page_object.html()
    }
    return render(request, "admin_page.html", context)


def admin_add(request):
    """添加管理员"""
    info = "添加管理员"
    if request.method == "GET":
        form = AdminModelForm()
        return render(request, "change.html", {'form': form, 'info': info})
    # POST
    form = AdminModelForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect("/admin/list/")
    return render(request, "change.html", {'form': form, 'info': info})


def admin_edit(request, nid):
    """编辑管理员"""
    info = "编辑管理员"
    # 是否存在对象
    row_object = models.Admin.objects.filter(id=nid).first()
    if not row_object:
        return render(request, "error.html", {'msg': "对象不存在"})
    if request.method == "GET":
        form = AdminModelForm(instance=row_object)
        return render(request, "change.html", {'form': form, 'info': info})
    form = AdminModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect("/admin/list/")
    return render(request, "change.html", {'form': form, 'info': info})


def admin_delete(request, nid):
    """删除管理员"""
    row_object = models.Admin.objects.filter(id=nid).first()
    if not row_object:
        return render(request, "error.html", {'msg': "对象不存在"})
    models.Admin.objects.filter(id=nid).delete()
    return redirect("/admin/list/")


def import_genre(request):
    """导入所有电影类型"""
    path = os.path.join(BASE, "app01/static/IMDBInfo/info/genre.txt")
    genres_to_create = []  # [<Genre: <Genre:Musical>>, <Genre: <Genre:War>> ...]
    try:
        with open(path) as fb:
            for line in fb:
                genre_name = line.strip()
                # 检查该类型是否已存在
                if not models.Genre.objects.filter(name=genre_name).exists():
                    genres_to_create.append(models.Genre(name=genre_name))
        # 批量创建
        models.Genre.objects.bulk_create(genres_to_create)
    except FileNotFoundError:
        return HttpResponse("文件未找到", status=404)
    except Exception as e:
        # 记录异常到日志
        print(f"导入过程中发生错误: {e}")
        return HttpResponse("导入过程中发生错误", status=500)
    return HttpResponse("OK")


def import_movie(request):
    """导入所有电影信息，并设置它们的类型"""
    path = os.path.join(BASE, "app01/static/IMDBInfo/info/info.csv")
    try:
        with open(path) as fb:
            reader = csv.reader(fb)
            title = reader.__next__()
            # 读取title信息 id,name,url,duration,genre,release_time,intro,directors,writers,stars
            # 这里的id是imdb的id，根据它来访问static文件夹下面的poster
            title_dct = dict(zip(title, range(len(title))))
            # title: ['id','name','url','duration','genre','release_time','intro','directors','writers','stars']
            # title_dct: {'id': 0, 'name': 1, 'url': 2, 'duration': 3, 'genre': 4, 'release_time': 5, 'intro': 6,
            # 'directors': 7, 'writers': 8, 'stars': 9}

            # 加载所有类型到内存
            genres = {genre.name: genre for genre in models.Genre.objects.all()}
            movies_to_create = []
            for i, line in enumerate(reader):
                m = models.Movie.objects.create(
                    name=line[title_dct['name']],
                    imdb_id=line[title_dct['id']],
                    duration=line[title_dct['duration']],
                    release_time=line[title_dct['release_time']],
                    intro=line[title_dct['intro']],
                    director=line[title_dct['directors']],
                    writers=line[title_dct['writers']],
                    actors=line[title_dct['stars']]
                )
                movies_to_create.append(m)
                # 查看进度
                if i % 1000 == 0:
                    print("创建数据--" + str(i))

            # 使用事务确保数据一致性
            with transaction.atomic():
                # 批量创建电影
                models.Movie.objects.bulk_create(movies_to_create)
            # 要先更新才能设置类型
            field_names = [f.name for f in models.Movie._meta.fields]
            models.Movie.objects.bulk_update(movies_to_create, field_names)
            # 为每部电影设置类型
            for i, line in enumerate(reader):
                movie = models.Movie.objects.get(imdb_id=line[title_dct['id']])
                genre_names = line[title_dct['genre']].split('|')
                for genre_name in genre_names:
                    if genre_name in genres:
                        movie.genre.add(genres[genre_name])
                # 查看进度
                if i % 1000 == 0:
                    print("设置类型--" + str(i))
        return HttpResponse("电影信息导入成功")
    except FileNotFoundError:
        return HttpResponse("文件未找到", status=404)
    except Exception as e:
        return HttpResponse(f"导入过程中发生错误: {str(e)}", status=500)


def import_user_rating(request):
    """
    获取ratings文件，设置用户信息和对电影的评分
    由于用户没有独立的信息，默认用这种方式保存用户User: name=userId, password=userId, email=userId@example.com
    通过imdb_id对电影进行关联，设置用户对电影的评分，comment默认为空
    """
    path = os.path.join(BASE, "app01/static/IMDBInfo/info/ratings.csv")
    try:
        with open(path) as fb:
            reader = csv.reader(fb)
            # userId,movieId,rating,timestamp
            title = reader.__next__()
            title_dct = dict(zip(title, range(len(title))))
            # csv文件中，一条记录就是一个用户对一部电影的评分和时间戳，一个用户可能有多条评论
            # 所以要先取出用户所有的评分，设置成一个字典,格式为{ user:{movie1:rating, movie2:rating, ...}, ...}
            user_id_dct = dict()
            for line in reader:
                user_id = line[title_dct['userId']]
                imdb_id = line[title_dct['movieId']]
                rating = line[title_dct['rating']]
                user_id_dct.setdefault(user_id, dict())
                user_id_dct[user_id][imdb_id] = rating
        # 对所有用户和评分记录
        for user_id, ratings in user_id_dct.items():
            u = models.UserInfo.objects.create(name=user_id, psw=user_id, email=f'{user_id}@example.com')
            # 必须先保存
            u.save()
            # 开始加入评分记录
            for imdb_id, rating in ratings.items():
                # Movie_rating(uid=)
                movie = models.Movie.objects.get(imdb_id=imdb_id)
                relation = models.Movie_rating(user=u, movie=movie, score=rating, comment='')
                relation.save()
            print(f'{user_id} process success')
        return HttpResponse("用户评分导入成功")
    except FileNotFoundError:
        return HttpResponse("文件未找到", status=404)
    except Exception as e:
        return HttpResponse(f"导入过程中发生错误: {str(e)}", status=500)


def cal_rank_url(request, silent=False):
    """计算排行榜的路由"""
    if data_procession.cal_rank():
        if not silent:
            messages.success(request, '计算成功')
        return render(request, "admin_page.html")
    else:
        if not silent:
            messages.error(request, '发生错误')
        return render(request, "admin_page.html")


def admin_set_icons(request):
    if gen_icon.set_icons():
        messages.success(request, '设置成功')
        return render(request, "admin_page.html")
    else:
        messages.error(request, '发生错误')
        return render(request, "admin_page.html")
