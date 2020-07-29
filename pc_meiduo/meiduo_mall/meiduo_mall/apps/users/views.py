from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
import json

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

class RegisterView(View):

    def post(self,request):
        # 接收参数
        dict = json.loads(request.body.decode())
        username = dict.get('username')
        password = dict.get('password')
        password2 = dict.get('password2')
        mobile = dict.get('mobile')
        allow = dict.get('allow')
        sms_code = dict.get('sms_code')

        if not all([username,password,password2,mobile,allow,sms_code]):
            return JsonResponse({'code':400,'errmsg':'缺少必传参数'})