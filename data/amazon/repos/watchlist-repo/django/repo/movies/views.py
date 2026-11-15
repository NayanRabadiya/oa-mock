from django.db.models import Avg
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Movie, Rating
from .serializers import MovieSerializer


@api_view(["GET"])
def list_movies(request):
    return Response(MovieSerializer(Movie.objects.order_by("title"), many=True).data)


@api_view(["GET"])
def movie_detail(request, movie_id):
    movie = Movie.objects.filter(pk=movie_id).first()
    if movie is None:
        return Response({"message": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)
    data = MovieSerializer(movie).data
    avg = movie.ratings.aggregate(avg=Avg("stars"))["avg"]
    data["averageRating"] = int(avg) if avg is not None else None
    data["ratingsCount"] = movie.ratings.count()
    return Response(data)


@api_view(["POST"])
def rate_movie(request, movie_id):
    movie = Movie.objects.filter(pk=movie_id).first()
    if movie is None:
        return Response({"message": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)
    stars = request.data.get("stars")
    if not isinstance(stars, int) or not 1 <= stars <= 5:
        return Response({"message": "Stars must be a whole number from 1 to 5"}, status=status.HTTP_400_BAD_REQUEST)
    Rating.objects.update_or_create(movie=movie, user=request.user,
                                    defaults={"stars": stars, "review": request.data.get("review", "")})
    return Response({"message": "Rating saved"}, status=status.HTTP_201_CREATED)
