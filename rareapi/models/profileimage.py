"""ProfileImage Model Module"""
from django.db import models

class ProfileImage(models.Model):
    """ProfileImage Model"""
    image = models.ImageField(
        upload_to="images/", blank=True, null=True)
    profile = models.ForeignKey(
        "RareUser", on_delete=models.CASCADE, related_name="images", blank=True, null=True)
