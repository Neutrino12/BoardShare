from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserDetails(models.Model):
    user = models.OneToOneField(User, primary_key=True, related_name='user')
    gender = models.CharField(max_length=60)
    about_me = models.CharField(max_length=255)
    follows = models.ManyToManyField('self', related_name='followers', symmetrical=False)
    num_pins = models.IntegerField(default = 0)
    num_boards = models.IntegerField(default = 0)
    num_followers = models.IntegerField(default = 0)
    num_followings = models.IntegerField(default = 0)
    data_local = models.ImageField(upload_to="media/user/")
    def __unicode__(self):
        return "About Me: %s" % about_me


class Board(models.Model):
    title = models.CharField(max_length=60)
    description = models.CharField(max_length=200)
    category = models.CharField(max_length=60) #models.ForeignKey(Category, blank=False)
    user = models.ForeignKey(User, blank=False) 
    def __unicode__(self):
        return self.description


class Pin(models.Model):
    data_type = models.CharField(max_length=60)
    num_likes = models.IntegerField(default = 0)
    board = models.ManyToManyField(Board, blank=False, null=False)
    user = models.ForeignKey(User, blank=False)
    board_title = models.CharField(max_length=60)
    data_local = models.ImageField(upload_to="media/pin/")
    data_text = models.CharField(max_length=255)
    def __unicode__(self):
        return self.data_text

class Comments(models.Model):
    content = models.CharField(max_length=255)
    pin = models.ForeignKey(Pin, blank=False) 
    user = models.ForeignKey(User, blank=False) 
    def __unicode__(self):
        return self.content
		

