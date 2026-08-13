from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.auth import CustomAuthToken, LogoutView
from api.views.ingredients import IngredientViewSet
from api.views.recipes import RecipeViewSet
from api.views.tags import TagViewSet
from api.views.users import UserViewSet

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags'),
router.register('ingredients', IngredientViewSet, basename='ingredients'),
router.register('recipes', RecipeViewSet, basename='recipes'),
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/login', CustomAuthToken.as_view(), name='login'),
    path('auth/token/logout', LogoutView.as_view(), name='logout'),
]
