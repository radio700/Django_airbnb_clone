# import os
# import dotenv
import requests
import os
from django.urls import reverse
from django.http import HttpResponse
from django.views.generic import FormView, DetailView, UpdateView
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.core.files.base import ContentFile
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from . import forms, models, mixins
from config import settings

# Create your views here.

class LoginView(mixins.LoggedOutOnlyView, FormView):

    template_name = "users/login.html"
    form_class = forms.LoginForm

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        next_arg = self.request.GET.get("next")
        if next_arg is not None:
            return next_arg
        else:
            return reverse("core:home")


def log_out(request):
    messages.info(request, "See you later")
    logout(request)
    return redirect("core:home")


class SignupView(FormView):
    template_name = "users/signup.html"
    form_class = forms.SignupForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        user.verify_email()
        return super().form_valid(form)


def complete_verification(request, key):
    try:
        user = models.User.objects.get(email_secret=key)
        user.email_verified = True
        user.email_secret = ""
        user.save()
        # to do: add succes message
    except models.User.DoesNotExist:
        # to do: add error message
        pass
    return redirect(reverse("core:home"))


# ?????????????????? -> ?????????????????? -> ??????????????? ???????????? -> ???????????? -> ???????????? API ?????? -> ????????????
def github_login(request):
    client_id = os.environ.get("GITHUB_CLIENT_ID")
    redirect_uri = "http://127.0.0.1:8000/users/login/github/callback"
    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user"
        # [[1]]????????? ????????? ???????????? ???????????? ???????????? ????????? ????????? ??? redirect_uri??? ???????????? -> callback?????? ????????????
        # scope=read:user??? Grants access to read a user's profile data ????????? ????????????
        # ???????????? https://docs.github.com/en/developers/apps/building-oauth-apps/scopes-for-oauth-apps
        # ?????? ??? ??? https://clownhacker.tistory.com/170
    )


class GithubException(Exception):
    pass


def github_callback(request):
    try:
        client_id = os.environ.get("GITHUB_CLIENT_ID")
        client_secret = os.environ.get("GITHUB_CLIENT_SECRET")
        code = request.GET.get("code", None)
        # print(f"--------------{code}<<<<<<?????????")
        if code is not None:
            # [[2]]github?????? ???????????? code??? ???????????? ?????? POST????????? github??? access_token??? ????????????
            token_request = requests.post(
                f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
                headers={"Accept": "application/json"},
                # [[2.5]]?????? ????????? ????????? ????????? access_token??? ?????????????????? json????????? ????????? post(f"", headers={})??? ????????????
            )
            token_json = token_request.json()
            # print(f"--------------------{token_json}<<<<<<<?????????")
            error = token_json.get("error", None)
            if error is not None:
                raise GithubException("?????? ????????? ????????? ????????????")
            else:
                access_token = token_json.get("access_token")
                # print(f"-------------------{access_token}<<<<<<<???????????? access_token ????????? ?????????")
                profile_request = requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json",
                    },
                    # [[3]] ????????? access_tocken??? https://api.github.com/user ????????? ???????????? ????????? ????????? ????????????
                    # get("", headers={})??? ????????????
                )
                profile_json = profile_request.json()
                # print(f"-------------------{profile_json}<<<<<<<???????????? json???")
                username = profile_json.get("login", None)
                # username = radio700
                if username is not None:
                    name = profile_json.get("name")
                    if name is None:  # sejung_kim??? ?????? ??????
                        name = username  # username(radio700)??? name??? ????????????
                    email = profile_json.get("email")
                    if email is None:
                        email = name
                    bio = profile_json.get("bio")
                    if bio is None:
                        bio = ""
                    try:
                        user = models.User.objects.get(email=email)
                        # print(f"-------------------------{user}<<<<<<<<<<<?????????")
                        if user.login_method != models.User.LOGIN_GITHUB:
                            raise GithubException(
                                f"????????? ????????? ???????????? ????????? ???????????? ->{user.login_method}"
                            )
                    except models.User.DoesNotExist:
                        user = models.User.objects.create(
                            email=email,
                            first_name=name,
                            username=email,
                            bio=bio,
                            login_method=models.User.LOGIN_GITHUB,
                        )
                        user.set_unusable_password()
                        user.save()
                    login(request, user)
                    messages.success(request, f"{user.first_name}??? ???????????????")
                    return redirect("core:home")
                else:
                    raise GithubException("??????????????? ?????? ?????? ?????????")
        else:
            raise GithubException("??????????????? ????????? ????????????")
    except GithubException as e:
        messages.error(request, e)
        return redirect("users:login")


