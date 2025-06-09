import mimetypes
import os
from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404, HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json

from todos import settings

from .models import Todo


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
            # Handle form POST data
            title = request.POST.get('title')
        
        if title:
            todo = Todo.objects.create(title=title, pub_date=timezone.now())
            # Return JSON if client accepts JSON
            if request.headers.get('Accept') == 'application/json' or request.content_type == 'application/json':
                return JsonResponse({
                    'id': todo.id,
                    'title': todo.title,
                    'pub_date': todo.pub_date.isoformat()
                }, status=201)
            return redirect('index')
    
    todos = Todo.objects.order_by("-pub_date")[:5]
    
    # Return JSON if client accepts JSON
    if request.headers.get('Accept') == 'application/json':
        todos_data = [{
            'id': todo.id,
            'title': todo.title,
            'pub_date': todo.pub_date.isoformat()
        } for todo in todos]
        return JsonResponse({'todos': todos_data})
    
    context = {"todos": todos}
    return render(request, "todosapp/index.html", context)


def detail(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id)
    
    # Return JSON if client accepts JSON
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'id': todo.id,
            'title': todo.title,
            'pub_date': todo.pub_date.isoformat()
        })
    
    return HttpResponse("You're looking at todo %s." % todo.id)


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

