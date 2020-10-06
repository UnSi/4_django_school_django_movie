from django import template
from movies.models import Category, Movie


register = template.Library()


@register.simple_tag()
def get_categories():
    """вывод категорий"""
    return Category.objects.all()


@register.inclusion_tag('movies/tags/last_movie.html')
def get_last_movies(count=5):
    """вывод категорий"""
    movies = Movie.objects.filter(draft=False).order_by("id")[:count]
    return {"last_movies": movies}
