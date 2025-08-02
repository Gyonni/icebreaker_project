from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from .models import GameStatus

@admin.register(GameStatus)
class GameStatusAdmin(admin.ModelAdmin):
    change_list_template = "admin/config/gamestatus/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('toggle-3t1l/', self.toggle_3t1l_status, name='toggle_3t1l'),
            path('toggle-bingo/', self.toggle_bingo_status, name='toggle_bingo'),
        ]
        return custom_urls + urls

    def get_game_status(self):
        status, created = GameStatus.objects.get_or_create(pk=1)
        return status

    def toggle_3t1l_status(self, request):
        status = self.get_game_status()
        status.is_3t1l_active = not status.is_3t1l_active
        status.save()
        return HttpResponseRedirect("../")

    def toggle_bingo_status(self, request):
        status = self.get_game_status()
        status.is_bingo_active = not status.is_bingo_active
        status.save()
        return HttpResponseRedirect("../")

    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
