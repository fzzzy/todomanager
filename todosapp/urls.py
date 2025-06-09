from django.urls import path

from . import views
from . import auth_views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", auth_views.login_view, name="login"),
    path("signup/", auth_views.signup_view, name="signup"),
    path("logout/", auth_views.logout_view, name="logout"),
    path("<int:todo_id>/", views.detail, name="detail"),
    path("<int:todo_id>/set_state", views.set_state, name="set_state"),
    path("<int:todo_id>/update_title", views.update_title, name="update_title"),
    path("<int:todo_id>/delete", views.delete_todo, name="delete_todo"),
    path("vite/", views.vite_app, name="vite_app"),
    path("vite/<path:path>", views.vite_static, name="vite_static"),
]

