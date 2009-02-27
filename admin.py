from django.contrib import admin
from blogy.models import Post, Series


class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title', )}
    list_display = ('title', 'author', 'is_draft', 'enable_comments',
                    'created_on', 'updated_on', 'published_on', 
                    'tags', 'series')
    search_fields = ('title', 'raw_text')
    list_filter = ('published_on', 'created_on', 'updated_on', 'is_draft')

class SeriesAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title', )}
    search_fields = ('title', )
    list_filter = ('created_on', 'updated_on')

admin.site.register(Post, PostAdmin)
admin.site.register(Series, SeriesAdmin)
