from django.contrib import admin
from .models import Post, Page, UserProfile, Industry

# Register your models here.


class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')


admin.site.register(Post)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)
admin.site.register(Industry)