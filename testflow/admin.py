from django.contrib import admin
from .models import ResetPasswordRequest

# Register your models here.

@admin.register(ResetPasswordRequest)
class ResetPasswordRequestAdmin(admin.ModelAdmin):
	list_display = ['userEmail', 'request_at','updated_at', 'encryptCode', 'user','verified']
