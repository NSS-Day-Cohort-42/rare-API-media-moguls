"""View module for handling requests about posttags"""
import datetime
from django.http import HttpResponseServerError
from django.core.exceptions import ValidationError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import serializers
from rest_framework import status
from rareapi.models import Subscription, RareUser

class Subscriptions(ViewSet):
    """Rare subscriptions"""

    def list(self, request):
        """Handle GET requests to get all active subscriptions
        for a given author
        """
        current_user = RareUser.objects.get(user=request.auth.user)
        subscriptions = Subscription.objects.filter(ended_on__isnull=True)
        author_id = self.request.query_params.get('author', None)
        subscribed_to_author = self.request.query_params.get('followers', None)

        if author_id is not None:
            author = RareUser.objects.get(user__id=author_id)
            if author != current_user:
                try:
                    subscription = subscriptions.get(
                        author=author, follower=current_user)

                    serializer = SubscribedToAuthorSerializer(
                        subscription, many=False, context={'request': request}
                    )

                    return Response(
                        serializer.data,
                        status=status.HTTP_200_OK
                    )

                except Subscription.DoesNotExist:
                    return Response(
                        {'message': 'You are not subscribed to this author.'},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY
                    )
            elif author == current_user:
                return Response(
                    {'reason': 'Users cannot subscribe to their own profile.'},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )

        elif subscribed_to_author is not None:
            author = RareUser.objects.get(user__id=subscribed_to_author)

            subscribers = subscriptions.filter(author=author, ended_on=None)

            serializer = UsersSubscribersSerializer(
                subscribers, many=True, context={'request': request})
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        serializer = SubscriptionSerializer(
            subscriptions, many=True, context={'request': request})
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


    @action(methods=['get', 'post', 'patch'], detail=True)
    # Adds an ended_on for an active subscription between a follower and author
    def manage(self, request, pk):
        """docstrings"""

        if request.method == "PATCH":
            follower = RareUser.objects.get(user=request.auth.user)
            author = RareUser.objects.get(pk=pk)

            try:
                subscription = Subscription.objects.get(author=author, follower=follower)

                if subscription.ended_on is None:
                    subscription.ended_on = datetime.datetime.now()
                    subscription.save()

                    return Response(
                        {'message': 'unsubscribed'},
                        status=status.HTTP_200_OK
                    )

                elif subscription.ended_on is not None:
                    subscription.ended_on = None
                    subscription.save()

                    return Response(
                        {'message': 'subscribed'},
                        status=status.HTTP_200_OK
                    )

            except Subscription.DoesNotExist:

                if follower != author:
                    subscription = Subscription()
                    subscription.follower = follower
                    subscription.author = author

                    try:
                        subscription.save()

                        serializer = SubscriptionSerializer(
                            subscription,
                            context={'request': request}
                        )

                        return Response(
                            serializer.data,
                            status=status.HTTP_201_CREATED
                        )

                    except ValidationError as ex:
                        return Response(
                            {"reason": ex.message},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    return Response(
                        {"reason": "user cannot subscribe to their own posts"},
                        status=status.HTTP_422_UNPROCESSABLE_ENTITY
                    )

        return Response({}, status=status.HTTP_204_NO_CONTENT)

class FollowerSerializer(serializers.ModelSerializer):
    """JSON serializer for subscription follower and author related Django user"""
    class Meta:
        model = RareUser
        fields = ('id', 'username', 'is_active',
            'is_staff', 'email', 'full_name')

class FollowerUsernameSerializer(serializers.ModelSerializer):
    """JSON serializer for subscription follower and author related Django user"""
    class Meta:
        model = RareUser
        fields = ('id', 'username')

class AuthorSerializer(serializers.ModelSerializer):
    """JSON serializer for subscription follower and author related Django user"""
    class Meta:
        model = RareUser
        fields = ('id', 'username', 'is_active',
            'is_staff', 'email', 'full_name')

class SubscriptionSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for subscriptions"""
    follower = FollowerSerializer(many=False)
    author = AuthorSerializer(many=False)
    class Meta:
        model = Subscription
        fields = ('id', 'follower', 'author',
            'created_on', 'ended_on')

class SubscribedToAuthorSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for subscriptions"""
    author = AuthorSerializer(many=False)
    follower = FollowerUsernameSerializer(many=False)
    class Meta:
        model = Subscription
        fields = ('id', 'author', 'created_on',
        'follower', 'ended_on')

class UsersSubscribersSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for subscriptions"""
    follower = FollowerSerializer(many=False)
    class Meta:
        model = Subscription
        fields = ('id', 'follower', 'author_username', 'created_on', 'ended_on')
