from django.contrib import admin
from .models import UserToken

class UserTokenAdmin(admin.ModelAdmin):
    readonly_fields = ('user', 'token', 'created_at', 'used')

admin.site.register(UserToken, UserTokenAdmin)