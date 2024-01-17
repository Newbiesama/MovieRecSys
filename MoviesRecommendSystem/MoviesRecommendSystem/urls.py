"""MoviesRecommendSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from app01.views import homepage, user, admin, account, task, order, movie

urlpatterns = [
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
    # 任务
    path('task/', task.task_t),
    path('task/add/', task.task_add),
    # 订单
    path('order/list/', order.order_list),
    path('order/add/', order.order_add),
    path('order/delete/', order.order_delete),
    path('order/detail/', order.order_detail),
    path('order/edit/', order.order_edit),
]
