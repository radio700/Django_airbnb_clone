# from django.shortcuts import redirect, render
# from django.core.paginator import EmptyPage, Paginator
from django.views.generic import ListView
from django.utils import timezone
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context["now"] = now
        return context

