from django.urls import include, path
from rest_framework import routers

from .views import (AccessTokenObtainView, CategoryViewSet, CommentsViewSet,
                    GenreViewSet, ReviewViewSet, TitleViewSet, UserSelfView,
                    UserViewSet, confirmation_code_obtain_view)

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet, basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet, basename='comments')
router.register('categories', CategoryViewSet, basename='category')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')
router.register(r'titles/(?P<title_id>\d+)', TitleViewSet, basename='titles')


urlpatterns = [
    path(
        'v1/auth/signup/',
        confirmation_code_obtain_view,
        name='get_confirm_code'
    ),
    path(
        'v1/auth/token/',
        AccessTokenObtainView.as_view(),
        name='token_obtain'
    ),
    path(
        'v1/users/me/',
        UserSelfView.as_view(),
        name='user-me'
    ),
    path('v1/', include(router.urls)),
]
