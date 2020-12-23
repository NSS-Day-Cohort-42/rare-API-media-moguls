"""Comment Model Module"""
from django.db import models
from . import RareUser, Post

class Comment(models.Model):
    """Comment Model"""
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        RareUser, on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=500)
    subject = models.CharField(max_length=50)
    created_on = models.DateTimeField(auto_now_add=True)

    @property
    def is_user_author(self):
        """Unmapped Prop"""
        return self.__is_user_author

    @is_user_author.setter
    def is_user_author(self, value):
        """Unmapped Prop"""
        self.__is_user_author = value
