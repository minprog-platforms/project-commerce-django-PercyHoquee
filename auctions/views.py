from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models.fields import CharField, IntegerField
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.db.models import Max

from .models import Bid, User, Listing, Watchlist, Comment


class NewListingForm(forms.Form):
    title = forms.CharField(max_length=100)
    description = forms.CharField(max_length=200)
    start_price = forms.IntegerField(initial=0)


class NewBidForm(forms.Form):
    amount = forms.IntegerField()

class NewCommentForm(forms.Form):
    text = forms.CharField(max_length=200)


def index(request):
    listings = Listing.objects.filter(status="a")

    return render(request, "auctions/index.html", {
        "listings": listings,
        "active": "Active Listings"
    })


def closed(request):
    listings = Listing.objects.filter(status="c")

    return render(request, "auctions/index.html", {
        "listings": listings,
        "closed": "Closed Listings"
    })


def watchlist(request):
    watchlist = Watchlist.objects.get(user=request.user) 

    listings = watchlist.listings.all()

    return render(request, "auctions/index.html", {
        "listings": listings,
        "watchlist": "Watchlist"
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

            watchlist = Watchlist(user=user)
            watchlist.save()
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

            listing = Listing(title=title, description=description, start_price=start_price, owner=request.user, highest_bid=0)
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
    listing = Listing.objects.get(id=listing_id)

    listing.set_maximum_bid()

    watchlist = Watchlist.objects.get(user=request.user)

    watchlist_items = watchlist.listings.all()

    if listing in watchlist_items:
        listed = True
    else:
        listed = False

    owner_id = listing.owner.id

    highest_amount = listing.bids.all().aggregate(Max('amount'))["amount__max"]

    if highest_amount != None:
        highest_bid = Bid.objects.get(amount=highest_amount)

        highest_bidder = highest_bid.bidder.id
    else:
        highest_bidder = None

    comments = listing.comments.all()

    if request.method == "POST":
        form = NewBidForm(request.POST)

        if form.is_valid():
            amount = int(request.POST["amount"])

            start_price = listing.start_price
            highest_bid = listing.highest_bid

            if (amount >= start_price and highest_bid == None) or (amount >= start_price and amount > highest_bid):
                listing.highest_bid = amount
                listing.save()

                bid = Bid(amount=amount, bidder=request.user, listing=listing)
                bid.save()

                return HttpResponseRedirect(reverse("listing", args=[listing.id]))
            else: 
                return render(request, "auctions/listing.html", {
                "listing": listing,
                "form": NewBidForm(request.POST),
                "listed": listed,
                "owner_id": owner_id,
                "highest_bidder": highest_bidder,
                "comments": comments,
                "comment_form": NewCommentForm(),
                "message": "Bid Higher Please"
            })
        else:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "form": NewBidForm(request.POST),
                "listed": listed,
                "highest_bidder": highest_bidder,
                "comments": comments,
                "comment_form": NewCommentForm(),
                "owner_id": owner_id
            })
    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "form": NewBidForm(),
            "listed": listed,
            "highest_bidder": highest_bidder,
            "comments": comments,
            "comment_form": NewCommentForm(),
            "owner_id": owner_id
        })


def add(request, listing_id):
    watchlist = Watchlist.objects.get(user=request.user)

    listing = Listing.objects.get(id=listing_id)

    watchlist.listings.add(listing)

    return HttpResponseRedirect(reverse("listing", args=[listing.id]))


def remove(request, listing_id):
    watchlist = Watchlist.objects.get(user=request.user)

    listing = Listing.objects.get(id=listing_id)

    watchlist.listings.remove(listing)

    return HttpResponseRedirect(reverse("listing", args=[listing.id]))


def close_listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)

    listing.status = "c"
    listing.save()

    return HttpResponseRedirect(reverse("listing", args=[listing.id]))


def comment(request, listing_id):
    text = request.POST["text"]

    listing = Listing.objects.get(id=listing_id)

    comment = Comment(text=text, commenter=request.user, listing=listing)
    comment.save()

    return HttpResponseRedirect(reverse("listing", args=[listing.id]))



