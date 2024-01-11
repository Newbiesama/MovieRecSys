from django import forms
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import render, redirect

from app01 import models
from app01.utils.bootstrap import BootStrapForm
from app01.utils.encrypt import md5
from app01.utils.checkcode import check_code


class LoginForm(BootStrapForm):
    name = forms.CharField(
        label="用户名",
        widget=forms.TextInput,
        required=True,
    )
    psw = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(render_value=True),
        required=True,
    )
    code = forms.CharField(
        label="验证码",
        widget=forms.TextInput,
        required=True,
    )

    def clean_password(self):
        """将输入的密码转为密文"""
        password = self.cleaned_data.get("psw")
        return md5(password)


def login(request):
    """ 登录页 """
    if request.method == "GET":
        form = LoginForm()
        return render(request, "login.html", {'form': form})
    # Post
    form = LoginForm(request.POST)
    if form.is_valid():
        # 可以获得cleaned_data

        # 验证码的校验
        input_code = form.cleaned_data.pop('code')
        session_code = request.session.get('image_code', "")
        if session_code.upper() != input_code.upper():
            form.add_error("code", "验证码错误")
            return render(request, "login.html", {'form': form})

        # 与数据库内容匹配，前提 Form 的键与数据库的键一致
        obj = models.UserInfo.objects.filter(**form.cleaned_data).first()

        # 错误
        if not obj:
            # 添加错误
            form.add_error("psw", "用户名或密码错误")
            return render(request, "login.html", {'form': form})

        # 正确
        # 网站生成随机字符串；写到用户浏览器的cookie中；再写入到session中；
        request.session["info"] = {'id': obj.id, 'name': obj.name}
        # 重新设置 session 超时时间
        request.session.set_expiry(60 * 60 * 24 * 7)
        return redirect("/admin/list/")
    return render(request, "login.html", {'form': form})


def logout(request):
    """注销账号"""
    request.session.clear()
    return redirect("/login/")


def image_code(request):
    """生成图片验证码"""
    # 调用函数，生成图片验证码
    img, code_string = check_code()
    # 写入到自己的session中（以便于后续获取验证码再进行校验）
    request.session["image_code"] = code_string
    # 给Session设置60s超时
    request.session.set_expiry(60)
    stream = BytesIO()
    img.save(stream, 'png')
    return HttpResponse(stream.getvalue())
