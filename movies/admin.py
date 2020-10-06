from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from modeltranslation.admin import TranslationAdmin

from .models import Category, Genre, Movie, MovieShots, Rating, RatingStar, Reviews, Actor
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class MovieAdminForm(forms.ModelForm):
    description_ru = forms.CharField(label='Описание', widget=CKEditorUploadingWidget())
    description_en = forms.CharField(label='Описание', widget=CKEditorUploadingWidget())
    # поле модели, куда будет применяться виджет

    class Meta:
        model = Movie
        fields = '__all__'


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    """категории"""

    list_display = ('id', 'name', 'url')
    list_display_links = ('id', 'name')


class ReviewInLine(admin.TabularInline):
    """отзывы на странице фильмов"""
    model = Reviews
    extra = 1
    readonly_fields = ('email', 'name')


class MovieShotsInLine(admin.TabularInline):
    """кадры на странице фильмов"""
    model = MovieShots
    extra = 1
    readonly_fields = ("get_image",)

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="100" height="110"')

    get_image.short_description = 'Изображение'


@admin.register(Movie)
class MovieAdmin(TranslationAdmin):
    """фильмы"""
    list_display = ('id', 'title', 'year', 'world_premiere', 'category', 'url', 'draft')
    list_display_links = ('title',)
    list_filter = ('category', 'year')
    search_fields = ('title', 'category__name')
    inlines = [MovieShotsInLine, ReviewInLine]
    save_on_top = True
    save_as = True
    list_editable = ('draft',)
    actions = ['publish', 'unpublish']
    form = MovieAdminForm
    # fields = (("actors", "directors", "genres"),)
    readonly_fields = ('get_image',)
    fieldsets = (
        (None, {
            "fields": (("title", "tagline"),)
        }),
        (None, {
            "fields": (("description", "poster", "get_image"),)
        }),
        (None, {
            "fields": (("year", "world_premiere", "country"),)
        }),
        ("Actors", {
            "classes": ("collapse",),
            "fields": (("actors", "directors", "genres", "category"),)
        }),
        (None, {
            "fields": (("budget", "fees_in_usa", "fees_in_world"),)
        }),
        ('Options', {
            "fields": (("url", "draft"),)
        }),

    )

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.poster.url} width="100" height="110"')

    def unpublish(self, request, queryset):
        """Снять с публикации"""
        row_update = queryset.update(draft=True)
        if row_update == 1:
            message_bit = "1 запись была обновлена"
        else:
            message_bit = f"{row_update} записей были обновлены"
        self.message_user(request, f"{message_bit}")

    def publish(self, request, queryset):
        """Опубликовать"""
        row_update = queryset.update(draft=False)
        if row_update == 1:
            message_bit = "1 запись была обновлена"
        else:
            message_bit = f"{row_update} записей были обновлены"
        self.message_user(request, f"{message_bit}")

    publish.short_description = 'Опубликовать'
    publish.allowed_permissions = ('change',)

    unpublish.short_description = 'Снять с публикации'
    unpublish.allowed_permissions = ('change',)


    get_image.short_description = 'Постер'


@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    """отзывы"""
    list_display = ('name', 'email', 'parent', 'movie', 'id')
    readonly_fields = ('name', 'email')


@admin.register(Actor)
class ActorAdmin(TranslationAdmin):
    """отзывы"""
    list_display = ('name', 'age', 'get_image')
    readonly_fields = ('get_image',)

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="50" height="60"')

    get_image.short_description = 'Изображение'


@admin.register(Genre)
class GenreAdmin(TranslationAdmin):
    """жанры"""
    list_display = ('name', 'url')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """рейтинг"""
    list_display = ('star', 'movie', 'ip')


@admin.register(MovieShots)
class MovieShotsAdmin(TranslationAdmin):
    """кадры из фильма"""
    list_display = ('title', 'movie')


# admin.site.register(Category, CategoryAdmin)
# admin.site.register(Genre)
# admin.site.register(Movie, MovieAdmin)
# admin.site.register(MovieShots)
# admin.site.register(Actor)
# admin.site.register(Rating)
admin.site.register(RatingStar)
# admin.site.register(Reviews)

admin.site.site_title = "Django movies"
admin.site.site_header = "Django movies"
