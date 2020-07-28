import logging
import random
import re

logger = logging.getLogger('django')
from celery_tasks.sms.tasks import ccp_send_sms_code

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django_redis import get_redis_connection
from meiduo_mall.libs.captcha.captcha import captcha
from meiduo_mall.libs.yuntongxun.ccp_sms import CCP
# Create your views here.

class ImageCodeView(View):
    # 返回图形验证码的类视图
    def get(self,request,uuid):
        # 生成图形验证码，保存到redis中，另外返回图片
        text, image = captcha.generate_captcha()

        redis_com = get_redis_connection('verify_code')
        redis_com.setex('img_%s'%uuid, 300,text)
        # 返回图片
        return HttpResponse(image,
                            content_type='img/jpg')


class SMSCodeView(View):

    def get(self,request,mobile):

        # 创建连接到redis数据库的对象
        redis_conn = get_redis_connection('verify_code')
        # 进入函数，获取redis里面的值，如果获取成功，说明没过60s
        time_redis = redis_conn.get('time_%s'%mobile)
        if time_redis:
            return JsonResponse({'code':400,
                                 'errmsg':'发送短信过于频繁'})
        # 接受查询参数参数
        image = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')
        # 校验参数
        if not all([image,uuid]):
            return JsonResponse({"code":400,
                                 "errmsg":'缺少必传参数'})

        # 提取图片验证码
        image_redis = redis_conn.get('img_%s'%uuid)
        # 验证验证码过期或不存在
        if image_redis is None:
            return JsonResponse({'code':400,
                                 'errmsg':'图形验证码失效'})
        # 删除redis中的图形验证码
        try:
            redis_conn.delete('img_%s'%uuid)
        except Exception as e:
            logger.error(e)

        # 对比图形验证码
        image_new = image_redis.decode('utf-8')
        if image.lower() != image_new.lower():
            return JsonResponse({'code':400,
                                 'errmsg':'输入图形验证码有误'})

        # 生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)

        # 创建 Redis 管道
        pl = redis_conn.pipeline()

        # 将 Redis 请求添加到队列
        pl.setex('sms_%s' % mobile, 300, sms_code)
        pl.setex('time_%s' % mobile, 60, 1)

        # 执行请求, 这一步千万别忘了
        pl.execute()
        # 保存短信验证码
        # 短信验证码有效时间，300秒
        # 发送短信验証码
        ccp_send_sms_code.delay(mobile, sms_code)
        # return JsonResponse({'code':0,'errmsg':'短信发送成功'})

        return JsonResponse({'code': 0,
                             'errmsg': 'ok'})