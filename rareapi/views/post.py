"""docstrings"""
import uuid
import base64
from django.http.response import HttpResponseServerError
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils import timezone
from rest_framework.viewsets import ViewSet
from rest_framework import serializers
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rareapi.models import Post, RareUser, Category, PostTag
from rareapi.views.category import CategorySerializer

class Posts(ViewSet):
    """docstrings"""

    def create(self, request):
        """Handle POST operations for posts"""
        author = RareUser.objects.get(user=request.auth.user)
        category = Category.objects.get(pk=request.data["category_id"])

        post = Post()

        post.category = category
        post.rareuser = author
        post.title = request.data["title"]
        post.publication_date = request.data["publication_date"]
        post.content = request.data["content"]
        post.selected_tags = request.data["selected_tags"]

        if author.is_staff:
            post.approved = True
        else:
            post.approved = False

        if request.data["post_img"] is not None:
            format, imgstr = request.data["post_img"].split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'"post_image"-{uuid.uuid4()}.{ext}')

            post.image_url = data

        try:
            post.save()
            serializer = PostSerializer(post, context={'request': request})
            #iterate selected tags and save relationships to database
            for tag in post.selected_tags:

                posttag = PostTag()
                posttag.tag_id = int(tag["id"])
                posttag.post_id = int(serializer.data["id"])

                posttag.save()
            return Response(serializer.data)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        """Handles GET request for posts by logged in user"""
        posts = Post.objects.all()
        current_user = RareUser.objects.get(user=request.auth.user)

        rareuser_id = self.request.query_params.get('rareuser_id', None)
        category_id = self.request.query_params.get('category_id', None)
        subscribed = self.request.query_params.get('subscribed', None)

        if rareuser_id is not None:
            author = RareUser.objects.get(user=rareuser_id)
            posts_by_author = posts.filter(
                rareuser=author, approved=True).order_by('-publication_date')

            serializer = PostSerializer(
                posts_by_author, many=True, context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        elif category_id is not None:
            category = Category.objects.get(id=category_id)
            posts = posts.filter(
                category=category).order_by('-publication_date')

        elif subscribed is not None:
            subscribed_posts = posts.filter(
                rareuser__subscribers__follower=current_user).order_by('-publication_date')

            serializer = SubscribedPostSerializer(
                subscribed_posts, many=True, context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        for post in posts:
            post.is_user_author = None
            if post.rareuser == current_user:
                post.is_user_author = True
            else:
                post.is_user_author=False

        serializer = PostSerializer(
            posts, many=True, context={'request': request}
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def retrieve(self, request, pk=None):
        """Handle GET request for single post
        Returns:
            Response JSON serielized post instance
        """
        try:
            post = Post.objects.get(pk=pk)

            post.is_user_author = None
            current_user = RareUser.objects.get(user=request.auth.user)
            
            if post.rareuser == current_user:
                post.is_user_author = True
            else:
                post.is_user_author=False

            serializer = PostSerializer(
                post, context={'request': request})
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests for posts"""
        author = RareUser.objects.get(user=request.auth.user)

        post = Post.objects.get(pk=pk)
        post.title = request.data["title"]
        post.publication_date = request.data["publication_date"]
        post.content = request.data["content"]
        post.rareuser = author

        category = Category.objects.get(pk=request.data["category_id"])
        post.category = category

        if request.data["post_img"] is not None:

            format, imgstr = request.data["post_img"].split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'"post_image"-{uuid.uuid4()}.{ext}')
            post.image_url = data

        post.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single post
        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            post = Post.objects.get(pk=pk)
            post.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Post.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['patch'], detail=True)
    def approval(self, request, pk=None):
        """Manages admins approving posts"""

        post = Post.objects.get(pk=pk)

        post.approved = not post.approved
        post.save()

        serializer = PostApprovalSerializer(
            post, context={'request': request}
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(methods=['patch'], detail=True)
    def publish(self, request, pk=None):
        """Manages users publishing and unpublishing posts"""

        post = Post.objects.get(pk=pk)

        if post.publication_date is not None:
            post.publication_date = None
            post.save()

            serializer = PostSerializer(post, context={'request': request})
            return Response(serializer.data)

        else:
            post.publication_date = timezone.now().today()
            post.save()

            serializer = PostSerializer(post, context={'request': request})
            return Response(serializer.data)


class AuthorSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for RareUser Info in a post"""
    class Meta:
        model = RareUser
        fields = ('id', 'is_staff', 'email', 'full_name')

class PostSerializer(serializers.HyperlinkedModelSerializer):
    """Basic Serializer for single post"""
    rareuser = AuthorSerializer(many=False)
    category = CategorySerializer(many=False)
    class Meta:
        model = Post
        fields = ('id', 'author_username', 'author_is_active',
        'title', 'publication_date', 'content', 'rareuser',
        'image_url', 'category', 'approved',
        'is_user_author', 'author_full_name')
        depth = 3

class PostApprovalSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Post Approval status"""
    class Meta:
        model = Post
        fields = ('id', 'approved')

class SubscribedPostSerializer(serializers.HyperlinkedModelSerializer):
    """Basic Serializer for single post"""
    rareuser = AuthorSerializer(many=False)
    category = CategorySerializer(many=False)
    class Meta:
        model = Post
        fields = ('id', 'author_username', 'author_is_active',
        'title', 'publication_date', 'content', 'rareuser',
        'image_url', 'category', 'category_id', 'approved',
        'is_user_author', 'author_full_name')
        depth = 3
