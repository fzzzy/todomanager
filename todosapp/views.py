from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.utils import timezone

from .models import Todo


def index(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            Todo.objects.create(title=title, pub_date=timezone.now())
            return redirect('index')
    
    todos = Todo.objects.order_by("-pub_date")[:5]
    context = {"todos": todos}
    return render(request, "todosapp/index.html", context)



def detail(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id)
    return HttpResponse("You're looking at todo %s." % todo.id)

