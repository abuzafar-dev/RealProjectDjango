from django.contrib import admin

from blog.models import Category, Comment, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug']
    prepopulated_fields = {'slug': ['name']}


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'category', 'views', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'text']
    inlines = [CommentInline]
