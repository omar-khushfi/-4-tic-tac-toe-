
from django.contrib import admin
from django.urls import path
from .views import *
urlpatterns = [
      path('',games,name="games"),

   path('game/<int:pk>',game,name="game"),
   path('login/',login_view,name="login"),
   path('logout/',logout_view,name='logout'),
   path('signup/',signup_view,name="signup"),
   path('creategame',creategame,name="creategame")
]
