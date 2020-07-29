from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from users.models import User


class UsernameCountView(View):
    def get(self,request,username):
        try:
            count = User.objects.filter(username=username).count()
        except Exception as e:
            return JsonResponse({'code':400,
                                 'errmsg':'访问数据库失败'})

        return JsonResponse({'code':0,
                             'errmsg':'ok',
                             'count':count})

class MobileCountView(View):
    def get(self,request,mobile):
        try:
            count = User.objects.filter(mobile=mobile).count()
        except Exception as e:
            return JsonResponse({'code':400,
                                 'errmsg':'访问数据库失败'})

        return JsonResponse({'code':0,
                             'errmsg':'ok',
                             'count':count})