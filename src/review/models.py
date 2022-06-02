# Create your models here.
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models
from PIL import Image
from os import path


class Ticket(models.Model):
    # Your Ticket model definition goes here
    objects = models.Manager()
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    time_created = models.DateTimeField(auto_now_add=True)

    IMAGE_MAX_SIZE = (800, 800)

    def __str__(self):
        return f" {self.title} - {self.user}"

    def resize_image(self):
        image = Image.open(self.image)
        image.thumbnail(self.IMAGE_MAX_SIZE)
        image.save(self.image.path)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.resize_image()


class Review(models.Model):
    objects = models.Manager()
    ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        # validates that rating must be between 0 and 5
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    headline = models.CharField(max_length=128)
    body = models.CharField(max_length=8192, blank=True)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)


class UserFollows(models.Model):
    # Your UserFollows model definition goes here
    objects = models.Manager()
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    followed_user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followed_by')

    class Meta:
        # ensures we don't get multiple UserFollows instances
        # for unique user-user_followed pairs
        unique_together = (
            "user",
            "followed_user",
        )


"""
class User(AbstractUser):
    CREATOR = "CREATOR"
    SUBSCRIBER = "SUBSCRIBER"

    ROLE_CHOICES = (
        (CREATOR, "Créateur"),
        (SUBSCRIBER, "Abonné"),
    )
    profile_photo = models.ImageField(verbose_name="photo de profil")
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, verbose_name="rôle")

    follows = models.ManyToManyField(
        "self",
        limit_choices_to={"role": CREATOR},
        symmetrical=False,
        verbose_name="suit",
    )

"""
