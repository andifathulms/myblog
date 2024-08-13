from django.contrib.auth.models import AbstractUser
from django.db import models

from model_utils import Choices
from model_utils.fields import AutoCreatedField


class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=30, db_index=True, blank=True, null=True)
    email = models.EmailField(blank=True, null=True, max_length=254, db_index=True)

    GENDER = Choices(
        (1, "male", 'Male'),
        (2, "female", 'Female')
    )
    gender = models.PositiveSmallIntegerField(choices=GENDER)

    is_active = models.BooleanField(default=True)
    created = AutoCreatedField()
