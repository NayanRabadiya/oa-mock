import logging

from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response

from movies.models import Movie
from movies.serializers import MovieSerializer

from .models import Watchlist
from .throttling import WatchlistOperationThrottle
from .validators import is_valid_movie_id

logger = logging.getLogger("moviedb")


def error(message, code):
    return Response({"message": message}, status=code)


@api_view(["GET"])
def get_watchlist(request):
    try:
        entries = Watchlist.objects.filter(user=request.user).select_related("movie").order_by("created_at", "id")
        movies = [entry.movie for entry in entries]
        return Response(MovieSerializer(movies, many=True).data)
    except Exception:
        logger.exception("Get watchlist error")
        return error("Server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@throttle_classes([WatchlistOperationThrottle])
def add_to_watchlist(request):
    try:
        movie_id = request.data.get("movieId")
        if not movie_id:
            return error("Movie ID is required", status.HTTP_400_BAD_REQUEST)
        if not is_valid_movie_id(movie_id):
            return error("Invalid movie ID format", status.HTTP_400_BAD_REQUEST)
        movie = Movie.objects.filter(pk=movie_id).first()
        if movie is None:
            return error("Movie not found", status.HTTP_404_NOT_FOUND)

        if Watchlist.objects.filter(user=request.user, movie=movie).exists():
            return error("Movie already in watchlist", status.HTTP_400_BAD_REQUEST)
        Watchlist.objects.create(user=request.user, movie=movie)

        return Response({"message": "Movie added to watchlist successfully"}, status=status.HTTP_201_CREATED)
    except IntegrityError:
        # the unique constraint is a second safety net against duplicates
        return error("Movie already in watchlist", status.HTTP_400_BAD_REQUEST)
    except Exception:
        logger.exception("Add to watchlist error")
        return error("Server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@throttle_classes([WatchlistOperationThrottle])
def remove_from_watchlist(request):
    try:
        movie_id = request.data.get("movieId")
        if not movie_id:
            return error("Movie ID is required", status.HTTP_400_BAD_REQUEST)
        if not is_valid_movie_id(movie_id):
            return error("Invalid movie ID format", status.HTTP_400_BAD_REQUEST)

        deleted, _ = Watchlist.objects.filter(user=request.user, movie_id=movie_id).delete()
        if not deleted:
            return error("Movie not found in watchlist", status.HTTP_404_NOT_FOUND)

        return Response({"message": "Movie removed from watchlist successfully"})
    except Exception:
        logger.exception("Remove from watchlist error")
        return error("Server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def check_watchlist_status(request, movie_id):
    try:
        if not is_valid_movie_id(movie_id):
            return error("Invalid movie ID format", status.HTTP_400_BAD_REQUEST)

        in_watchlist = Watchlist.objects.filter(user=request.user, movie_id=movie_id).exists()

        return Response({"isInWatchlist": in_watchlist})
    except Exception:
        logger.exception("Check watchlist status error")
        return error("Server error", status.HTTP_500_INTERNAL_SERVER_ERROR)
