from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models.fields import CharField, IntegerField
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import Bid, User, Listing


class NewListingForm(forms.Form):
    title = forms.CharField(max_length=100)
    description = forms.CharField(max_length=200)
    start_price = forms.IntegerField(initial=0)


class NewBidForm(forms.Form):
    amount = forms.IntegerField()


def index(request):
    listings = Listing.objects.all()

    return render(request, "auctions/index.html", {
        "listings": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)

        if form.is_valid():
            title = request.POST["title"]
            description = request.POST["description"]
            start_price = request.POST["start_price"]

            listing = Listing(title=title, description=description, start_price=start_price, owner_id=request.user, highest_bid=0)
            listing.save()

            return HttpResponseRedirect(reverse("index"))
        else: 
            return render(request, "auctions/create.html", {
                "form": form
            })
    else:
        return render(request, "auctions/create.html", {
            "form": NewListingForm()
        })


def listing(request, listing_id):
    if request.method == "POST":
        form = NewBidForm(request.POST)

        listing = Listing.objects.get(id=listing_id)

        if form.is_valid():
            amount = int(request.POST["amount"])

            start_price = listing.start_price
            highest_bid = listing.highest_bid

            if amount >= start_price and amount >= highest_bid:
                listing.highest_bid = amount
                listing.save()

                bid = Bid(amount=amount, bidder_id=request.user, listing_id=listing)
                bid.save()

                return HttpResponseRedirect(reverse("listing", args=[listing.id]))
            else: 
                return render(request, "auctions/listing.html", {
                "listing": listing,
                "form": NewBidForm(request.POST),
                "message": "Bid Higher Please"
            })
        else:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "form": NewBidForm(request.POST),
            })
    else:
        listing = Listing.objects.get(id=listing_id)

        return render(request, "auctions/listing.html", {
            "listing": listing,
            "form": NewBidForm()
        })

