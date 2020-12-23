"""docstrings"""
# https://www.base64-image.de/ for image encoding and postman tests

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
from rareapi.models import ProfileImage, RareUser

class ProfileImages(ViewSet):
    """docstrings"""

    def create(self, request):
        """docstrings"""
        profile_image = ProfileImage()

        format, imgstr = request.data["image"].split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name=f'"image"-{uuid.uuid4()}.{ext}')

        profile_image.image = data

        profile_image.save()
        serializer = ProfileImageSerializer(profile_image, context={'request': request})

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


    def list(self, request):
        """Handles GET request for posts by logged in user"""
        images = ProfileImage.objects.all()

        serializer = ProfileImageSerializer(
            images, many=True, context={'request': request}
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def retrieve(self, request, pk=None):
        """Handle PUT requests for posts"""
        try:
            profile_image = ProfileImage.objects.get(pk=pk)

            serializer = ProfileImageSerializer(
                profile_image, context={'request': request})

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        except Exception as ex:
            return HttpResponseServerError(ex)

    @action(methods=['patch'], detail=True)
    def savetoprofile(self, request, pk=None):
        """Manages admins approving posts"""

        user_profile = RareUser.objects.get(user=request.auth.user)
        profile_image = ProfileImage.objects.get(pk=pk)

        profile_image.profile = user_profile

        profile_image.save()

        serializer = ProfileImageSerializer(
            profile_image, context={'request': request}
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single post
        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            profile_image = ProfileImage.objects.get(pk=pk)
            profile_image.delete()

            return Response(
                {},
                status=status.HTTP_204_NO_CONTENT
            )

        except ProfileImage.DoesNotExist as ex:
            return Response(
                {'message': ex.args[0]},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as ex:
            return Response(
                {'message': ex.args[0]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProfileImageSerializer(serializers.ModelSerializer):
    """Serializer for ProfileImage """
    class Meta:
        model = ProfileImage
        fields = ('id', 'image', 'profile')

