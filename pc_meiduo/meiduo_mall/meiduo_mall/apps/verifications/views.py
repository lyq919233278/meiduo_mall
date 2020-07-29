from django.shortcuts import render

# Create your views here.
import logging
logger = logging.getLogger('django')
import random
from django import http
from meiduo_mall.libs.yuntongxun.ccp_sms import CCP
from django.views import View
from django_redis import get_redis_connection
from django.http import HttpResponse, JsonResponse

from meiduo_mall.libs.captcha.captcha import captcha


class ImageCodeView(View):
    def get(self,request,uuid):
        text, image = captcha.generate_captcha()

        # 链接redis数据库，获取数据库对象
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('img_%s'%uuid, 300, text)
        return HttpResponse(image,
                            content_type='image/jpg')


class SMSCodeView(View):
    def get(self,request,mobile):

        redis_conn = get_redis_connection('verify_code')
        time = redis_conn.get('time_%s'%mobile)
        if time:
            return JsonResponse({'code':400,'errmsg':'发送短信过于频繁'})
        # 接收参数

        image_code_c = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')
        # 校验参数
        if not all([image_code_c,uuid]):
            return JsonResponse({'code':400,
                                 'errmsg':'缺少必传参数'})

        # 创建连接到redis的对象

        # 提取图片验证码
        image_code_s = redis_conn.get('img_%s'%uuid)
        if image_code_s is None:
            return JsonResponse({'code':400,
                                 'errmsg':'图形验证码失效'})

        try:
            redis_conn.delete('img_%s'%uuid)
        except Exception as e:
            logger.error(e)

        image_code_sc = image_code_s.decode()
        # 对比图形验证码
        if image_code_c.lower() != image_code_sc.lower():
            return JsonResponse({'code':400,
                                 'errmsg':'输入图形验证码有误'})

        # 生成短信验证码
        sms_code = '%06d'% random.randint(0,999999)
        logger.info(sms_code)

        # 保存短信验证码
        # 有效时间为300秒
        redis_conn.setex('sms_%s'%mobile,300,sms_code)
        redis_conn.setex('time_%s'%mobile,60,1)
        # 发送短信验证码
        CCP().send_template_sms(mobile,[sms_code,5],1)

        return JsonResponse({'code':0,
                             'errmsg':'发送短信成功'})