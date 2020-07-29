from django.db import models
# Create your models here.
from django.contrib.auth.models import AbstractUser


# 我们重写用户模型类，继承自AbstractUser
class User(AbstractUser):
    mobile = models.CharField(
        unique=True,
        verbose_name='手机号',
        null= True,
        max_length=11
    )

    class Meta:
        db_table = 'tb_users'
        verbose_name = '手机号'
        verbose_name_plural = '手机号'

    def __str__(self):
        return self.username