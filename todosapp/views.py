import mimetypes
import os
from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404, HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json

from todos import settings

from .models import Todo


@login_required
def index(request):
    if request.method == 'POST':
        # Handle JSON POST data
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                title = data.get('title')
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
        else:
            title = request.POST.get('title')
        
        if title:
            todo = Todo.objects.create(
                user=request.user,
                title=title, 
                pub_date=timezone.now()
            )
            if request.headers.get('Accept') == 'application/json' or request.content_type == 'application/json':
                return JsonResponse({
                    'id': todo.id,
                    'title': todo.title,
                    'state': todo.state,
                    'pub_date': todo.pub_date.isoformat()
                }, status=201)
            return redirect('index')
    
    # Get todos for the current user only
    todos = Todo.objects.filter(user=request.user).order_by("-pub_date")[:5]
    
    if request.headers.get('Accept') == 'application/json':
        todos_data = [{
            'id': todo.id,
            'title': todo.title,
            'state': todo.state,
            'pub_date': todo.pub_date.isoformat()
        } for todo in todos]
        return JsonResponse({'todos': todos_data})
    
    dist_path = os.path.join(settings.BASE_DIR, 'vite-project', 'dist')
    index_path = os.path.join(dist_path, 'index.html')
    
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    else:
        raise Http404("Vue app not found. Make sure to run 'make runvite' first.")


@login_required
def set_state(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id, user=request.user)
    
    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                state = data.get('state')
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
        else:
            state = request.POST.get('state')
        
        if state is not None:
            todo.state = state
            todo.save()
            
            if request.headers.get('Accept') == 'application/json' or request.content_type == 'application/json':
                return JsonResponse({
                    'id': todo.id,
                    'title': todo.title,
                    'state': todo.state,
                    'pub_date': todo.pub_date.isoformat()
                })
            return redirect('index')
        else:
            if request.headers.get('Accept') == 'application/json' or request.content_type == 'application/json':
                return JsonResponse({'error': 'State value is required'}, status=400)
            return HttpResponse("State value is required", status=400)
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'id': todo.id,
            'title': todo.title,
            'state': getattr(todo, 'state', None),
            'pub_date': todo.pub_date.isoformat()
        })
    
    return HttpResponse("state for %s." % todo.id)


@login_required
def detail(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id, user=request.user)
    
    # Return JSON if client accepts JSON
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'id': todo.id,
            'title': todo.title,
            'pub_date': todo.pub_date.isoformat()
        })
    
    return render(request, 'todosapp/detail.html', {'todo': todo})


def vue_app(request):
    """Serve the main Vue app (index.html)"""
    dist_path = os.path.join(settings.BASE_DIR, 'vite-project', 'dist')
    index_path = os.path.join(dist_path, 'index.html')
    
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    else:
        raise Http404("Vue app not found. Make sure to run 'make runvite' first.")


def vue_static(request, path):
    """Serve static files from vite-project/dist"""
    dist_path = os.path.join(settings.BASE_DIR, 'vite-project', 'dist')
    file_path = os.path.join(dist_path, path)
    
    if not file_path.startswith(dist_path):
        raise Http404("Invalid path")
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
            return response
    else:
        raise Http404("File not found")

@login_required
def delete_todo(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id, user=request.user)
    
    if request.method == 'POST' or request.method == 'DELETE':
        todo.delete()
        
        if request.headers.get('Accept') == 'application/json' or request.content_type == 'application/json':
            return JsonResponse({'message': 'Todo deleted successfully'}, status=200)
        return redirect('index')
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    return HttpResponse("Method not allowed", status=405)


@login_required
def update_title(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id, user=request.user)
    
    if request.method == 'POST' or request.method == 'PUT':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                title = data.get('title')
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
        else:
            title = request.POST.get('title')
        
        if title is not None and title.strip():
            todo.title = title.strip()
            todo.save()
            
            if request.headers.get('Accept') == 'application/json' or request.content_type == 'application/json':
                return JsonResponse({
                    'id': todo.id,
                    'title': todo.title,
                    'state': todo.state,
                    'pub_date': todo.pub_date.isoformat()
                })
            return redirect('index')
        else:
            if request.headers.get('Accept') == 'application/json' or request.content_type == 'application/json':
                return JsonResponse({'error': 'Title value is required and cannot be empty'}, status=400)
            return HttpResponse("Title value is required and cannot be empty", status=400)
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'id': todo.id,
            'title': todo.title,
            'state': todo.state,
            'pub_date': todo.pub_date.isoformat()
        })
    
    return HttpResponse("title for %s." % todo.id)

