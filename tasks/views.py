from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.utils import timezone
from .models import Task
from .forms import TaskForm

# Create your views here.

def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                usuario = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                usuario.save()
                login(request, usuario)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'El usuario ya existe'
                })
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'Las contraseñas no coinciden'
        })


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        usuario = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if usuario is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Usuario o contraseña incorrectos'
            })
        else:
            login(request, usuario)
            return redirect('tasks')


def signout(request):
    logout(request)
    return redirect('home')


@login_required
def tasks(request):
    tareas = Task.objects.filter(usuario=request.user, fecha_completada__isnull=True)
    return render(request, 'tasks.html', {'tareas': tareas})


@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            nueva_tarea = form.save(commit=False)
            nueva_tarea.usuario = request.user
            nueva_tarea.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm,
                'error': 'Por favor ingresa datos válidos'
            })


@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        tarea = get_object_or_404(Task, pk=task_id, usuario=request.user)
        form = TaskForm(instance=tarea)
        return render(request, 'task_detail.html', {'tarea': tarea, 'form': form})
    else:
        try:
            tarea = get_object_or_404(Task, pk=task_id, usuario=request.user)
            form = TaskForm(request.POST, instance=tarea)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'tarea': tarea, 'form': form, 'error': 'Error al actualizar la tarea'})


@login_required
def tasks_completed(request):
    tareas = Task.objects.filter(usuario=request.user, fecha_completada__isnull=False).order_by('-fecha_completada')
    return render(request, 'tasks.html', {'tareas': tareas})


@login_required
def complete_task(request, task_id):
    tarea = get_object_or_404(Task, pk=task_id, usuario=request.user)
    if request.method == 'POST':
        tarea.fecha_completada = timezone.now()
        tarea.save()
        return redirect('tasks')
