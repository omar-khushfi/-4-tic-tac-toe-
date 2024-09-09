from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    name=models.CharField(max_length=150)
    round=models.BooleanField(default=0)
    REQUIRED_FIElDS=['name']
    

    
class Game(models.Model):
    player=models.ManyToManyField(User)
    currnt_move=models.CharField(max_length=10,default='o')
    name=models.CharField(max_length=50,unique=True)
   
    
    
class Move(models.Model):
    ty=models.CharField(max_length=12)
    x=models.IntegerField()
    game=models.ForeignKey(Game,on_delete=models.CASCADE)
    