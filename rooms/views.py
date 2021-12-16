from django.shortcuts import redirect, render
from django.core.paginator import EmptyPage, Paginator
from . import models

# Create your views here.
def all_rooms(request):
    page = request.GET.get("page",1)
    room_list = models.Room.objects.all()

    paginator = Paginator(room_list, 10,orphans=5)
    try:
        rooms = paginator.page(int(page))
        context = {"page": rooms}
        return render(request, "rooms/home.html", context)
    except EmptyPage:
        rooms = paginator.page(1)
        return redirect("/")

