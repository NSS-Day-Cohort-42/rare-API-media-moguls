"""docstrings"""
from django.conf.urls import include
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rareapi.views import register_user, login_user, Users
from rareapi.views import Subscriptions, Posts, Reactions, Comments
from rareapi.views import Tags, PostTags, Categories, ProfileImages

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'categories', Categories, 'category')
router.register(r'tags', Tags, 'tag')
router.register(r'comments', Comments, 'comment')
router.register(r'post_tags', PostTags, 'posttag')
router.register(r'posts', Posts, 'post')
router.register(r'users', Users, 'user')
router.register(r'reactions', Reactions, 'reaction')
router.register(r'subscriptions', Subscriptions, 'subscription')
router.register(r'profileimages', ProfileImages, 'profileimage')

urlpatterns = [
    path('', include(router.urls)),
    path('register', register_user),
    path('login', login_user),
    path('api-auth', include('rest_framework.urls', namespace='rest_framework')),
]

urlpatterns += static (settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
