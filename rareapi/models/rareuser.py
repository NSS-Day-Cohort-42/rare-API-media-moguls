"""RareUser Model Module"""
from django.db import models
from django.conf import settings

class RareUser(models.Model):
    """RareUser Model"""
    bio = models.CharField(max_length=500)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    @property
    def username(self):
        """This makes the username property accessible directly from the RareUser"""
        return self.user.username

    @property
    def is_staff(self):
        """This makes the is_staff property accessible directly from the RareUser"""
        return self.user.is_staff

    @property
    def is_active(self):
        """This makes the is_active property accessible directly from the RareUser"""
        return self.user.is_active

    @property
    def email(self):
        """This makes the email property accessible directly from the RareUser"""
        return self.user.email

    @property
    def full_name(self):
        """This makes the first and last name
        properties accessible directly from the RareUser
        as the full_name property"""
        return (f'{self.user.first_name} {self.user.last_name}')

    @property
    def date_joined(self):
        """This makes the date_joined property accessible directly from the RareUser"""
        return self.user.date_joined

    @property
    def is_current_user(self):
        """This unmapped property has a boolean value"""
        return self.__is_current_user

    @is_current_user.setter
    def is_current_user(self, value):
        """This allows the is_current_user property to be set"""
        self.__is_current_user = value

    @property
    def subscribed(self):
        """Unmapped Prop"""
        return self.__subscribed

    @subscribed.setter
    def subscribed(self, value):
        """Unmapped Prop"""
        self.__subscribed = value
