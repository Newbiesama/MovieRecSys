from django.db import models


class UserInfo(models.Model):
    """用户"""
    name = models.CharField(verbose_name='用户名', max_length=16)
    psw = models.CharField(verbose_name='密码', max_length=64)
    phone = models.CharField(verbose_name='手机号', max_length=32)
    create_time = models.DateField(verbose_name='创建日期')

    def __str__(self):
        return self.name


class Admin(models.Model):
    """管理员"""
    name = models.CharField(verbose_name='管理员名', max_length=16)
    psw = models.CharField(verbose_name='管理员密码', max_length=64)

    def __str__(self):
        return self.name


class Task(models.Model):
    """任务"""
    level_choices = (
        (1, "紧急"),
        (2, "重要"),
        (3, "一般"),
    )
    level = models.SmallIntegerField(verbose_name="级别", choices=level_choices, default=1)
    title = models.CharField(verbose_name="标题", max_length=64)
    detail = models.TextField(verbose_name="详细信息", max_length=128)
    user = models.ForeignKey(verbose_name="负责人", to="Admin", on_delete=models.CASCADE)


class Order(models.Model):
    """订单"""
    oid = models.CharField(verbose_name="订单号", max_length=64)
    title = models.CharField(verbose_name="商品名", max_length=64)
    price = models.IntegerField(verbose_name="价格")
    status_choices = (
        (1, "待支付"),
        (2, "已支付"),
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choices, default=1)
    admin = models.ForeignKey(verbose_name="管理员", to="Admin", on_delete=models.CASCADE)
