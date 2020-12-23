"""View module for handling requests about rareusers"""
from django.contrib.auth import get_user_model
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from rest_framework.decorators import action
from rareapi.models import RareUser, Subscription, Post, ProfileImage

class Users(ViewSet):
    """Users"""

    def list(self, request):
        """Handle GET requests to users resource
        Returns:
            Response -- JSON serialized list of users
        """
        rareusers = RareUser.objects.all()
        current_user = RareUser.objects.get(user=request.auth.user)

        for rareuser in rareusers:
            rareuser.is_current_user = None
            rareuser.subscribed = None

            try:
                Subscription.objects.get(
                    author=rareuser, follower=current_user, ended_on__isnull=True)
                rareuser.subscribed = True
            except Subscription.DoesNotExist:
                rareuser.subscribed = False

        user = RareUserSerializer(
            rareusers, many=True, context={'request': request})

        return Response(user.data)

    def retrieve(self, request, pk=None):
        """Handles GET requests to users resource for single User
        Written for User Profile View
        Returns:
            Response -- JSON serielized rareuser instance
        """
        try:
            rareuser = RareUser.objects.get(pk=pk)

            rareuser.is_current_user = None
            rareuser.subscribed = None
            current_user = RareUser.objects.get(user=request.auth.user)

            if current_user.id == int(pk):
                rareuser.is_current_user = True
            else:
                rareuser.is_current_user = False

            try:
                Subscription.objects.get(
                    author=rareuser, follower=current_user, ended_on__isnull=True)
                rareuser.subscribed = True
            except Subscription.DoesNotExist:
                rareuser.subscribed = False

            serializer = RareUserSerializer(
                rareuser, many=False, context={'request': request})

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        except RareUser.DoesNotExist:
            return Response(
                {'message': 'User does not exist.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=['get'], detail=False)
    def current_user(self, request):
        """docstrings"""
        current_user = RareUser.objects.get(user=request.auth.user)

        serializer = CurrentRareUserSerializer(
            current_user, context={'request': request})

        return Response(serializer.data)

    @action(methods=['patch'], detail=True)
    def change_type(self, request, pk=None):
        """docstrings"""
        user_obj = get_user_model()
        user_obj = user_obj.objects.get(pk=pk)

        user_obj.is_staff = not user_obj.is_staff
        user_obj.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    @action(methods=['patch'], detail=True)
    def change_active(self, request, pk=None):
        """docstrings"""

        user_obj = get_user_model()
        user_obj = user_obj.objects.get(pk=pk)

        user_obj.is_active = not user_obj.is_active
        user_obj.save()

        serializer = UserActiveSerializer(user_obj)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

class ImageSerializer(serializers.ModelSerializer):
    """JSON serializer for RareUser info in profile detail view"""
    class Meta:
        model = ProfileImage
        fields = ('id', 'image')

class UserActiveSerializer(serializers.ModelSerializer):
    """JSON serializer for RareUser info in profile detail view"""
    class Meta:
        model = get_user_model()
        fields = ('id', 'is_active')

class UsersPostsSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for rareusers Posts
    Arguments:
        serializers
    """
    class Meta:
        model = Post
        fields = ('id', 'title', 'url')

class FollowerSerializer(serializers.ModelSerializer):
    """JSON serializer for subscription follower and author related Django user"""
    class Meta:
        model = RareUser
        fields = ('id', 'username')

class AuthorSerializer(serializers.ModelSerializer):
    """JSON serializer for subscription follower and author related Django user"""
    posts = UsersPostsSerializer(many=True)
    class Meta:
        model = RareUser
        fields = ('id', 'username', 'posts')

class SubscriberSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for subscriptions"""
    follower = FollowerSerializer(many=False)
    class Meta:
        model = Subscription
        fields = ('id', 'follower', 'created_on', 'ended_on')

class SubscriptionSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for subscriptions"""
    author = AuthorSerializer(many=False)
    class Meta:
        model = Subscription
        fields = ('id', 'author', 'created_on', 'ended_on')

class RareUserSerializer(serializers.ModelSerializer):
    """JSON serializer for RareUser info in profile detail view"""
    posts = UsersPostsSerializer(many=True)
    subscribers = SubscriberSerializer(many=True)
    subscriptions = SubscriptionSerializer(many=True)
    images = ImageSerializer(many=True)
    class Meta:
        model = RareUser
        fields = ("id", "posts", 'subscribers', 'subscriptions',
            "bio", "is_staff", "is_active", "full_name", "images",
            "username", "email", "date_joined", "subscribed")

class CurrentRareUserSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for RareUser info in profile detail view"""
    posts = UsersPostsSerializer(many=True)

    class Meta:
        model = RareUser
        fields = ("id", "bio", "is_staff", "images",
            'posts', "is_active", "full_name",
            "username", "email", "date_joined")

class UserSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for rareusers
    Arguments:
        serializers
    """
    rareuser = RareUserSerializer(many=False)
    class Meta:
        model = get_user_model()
        fields = ('id', 'rareuser', 'username', "images", 'is_staff',
        'is_active', 'first_name', 'last_name', 'email', 'date_joined')
