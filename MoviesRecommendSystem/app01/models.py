from django.db import models


class UserInfo(models.Model):
    name = models.CharField(verbose_name='用户名', max_length=16)
    psw = models.CharField(verbose_name='密码', max_length=32)
    phone = models.CharField(verbose_name='手机号', max_length=32)
    create_time = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)
