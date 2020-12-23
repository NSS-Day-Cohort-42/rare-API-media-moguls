"""PostReaction Model Module"""
from django.db import models

class PostReaction(models.Model):
    """PostReaction Model"""
    reaction = models.ForeignKey("Reaction", on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey("RareUser", on_delete=models.CASCADE, related_name="likes")
