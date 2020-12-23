"""Post Model Module"""
from django.db import models
from . import RareUser, Category

class Post(models.Model):
    """Post Model"""
    rareuser = models.ForeignKey(
        RareUser, on_delete=models.CASCADE, related_name="posts")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=75)
    publication_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    image_url = models.ImageField(
        upload_to="headerimages", height_field=None,
        width_field=None, max_length=None, null=True, blank=True)
    content = models.CharField(max_length=5000)
    approved = models.BooleanField()

    @property
    def is_user_author(self):
        """Unmapped Prop"""
        return self.__is_user_author

    @property
    def author_full_name(self):
        """Unmapped Prop"""
        return self.rareuser.full_name

    @is_user_author.setter
    def is_user_author(self, value):
        """Unmapped Prop"""
        self.__is_user_author = value

    @property
    def author_username(self):
        """Unmapped Prop"""
        return self.rareuser.username

    @property
    def author_is_active(self):
        """Unmapped Prop"""
        return self.rareuser.is_active
