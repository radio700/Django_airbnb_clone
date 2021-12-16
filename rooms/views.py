from django.shortcuts import redirect, render
from django.urls.base import reverse
# from django.core.paginator import EmptyPage, Paginator
from django.views.generic import ListView
# from django.utils import timezone
from django.http import Http404


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
    """ homeview def"""
    model = models.Room
    paginate_by = 10
    ordering = "created"
    paginate_orphans = 5
    page_kwarg = 'page'
    context_object_name = "rooms"

def room_detail(request,pk):
    try:
        room = models.Room.objects.get(pk=pk)
        context = {'room':room}
        return render(request,"rooms/detail.html",context)

    except models.Room.DoesNotExist:
        # return redirect(reverse("core:home"))
        raise Http404


