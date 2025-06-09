from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json

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

