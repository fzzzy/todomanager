from django.contrib import admin

from .models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'state', 'pub_date')
    list_filter = ('state', 'pub_date', 'user')
    search_fields = ('title', 'user__username')
    readonly_fields = ('pub_date',)

