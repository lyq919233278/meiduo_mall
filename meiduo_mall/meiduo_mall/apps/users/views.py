import json
import re
from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import render
# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from users.models import User


class UsernameCountView(View):
    # 判断用户是否存在
    def get(self, request, username):
        print(username)
        # 判断用户是否存在
        try:
            count = User.objects.filter(username=username).count()
        except Exception as e:
            return JsonResponse({'code':400,
                                 'errmsg':'访问数据库失败'})

        return JsonResponse({'code': 0,
                             'errmsg':'ok',
                             'count':count})

class MobileCountView(View):

    def get(self, request, mobile):
        # 1、根据手机号统计数量
       	try:
            count = User.objects.filter(mobile=mobile).count()
        except Exception as  e:
            return JsonResponse({'code':400,
                                 'errmsg':'访问数据库失败'})
        # 2、构建响应
        return JsonResponse({'code': 0,
                             'errmsg': 'ok',
                             'count': count})

class RegisterView(View):

    def post(self,request):
        # 接收参数，保存到数据库
        dict = json.loads(request.body.decode())
        username = dict.get('username')
        password = dict.get('password')
        password2 = dict.get('password2')
        mobile = dict.get('mobile')
        sms_code = dict.get('sms_code')
        allow = dict.get('allow')

        if not all([username, password, password2, mobile, sms_code, allow]):
            return JsonResponse({'code':400,
                                 'errmsg':'缺少必传参数'})

        # 校验username
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return JsonResponse({'code': 400,
                                      'errmsg': 'username格式有误'})

            # 4.password检验
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return JsonResponse({'code': 400,
                                      'errmsg': 'password格式有误'})

            # 5.password2 和 password
        if password != password2:
            return JsonResponse({'code': 400,
                                      'errmsg': '两次输入不对'})
            # 6.mobile检验
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400,
                                      'errmsg': 'mobile格式有误'})
            # 7.allow检验
        if allow != True:
            return JsonResponse({'code': 400,
                                      'errmsg': 'allow格式有误'})

            # 8.sms_code检验 (链接redis数据库)
        redis_conn = get_redis_connection('verify_code')

        # 9.从redis中取值
        sms_code_c = redis_conn.get('sms_%s'%mobile)

        if not sms_code_c:
            return JsonResponse({'code':400,
                                 'errmsg':'短信验证码过期'})

        if sms_code != sms_code_c.decode():
            return JsonResponse({'code':400,
                                 'errmsg':'输入短信验证码错误'})
        try:
            user = User.objects.create_user(username=username,
                                     password=password,
                                     mobile=mobile)
        except Exception as e:
            return JsonResponse({'code':400,
                                 'errmsg':'保存到数据库出错'})

        login(request, user)

        return JsonResponse({'code':0,

                             'errmsg':'ok'})

