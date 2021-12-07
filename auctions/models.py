from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields import CharField, IntegerField
from django.db.models.fields.related import ForeignKey
from django.db.models import Max


class User(AbstractUser):
    pass


class Listing(models.Model):
    title = CharField(max_length=100)
    description = CharField(max_length=200)
    start_price = IntegerField()
    owner_id = ForeignKey(User, on_delete=models.CASCADE)
    highest_bid = IntegerField(default=0)


class Bid(models.Model):
    amount = IntegerField()
    bidder_id = ForeignKey(User, on_delete=models.CASCADE)
    listing_id = ForeignKey(Listing, on_delete=models.CASCADE)

    def maximum_bid(self, id):
        return Bid.objects.filter(listing_id=id).aggregate(Max('amount'))


class Comment(models.Model):
    text = CharField(max_length=200)
    commenter_id = ForeignKey(User, on_delete=models.CASCADE)
    listing_id = ForeignKey(Listing, on_delete=models.CASCADE)

