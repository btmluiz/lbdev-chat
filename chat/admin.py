from django.contrib import admin

# Register your models here.
from chat import models

admin.site.register(models.Chat)
admin.site.register(models.ChatSession)
admin.site.register(models.ChatHistory)
