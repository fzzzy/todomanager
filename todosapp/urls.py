from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:todo_id>/", views.detail, name="detail"),
    path("vue/", views.vue_app, name="vue_app"),
    path("vue/<path:path>", views.vue_static, name="vue_static"),
]

