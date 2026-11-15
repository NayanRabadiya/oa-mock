"""python manage.py seed: the movies and the two test users from the README. Safe to run again."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from movies.models import Movie

MOVIES = [
    ("65f0a1b2c3d4e5f600000001", "The Shawshank Redemption", 1994, "Drama"),
    ("65f0a1b2c3d4e5f600000002", "Interstellar", 2014, "Sci-Fi"),
    ("65f0a1b2c3d4e5f600000003", "The Dark Knight", 2008, "Action"),
    ("65f0a1b2c3d4e5f600000004", "Spirited Away", 2001, "Animation"),
    ("65f0a1b2c3d4e5f600000005", "Parasite", 2019, "Thriller"),
    ("65f0a1b2c3d4e5f600000006", "Inception", 2010, "Sci-Fi"),
]
USERS = [
    ("sam", "Sam Rivera", "sam.rivera@email.com"),
    ("alex", "Alex Chen", "alex.chen@email.com"),
]
PASSWORD = "Password@123"


class Command(BaseCommand):
    help = "Adds the sample movies and users."

    def handle(self, *args, **options):
        for movie_id, title, year, genre in MOVIES:
            Movie.objects.update_or_create(id=movie_id, defaults={"title": title, "year": year, "genre": genre})
        User = get_user_model()
        for username, name, email in USERS:
            user, _ = User.objects.get_or_create(username=username, defaults={"first_name": name, "email": email})
            user.set_password(PASSWORD)
            user.save()
        self.stdout.write("Seeded %d movies and %d users." % (len(MOVIES), len(USERS)))
