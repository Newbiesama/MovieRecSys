from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class AuthMiddleWare(MiddlewareMixin):
    """登录校验中间件"""
    def process_request(self, request):
        # 0.排除那些不需要登录就能访问的页面
        if request.path_info in ['/', '/register/', '/login/', '/index/', '/image/code/', '/admin/login/',
                                 '/admin/']:
            return None
        # 1.读取当前访问的用户的session信息，如果能读到，说明已登陆过，就可以继续向后走。
        info_dict = request.session.get('info')
        if info_dict:
            return None
        # 2.没有登录过，转到登录页
        return redirect("/login/")
