from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientsViewSet, RecipeViewSet,
                    TagsViewSet)

router_v1 = DefaultRouter()

router_v1.register(r'recipes', RecipeViewSet, basename='recipe')
router_v1.register(r'users', CustomUserViewSet, basename='user')
router_v1.register(r'tags', TagsViewSet, basename='tag')
router_v1.register(r'ingredients', IngredientsViewSet, basename='ingredient')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
