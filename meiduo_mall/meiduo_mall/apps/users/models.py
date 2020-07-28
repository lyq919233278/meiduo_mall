from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # 补充字段
    mobile = models.CharField(
        unique=True,
        verbose_name='手机号',
        null=True,
        max_length=11
    )

    class Meta:
        db_table = 'tb_users' # 指定模型类User所映射mysql表名

        verbose_name = '手机号'
        verbose_name_plural = '手机号'

    def __str__(self):
        return self.username