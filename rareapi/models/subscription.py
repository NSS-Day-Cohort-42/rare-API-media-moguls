"""Subscription Model Module"""
from django.db import models
from . import RareUser

class Subscription(models.Model):
    """Subscription Model"""
    follower = models.ForeignKey(
        RareUser, on_delete=models.CASCADE, related_name='subscriptions')
    author = models.ForeignKey(
        RareUser, on_delete=models.CASCADE, related_name='subscribers')
    created_on = models.DateTimeField(auto_now_add=True)
    ended_on = models.DateTimeField(blank=True, null=True)

    @property
    def author_username(self):
        """This makes the username property accessible directly from the RareUser"""
        return self.author.username

    @property
    def follower_username(self):
        """This makes the username property accessible directly from the RareUser"""
        return self.follower.username
