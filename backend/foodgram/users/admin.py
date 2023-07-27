from django.contrib import admin

from .models import User, Subscription


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name',
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')
    ordering = ('username',)
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    empty_value_display = '-пусто-'
