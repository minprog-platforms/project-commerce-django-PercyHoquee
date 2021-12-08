from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import PROTECT
from django.db.models.fields import CharField, IntegerField
from django.db.models.fields.related import ForeignKey, ManyToManyField, OneToOneField
from django.db.models import Max


class User(AbstractUser):
    pass


class Listing(models.Model):
    title = CharField(max_length=100)
    description = CharField(max_length=200)
    start_price = IntegerField()
    owner = ForeignKey(User, on_delete=models.CASCADE)
    highest_bid = IntegerField(default=0)
    CHOICES = (
        ('a', 'active'),
        ('c', 'closed'),
    )
    status = CharField(max_length=1, choices=CHOICES, default="a")

    def set_maximum_bid(self):
        bids = self.bids.all()

        self.highest_bid = bids.aggregate(Max('amount'))["amount__max"]


class Bid(models.Model):
    amount = IntegerField()
    bidder = ForeignKey(User, on_delete=models.CASCADE)
    listing = ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")


class Comment(models.Model):
    text = CharField(max_length=200)
    commenter = ForeignKey(User, on_delete=models.CASCADE)
    listing = ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")


class Watchlist(models.Model):
    user = OneToOneField(User, on_delete=models.CASCADE)
    listings = ManyToManyField(Listing, blank=True)