from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import ToDoForm
from .models import ToDo
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.


def hometodo(request):
    return render(request, 'todo/home.html')


def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('todo:currenttodos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'That Username has already been taken, Please try a new one..!'})
        else:
            # tell user that passwords didn't match
            return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'Passwords didnt match!'})


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html', {'form': AuthenticationForm(), 'error': 'Username or Password is not Correct!'})
        else:
            login(request, user)
            return redirect('todo:currenttodos')


@login_required
def logoutuser(request):
    if request.method == "POST":
        logout(request)
        return redirect('todo:hometodo')


@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', {'form': ToDoForm()})
    else:
        try:
            form = ToDoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('todo:currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html', {'form': ToDoForm(), 'error': 'Data in Bad Format, Try Again'})


@login_required
def currenttodos(request):
    todos = ToDo.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'todo/currenttodos.html', {'todos': todos})


@login_required
def completedtodos(request):
    todos = ToDo.objects.filter(
        user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/completedtodos.html', {'todos': todos})


@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(ToDo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = ToDoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = ToDoForm(request.POST, instance=todo)
            form.save()
            return redirect('todo:currenttodos')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form, 'error': 'Bad data format..'})


@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(ToDo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('todo:currenttodos')


@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(ToDo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('todo:currenttodos')
