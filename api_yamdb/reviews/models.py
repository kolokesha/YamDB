from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .validators import validate_nums, validate_username, validate_year


class UserRole:
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'


class CustomUser(AbstractUser):
    USER_ROLES = (
        (UserRole.USER, 'User'),
        (UserRole.MODERATOR, 'Moderator'),
        (UserRole.ADMIN, 'Admin'),
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[validate_username, UnicodeUsernameValidator()],
    )
    role = models.CharField(
        choices=USER_ROLES,
        default=UserRole.USER,
        max_length=max([len(role[0]) for role in USER_ROLES]),
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)

    @property
    def is_admin(self):
        return self.is_superuser or self.role == UserRole.ADMIN

    @property
    def is_moderator(self):
        return self.role == UserRole.MODERATOR

    def save(self, *args, **kwargs):
        self.is_staff = self.is_admin
        super(CustomUser, self).save(*args, **kwargs)


User = get_user_model()


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, db_index=True)


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, db_index=True)


class Title(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    year = models.IntegerField(
        validators=[validate_year]
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True

    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles'
    )
    description = models.TextField(
        verbose_name='Описание', blank=True, null=True
    )


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    score = models.PositiveSmallIntegerField(validators=[validate_nums])
    pub_date = models.DateTimeField('Дата отзыва', auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title_id'
            )
        ]

    def __str__(self):
        return self.text


class Comments(models.Model):
    review_id = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    pub_date = models.DateTimeField('Дата комментария', auto_now_add=True)

    def __str__(self):
        return self.text
