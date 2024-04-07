from django.conf.urls import url
from django.urls import path
from django.contrib import admin as dadmin
from app01.views import homepage, user, admin, account, task, order, movie, recommend
from scheduledTasks.views import testTimedTasks

urlpatterns = [
    # Django Administration
    url(r'^admin/', dadmin.site.urls),
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
    # 管理员
    path('admin/list/', admin.admin_list),
    path('admin/add/', admin.admin_add),
    path('admin/<int:nid>/edit/', admin.admin_edit),
    path('admin/<int:nid>/delete/', admin.admin_delete),
    # path('admin/import_g/', admin.import_genre),
    # path('admin/import_m/', admin.import_movie),
    # path('admin/import_u/', admin.import_user_rating),
    # 电影
    path('movie/detail/<int:nid>/', movie.movie_detail),
    path('movie/genre/<int:gid>/', movie.movie_genre),
    path('movie/rating/', movie.movie_rating),
    path('movie/rank/', movie.movie_rank),
    # 推荐
    path('recommend/', recommend.item_based),
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
    path("test-timed-tasks/", testTimedTasks, name="test-timed-tasks"),
]
