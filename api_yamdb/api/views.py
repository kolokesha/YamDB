from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase

from reviews.models import Category, Genre, Review, Title, User
from .filters import TitleFilter
from .permissions import (AdminOnly, AdminOrReadOnly,
                          AuthorModeratorAdminOrReadOnly)
from .serializers import (AccessTokenObtainSerializer, CategorySerializer,
                          CommentsSerializer, ConfirmationCodeObtainSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleSerializerRead, TitleSerializerWrite,
                          UserSelfSerializer, UserSerializer)


class CreateListDeleteViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    pass


@api_view(['POST'])
@permission_classes([AllowAny])
def confirmation_code_obtain_view(request):
    serializer = ConfirmationCodeObtainSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email')
    username = serializer.validated_data.get('username')

    try:
        user = User.objects.get_or_create(
            email=email, username=username)[0]
    except IntegrityError:
        raise ValidationError({'detail': 'Занято имя или почта'})

    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Cofirmation Code',
        f'{confirmation_code}',
        settings.EMAIL,
        [f'{email}'],
        fail_silently=False,
    )
    return Response(serializer.validated_data, status=status.HTTP_200_OK)


class AccessTokenObtainView(TokenViewBase):
    serializer_class = AccessTokenObtainSerializer
    permission_classes = (AllowAny,)


class UserSelfView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSelfSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AdminOnly,)
    lookup_field = 'username'
    pagination_class = LimitOffsetPagination
    filter_backends = (SearchFilter,)
    search_fields = ('username',)


class CategoryGenreBaseViewSet(CreateListDeleteViewSet):
    permission_classes = (AdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CategoryGenreBaseViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class GenreViewSet(CategoryGenreBaseViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


class TitleViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).all()
    permission_classes = (AdminOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleSerializerRead
        return TitleSerializerWrite


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AuthorModeratorAdminOrReadOnly,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AuthorModeratorAdminOrReadOnly,)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(
            Review, pk=review_id, title__id=self.kwargs.get('title_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(
            Review, pk=review_id, title__id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, review_id=review)
