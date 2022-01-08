from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy


class EmailLoginOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.login_method == "email"

    def handle_no_permission(self):
        messages.error(self.request, "접근 권한이 없습니다.")
        return redirect("core:home")


class LoggedOutOnlyView(UserPassesTestMixin):

    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        messages.error(self.request,"거기로 못가요")
        return redirect("core:home")

class LoggedInOnlyView(LoginRequiredMixin):
    login_url = reverse_lazy("users:login")
