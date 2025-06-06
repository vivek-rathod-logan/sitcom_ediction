from django.contrib import admin
from .models import *
@admin.register(count_user)
class CountUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'usercount', 'ip', 'country', 'device', 'session_key', 'created_at')
    search_fields = ('ip', 'country', 'device', 'session_key')
    list_filter = ('country', 'device', 'created_at')
    ordering = ('-created_at',)

admin.site.register(Comment)