from django.shortcuts import render
from django.views.generic import ListView, DetailView
from . import forms
from . import models
from django.core.paginator import Paginator

# Create your views here.
# def all_rooms(request):
#     page = request.GET.get("page",1)
#     room_list = models.Room.objects.all()

#     paginator = Paginator(room_list, 10,orphans=5)
#     try:
#         rooms = paginator.page(int(page))
#         context = {"page": rooms}
#         return render(request, "rooms/home.html", context)
#     except EmptyPage:
#         rooms = paginator.page(1)
#         return redirect("/")


class HomeView(ListView):
    """homeview def"""

    model = models.Room
    paginate_by = 10
    ordering = "created"
    paginate_orphans = 5
    page_kwarg = "page"
    context_object_name = "rooms"


# def room_detail(request,pk):
#     try:
#         room = models.Room.objects.get(pk=pk)
#         context = {'room':room}
#         return render(request,"rooms/detail.html",context)

#     except models.Room.DoesNotExist:
#         # return redirect(reverse("core:home"))
#         raise Http404


class RoomDetail(DetailView):
    """room detail def"""

    model = models.Room
    # 와;; 404.html을 자동으로 띄우네


def search(request):

    country = request.GET.get("country")

    if country:
        form = forms.SearchForm(request.GET)
        if form.is_valid():
            city = form.cleaned_data.get("city")
            country = form.cleaned_data.get("country")
            room_type = form.cleaned_data.get("room_type")
            price = form.cleaned_data.get("price")
            guests = form.cleaned_data.get("guests")
            bedrooms = form.cleaned_data.get("bedrooms")
            beds = form.cleaned_data.get("beds")
            baths = form.cleaned_data.get("baths")
            instant_book = form.cleaned_data.get("instant_book")
            superhost = form.cleaned_data.get("superhost")
            amenities = form.cleaned_data.get("amenities")
            facilities = form.cleaned_data.get("facilities")

            filter_args = {}

            if city != "Anywhere":
                filter_args["city__startswith"] = city

            filter_args["country"] = country

            if room_type is not None:
                filter_args["room_type"] = room_type

            if price is not None:
                filter_args["price__lte"] = price

            if guests is not None:
                filter_args["guests__gte"] = guests

            if bedrooms is not None:
                filter_args["bedrooms__gte"] = bedrooms

            if beds is not None:
                filter_args["beds__gte"] = beds

            if baths is not None:
                filter_args["beths__gte"] = baths

            if instant_book is True:
                filter_args["instant_book"] = True

            if superhost is True:
                filter_args["host__is_superhost"] = True

            for amenity in amenities:
                filter_args["amenities"] = amenity
                
            for facility in facilities:
                filter_args["facilities"] = facility

            qs = models.Room.objects.filter(**filter_args).order_by("-created")
            paginator = Paginator(qs, 10, orphans=5)
            page = request.GET.get("page", 1)
            rooms = paginator.get_page(page)

            return render(request, "rooms/search.html", {"form": form, "rooms": rooms})
    else:
        form = forms.SearchForm()
    
    return render(request, "rooms/search.html", {"form": form})
    # 요걸로 장난치는 사람이 있어요 그래서 랜더링을 해줘야 해요↑
