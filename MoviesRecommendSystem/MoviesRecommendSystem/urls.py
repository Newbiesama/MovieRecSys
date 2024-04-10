from django.conf.urls import url
from django.urls import path
from django.contrib import admin as dadmin
from app01.views import homepage, user, my_admin, account, task, order, movie, recommend
from scheduledTasks.views import start, stop
from app01.utils import data_procession

urlpatterns = [
    # Django Administration
    # url(r'^admin/', dadmin.site.urls),
    # 主页
    path('', homepage.index),
    # 账号
    path('login/', account.login),
    path('admin/login/', account.admin_login),
    path('logout/', account.logout),
    path('image/code/', account.image_code),
    path('register/', account.register),
    # 用户
    path('user/list/', user.user_list),
    path('user/add/', user.user_add),
    path('user/<int:nid>/edit', user.user_edit),
    path('user/<int:nid>/delete', user.user_delete),
    path('user/history/', user.user_history),
    path('user/detail/', user.user_detail),
    # 管理员
    path('myadmin/', my_admin.admin_page),
    path('admin/add/', my_admin.admin_add),
    path('admin/<int:nid>/edit/', my_admin.admin_edit),
    path('admin/<int:nid>/delete/', my_admin.admin_delete),
    # 数据处理
    # path('admin/import_g/', admin.import_genre),
    # path('admin/import_m/', admin.import_movie),
    # path('admin/import_u/', admin.import_user_rating),
    path('cal_rank/', my_admin.cal_rank_url),
    # 电影
    path('movie/detail/<int:nid>/', movie.movie_detail),
    path('movie/genre/<int:gid>/', movie.movie_genre),
    path('movie/rating/', movie.movie_rating),
    path('movie/rank/', movie.movie_rank),
    # 推荐
    path('recommend_user/', recommend.user_based),
    path('recommend_item/', recommend.item_based),
    # 任务
    path('task/', task.task_t),
    path('task/add/', task.task_add),
    # 订单
    path('order/list/', order.order_list),
    path('order/add/', order.order_add),
    path('order/delete/', order.order_delete),
    path('order/detail/', order.order_detail),
    path('order/edit/', order.order_edit),
    # 用于定时任务
    path("task_start/", start),
    path("task_stop/", stop),
]
