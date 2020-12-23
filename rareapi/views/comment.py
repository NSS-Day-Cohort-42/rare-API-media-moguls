"""View module for handling requests about comments"""
from django.core.exceptions import ValidationError
from rest_framework import status
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from rareapi.models import Comment, RareUser, Post


class Comments(ViewSet):
    """Rare comments"""

    def create(self, request):

        author = RareUser.objects.get(user=request.auth.user)
        post = Post.objects.get(pk=request.data["post_id"])

        comment = Comment()
        comment.post = post
        comment.author = author
        comment.content = request.data["content"]
        comment.subject = request.data["subject"]

        try:
            comment.save()
            serializer = CommentSerializer(comment, context={'request': request})
            return Response(serializer.data)

        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single comment

        """
        try:
            comment = Comment.objects.get(pk=pk)
            serializer = CommentSerializer(comment, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """Handle GET requests to comments resource

        Returns:
            Response -- JSON serialized list of comments
        """
        comments = Comment.objects.all()

        # Support filtering comments by post
        post = self.request.query_params.get('post_id', None)
        if post is not None:
            comments = comments.filter(post_id=post)

        for comment in comments:
            comment.is_user_author = None
            current_rareuser = RareUser.objects.get(user=request.auth.user)
            if comment.author == current_rareuser:
                comment.is_user_author = True
            else:
                comment.is_user_author=False

        serializer = CommentSerializer(
            comments, many=True, context={'request': request})
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Handle PUT requests for a comment

        Returns:
            Response -- Empty body with 204 status code
        """
        author = RareUser.objects.get(user=request.auth.user)
        post = Post.objects.get(pk=request.data["post_id"])

        comment = Comment.objects.get(pk=pk)
        comment.post = post
        comment.author = author
        comment.content = request.data["content"]
        comment.subject = request.data["subject"]

        comment.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single comment

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            comment = Comment.objects.get(pk=pk)
            comment.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Comment.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CommentAuthorSerializer(serializers.ModelSerializer):
    """JSON serializer for post author's related Django user"""
    class Meta:
        model = RareUser
        fields = ['id', 'username']

class PostSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for post"""
    class Meta:
        model = Post
        fields = ['id', 'title']

class CommentSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for comments"""
    author = CommentAuthorSerializer(many=False)
    post = PostSerializer(many=False)

    class Meta:
        model = Comment
        url = serializers.HyperlinkedIdentityField(
            view_name='comment',
            lookup_field='id'
        )
        fields = ('id', 'post', 'author',
                'content', 'subject', 'created_on', 'is_user_author')