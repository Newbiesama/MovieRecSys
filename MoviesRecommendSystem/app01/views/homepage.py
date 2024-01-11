from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    """ 主页 """
    return render(request, "index.html")

