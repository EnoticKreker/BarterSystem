from django.contrib import admin
from .models import ExchangeProposal as Offer, Post
# Register your models here.


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'created', 'status',]
    list_filter = ['status', 'created', 'author']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'created'
    ordering = ['status', 'created']
    show_facets = admin.ShowFacets.ALWAYS

admin.site.register(Offer)
    
