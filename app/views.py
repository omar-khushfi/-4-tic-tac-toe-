from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render,redirect
from django.urls import reverse
from .models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
# Create your views here.


def creategame(request):
    name=request.POST.get('name')

    if name!=None:
        game=Game(name=name)
        game.save()
        game.player.add(request.user) 
        game.save()
        return redirect(reverse('game', args=[game.id]))
    else:
        return render(request,'creategame.html')



@login_required()
def game(request,pk):
    game=Game.objects.get(pk=pk)
    player=game.player.all()
    
    if request.user not in player:
        game.player.add(request.user) 
        game.save()
    moves=[]
    for i in range(1,10):
        if  Move.objects.filter(x=i,game=game).exists():
            move= Move.objects.get(x=i,game=game)
            moves.append({'ty':move.ty,'x':i})
        else:
            moves.append({'ty':0,'x':i})
          
        
    context={
            'game':game,
            'moves':moves
    }
    
    return render(request,'game.html',context)

@login_required()
def games(request):
    games=Game.objects.all()
    search=None
    search=request.POST.get("search")
    
    if search != None:
        games=Game.objects.filter(name=search)
    if games.count() < 1:
            games=Game.objects.all()

    paginator=Paginator(games,6) 
    page_number=request.GET.get("page")
    try:
       games=paginator.page(page_number)
    except PageNotAnInteger: 
        games=paginator.page(1)
    except EmptyPage: 
        games=paginator.page(1)
    
    context={
    'games':games,
    }
    return render(request,'games.html',context)
    

def login_view(request):
    username=request.POST.get('name')
    password=request.POST.get('password')
    user=authenticate(request,username=username,password=password)
    if user is not None:
        login(request,user)
        return redirect('/')
    
    return render(request,'login.html')




def signup_view(request):
    name=request.POST.get('name')
    password1=request.POST.get('password1')
    password2=request.POST.get('password2')
    print(name,password1,password2)
    if (password1 == password2) and name:
        if (User.objects.filter(username=name).count() > 0):
            pass
        else:   
          
            user=User.objects.create(username=name,password=password1)
            if user:
                login(request,user)
                return redirect('/')
           

    return render(request,'signin.html')


def logout_view(request):
    logout(request)
    return redirect('login')


