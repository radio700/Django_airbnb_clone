from django.shortcuts import render

# from django.urls.base import reverse
# from django.core.paginator import EmptyPage, Paginator
from django.views.generic import ListView, DetailView

# from django.utils import timezone
# from django.http import Http404
from django_countries import countries


from . import models

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
    city = request.GET.get("city", "Anywhere")
    # anywhere는 파라미터가 아예 없을떄 뜸
    city = str.capitalize(city)
    country = request.GET.get("country", "KR")
    room_type = int(request.GET.get("room_type", 0))
    price = int(request.GET.get("price", 0))
    guests = int(request.GET.get("guests", 0))
    bedrooms = int(request.GET.get("bedrooms", 0))
    beds = int(request.GET.get("beds", 0))
    baths = int(request.GET.get("baths", 0))
    instant = request.GET.get("instant", False)
    super_host = request.GET.get("super_host", False)
    print(f"인스턴트,슈퍼호스트 + {instant}, {super_host}")
    s_amenities = request.GET.getlist("amenities")
    s_facilities = request.GET.getlist("facilities")
    print(f"어메니티,퍼실리티 + {s_amenities}, {s_facilities}")

    form = {
        "city": city,
        "s_room_type": room_type,
        "s_country": country,
        "price": price,
        "guests": guests,
        "bedrooms": bedrooms,
        "beds": beds,
        "baths": baths,
        "instant": instant,
        "super_host": super_host,
        "s_amenities": s_amenities,
        "s_facilities": s_facilities,
    }
    room_types = models.RoomType.objects.all()
    amenities = models.Amenity.objects.all()
    facilities = models.Facility.objects.all()

    choices = {
        "countries": countries,
        "room_types": room_types,
        "amenities": amenities,
        "facilities": facilities,
    }

    filter_args = {}

    if city != "Anywhere":
        filter_args["city__startswith"] = city

    print(filter_args)

    rooms = models.Room.objects.filter(**filter_args)
    print(rooms)

    return render(request, "rooms/search.html", {**form, **choices, "rooms": rooms})