def kakao_login(request):
    client_id = os.environ.get("KAKAO_CLIENT_ID")
    redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    )


class KakaoException(Exception):
    pass


def kakao_callback(request):
    try:
        code = request.GET.get("code")
        client_id = os.environ.get("KAKAO_CLIENT_ID")
        redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
        token_request = requests.get(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={redirect_uri}&code={code}"
        )
        token_json = token_request.json()
        error = token_json.get("error", None)
        if error is not None:
            raise KakaoException("??????????????? ?????? ??????")
        access_token = token_json.get("access_token")

        profile_request = requests.post(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        profile_json = profile_request.json()

        kakao_account = profile_json.get("kakao_account")
        email = kakao_account["email"]
        if email is None:
            raise KakaoException("???????????? ?????????")
        profile = kakao_account["profile"]
        nickname = profile["nickname"]
        profile_image_url = profile["profile_image_url"]

        try:
            user = models.User.objects.get(email=email)
            if user.login_method != models.User.LOGING_KAKAO:
                raise KakaoException(f"{user.login_method}??? ????????? ????????????")
        except models.User.DoesNotExist:
            user = models.User.objects.create(
                email=email,
                username=email,
                first_name=nickname,
                login_method=models.User.LOGING_KAKAO,
                email_verified=True,
            )
            user.set_unusable_password()
            user.save()
            if profile_image_url is not None:
                photo_request = requests.get(profile_image_url)
                user.avatar.save(
                    f"{nickname}-avatar", ContentFile(photo_request.content)
                )
        login(request, user)
        messages.success(request, f"{user.first_name}{user.last_name}??? ???????????????:)")
        return redirect(reverse("core:home"))
    except KakaoException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))


class UserProfileView(DetailView):

    model = models.User
    context_object_name = "user_obj"


class UpdateProfileView(mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):

    model = models.User
    template_name = "users/update-profile.html"
    fields = (
        "email",
        "first_name",
        "last_name",
        "gender",
        "bio",
        "birthday",
        "language",
        "currency",
    )
    success_message = "??????????????? ???????????? ?????????"

    def get_object(self, queryset=None):
        return self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        # print(form)
        form.fields["email"].widget.attrs = {"placeholder": "email"}
        form.fields["first_name"].widget.attrs = {"placeholder": "first name"}
        form.fields["last_name"].widget.attrs = {"placeholder": "last_name"}
        form.fields["gender"].widget.attrs = {"placeholder": "gender"}
        form.fields["bio"].widget.attrs = {"placeholder": "bio"}
        form.fields["birthday"].widget.attrs = {"placeholder": "birthday"}
        form.fields["language"].widget.attrs = {"placeholder": "language"}
        form.fields["currency"].widget.attrs = {"placeholder": "currency"}
        return form


class UpdatePasswordView(
    mixins.EmailLoginOnlyMixin,
    mixins.LoggedInOnlyView,
    SuccessMessageMixin,
    PasswordChangeView,
):
    template_name = "users/update-password.html"
    success_message = "??????????????? ???????????? ?????????"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        print(form)
        form.fields["old_password"].widget.attrs = {"placeholder": "?????? ????????????"}
        form.fields["new_password1"].widget.attrs = {"placeholder": "??? ????????????"}
        form.fields["new_password2"].widget.attrs = {"placeholder": "??? ???????????? ??????"}
        return form

    def get_success_url(self):
        return self.request.get_absolute_url()

@login_required
def switch_hosting(request):
    try:
        del request.session["is_hosting"]
    except KeyError:
        request.session["is_hosting"] = True
    return redirect(reverse("core:home"))

def switch_language(request):
    lang = request.GET.get("lang", None)
    if lang is not None:
        response = HttpResponse(200)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
        return response
