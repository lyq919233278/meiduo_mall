# 从你刚刚下载的包中导入Celery类
from celery import Celery

# 利用导入的Celery创建对象
celery_app = Celery('meiduo')


celery_app.config_from_object('celery_tasks.config')

# 让celery_app自动捕获目标地址下的任务：
# 就是自动捕获tasks
celery_app.autodiscover_tasks(['celery_tasks.sms'])

