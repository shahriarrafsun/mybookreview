from django.contrib import admin
from .models import Author, Book, Featured
# Register your models here.


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'birth_year', 'death_year')
    list_filter = ('birth_year',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('writer', 'title', 'published_date')
    list_filter = ('writer', 'published_date',)


@admin.register(Featured)
class FeaturedAdmin(admin.ModelAdmin):
    list_display = ('book',)
