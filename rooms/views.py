from django.http.response import Http404
from django.shortcuts import redirect, render
from django.urls.base import reverse
from django.views.generic import ListView, DetailView, UpdateView, FormView
from django.core.paginator import Paginator
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users import mixins as user_mixins
from . import forms, models

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
    paginate_by = 12
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

class EditRoomView(user_mixins.LoggedInOnlyView,UpdateView):
    model = models.Room
    template_name = "rooms/room_edit.html"
    fields = {
        "name",
        "description",
        "country",
        "city",
        "price",
        "address",
        "guest",
        "beds",
        "bedrooms",
        "baths",
        "check_in",
        "check_out",
        "instant_book",
        "room_type",
        "amenities",
        "facilities",
        "house_rules",
    }

    def get_object(self, queryset = None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room

class RoomPhotosview(user_mixins.LoggedInOnlyView, DetailView):

    model = models.Room
    template_name = "rooms/room_photos.html"

    def get_object(self, queryset = None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room

@login_required
def delete_photo(request, room_pk, photo_pk):
    user = request.user
    try:
        room = models.Room.objects.get(pk=room_pk)
        if room.host.pk != user.pk:
            messages.error(request, "Can't delete")
        else:
            models.Photo.objects.filter(pk=photo_pk).delete()
            messages.success(request, "Photo Deleted!!")
        return redirect(reverse("rooms:photos", kwargs={"pk": room_pk}))
    except models.Room.DoesNotExist:
        return redirect(reverse("core:home"))

class EditPhotoView(user_mixins.LoggedInOnlyView, SuccessMessageMixin , UpdateView):
    
    model = models.Photo
    template_name = "rooms/photo_edit.html"
    pk_url_kwarg = "photo_pk"
    success_message = "사진이 업데이트 됐어요"
    fields = ("caption",)

    def get_success_url(self):
        room_pk = self.kwargs.get("room_pk")
        
        return reverse("rooms:photos", kwargs={"pk": room_pk})


class AddPhotoview(user_mixins.LoggedInOnlyView, FormView):
    
    template_name = "rooms/photo_create.html"
    #create view 이용하는데 form을 바꿔야한다면 form view를 이용하면 됨 rooms/form.py에 CreatePhotoForm을 만들어주고
    form_class = forms.CreatePhotoForm

    def form_valid(self, form):
        pk = self.kwargs.get("pk")
        form.save(pk)
        messages.success(self.request, "Photo Uploaded")
        return redirect(reverse("rooms:photos", kwargs={"pk": pk}))

class CreateRoomView(user_mixins.LoggedInOnlyView, FormView):

    form_class = forms.CreateRoomForm
    template_name = "rooms/room_create.html"

    def form_valid(self, form):
        room = form.save()
        room.host = self.request.user
        room.save()
        form.save_m2m()
        messages.success(self.request, "Room Uploaded")
        return redirect(reverse("rooms:detail", kwargs={"pk": room.pk}))