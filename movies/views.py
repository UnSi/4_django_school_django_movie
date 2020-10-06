from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.base import View

from .models import Movie, Category, Actor, Genre, Rating
from .forms import ReviewForm, RatingForm


class GenreYear():
    """Жанры и годы выхода"""
    def get_genres(self):
        return Genre.objects.all()

    def get_years(self):
        return Movie.objects.filter(draft=False).values("year").distinct()


class MoviesView(GenreYear, ListView):
    """Список фильмов"""
    model = Movie
    queryset = Movie.objects.filter(draft=False)
    paginate_by = 3

    # template_name = "movies/movies.html"

    # def get_context_data(self, *args, **kwargs):
    #     context = super().get_context_data(*args, **kwargs)
    #     context["categories"] = Category.objects.all()
    #     return context


class ActorView(GenreYear, DetailView):
    model = Actor
    template_name = "movies/actor.html"
    slug_field = "name"


class MovieDetailView(GenreYear, DetailView):
    """Полное описание фильма"""
    model = Movie
    queryset = Movie.objects.filter(draft=False)
    slug_field = 'url'

    def get_context_data(self, **kwargs):
        ip = AddStarRating.get_client_ip(self, self.request)
        movie_id = kwargs['object'].id
        stars = self.get_user_stars(ip, movie_id)

        context = super().get_context_data(**kwargs)
        context["star_form"] = RatingForm
        if stars:
            context['stars'] = str(stars)
        context['form'] = ReviewForm()

        return context

    def get_user_stars(self, ip, movie_id):
        if Rating.objects.filter(ip=ip, movie_id=movie_id).exists():
            stars = Rating.objects.get(ip=ip, movie_id=movie_id).star
        else:
            stars = None
        return stars

    # def get(self, request, *args, **kwargs):
    #
    #     ip = AddStarRating.get_client_ip(self, self.request)
    #     movie_id = Movie.objects.get(url=kwargs['slug']).id
    #     stars = self.get_user_stars(ip, movie_id)
    #
    #     # не нашёл, как передать в контекст через get, взял get родителя, перезаписал здесь
    #     self.object = self.get_object()
    #     context = self.get_context_data(object=self.object)
    #     if stars:
    #         context['stars'] = str(stars)
    #
    #     return self.render_to_response(context)


class AddReview(View):
    """отзывы"""
    def post(self, request, pk):
        form = ReviewForm(request.POST)
        movie = Movie.objects.get(id=pk)
        if form.is_valid():
            form = form.save(commit=False)
            if request.POST.get('parent', None):
                form.parent_id = int(request.POST.get('parent'))
            # form.movie_id = pk
            form.movie = movie
            form.save()
        return redirect(movie.get_absolute_url())


class FilterMoviesView(GenreYear, ListView):
    """Фильтр фильмов"""
    paginate_by = 2

    def get_queryset(self):
        year_list = self.request.GET.getlist("year")
        genre_list = self.request.GET.getlist("genre")

        if not year_list or not genre_list:
            queryset = Movie.objects.filter(Q(draft=False),
                Q(year__in=year_list) |
                Q(genres__in=genre_list)).distinct()
        else:
            queryset = Movie.objects.filter(draft=False,
                                            year__in=year_list,
                                            genres__in=genre_list).distinct()

        # TODO: сделать что-то более универсальное
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['year'] = ''.join([f'year={x}&' for x in self.request.GET.getlist('year')])
        print(context['year'])
        context['genre'] = ''.join([f'genre={x}&' for x in self.request.GET.getlist('genre')])
        return context


class JsonFilterMoviesView(ListView):
    """Фильтр фильмов"""
    def get_queryset(self):
        year_list = self.request.GET.getlist("year")
        genre_list = self.request.GET.getlist("genre")
        queryset = Movie.objects.filter(Q(draft=False),
                                        Q(year__in=year_list) |
                                        Q(genres__in=genre_list)
                                        ).distinct().values('title', 'tagline', 'url', 'poster')

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = list(self.get_queryset())
        return JsonResponse({"movies": queryset}, safe=False)


class AddStarRating(View):
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request):
        form = RatingForm(request.POST)
        if form.is_valid():
            Rating.objects.update_or_create(
                ip=self.get_client_ip(request),
                movie_id=int(request.POST.get("movie")),
                defaults={"star_id": int(request.POST.get("star"))}
            )
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=400)


class Search(ListView):
    """Поиск фильма"""

    paginate_by = 3

    def get_queryset(self):
        return Movie.objects.filter(title__icontains=self.request.GET.get("q"))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["q"] = ''.join(f'q={self.request.GET.get("q")}&')
        return context


'''
def test(request):
    return JsonResponse({
        1: 'asdfsd'
    })
'''