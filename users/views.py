# import os
# import dotenv
from django.http import HttpResponse
import requests
import os

from django.urls import reverse
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


# 인증코드요청 -> 인증코드전달 -> 인증코드로 토큰요청 -> 토큰전달 -> 토큰으로 API 호출 -> 응답전달
def github_login(request):
    client_id = os.environ.get("GITHUB_CLIENT_ID")
    redirect_uri = "http://127.0.0.1:8000/users/login/github/callback"
    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user"
        # [[1]]유저가 버튼을 누를경우 깃허브로 이동해서 인증을 받아온 후 redirect_uri로 이동한다 -> callback으로 이동된다
        # scope=read:user는 Grants access to read a user's profile data 권한을 설정한다
        # 자세한건 https://docs.github.com/en/developers/apps/building-oauth-apps/scopes-for-oauth-apps
        # 참조 할 것 https://clownhacker.tistory.com/170
    )


class GithubException(Exception):
    pass


def github_callback(request):
    try:
        client_id = os.environ.get("GITHUB_CLIENT_ID")
        client_secret = os.environ.get("GITHUB_CLIENT_SECRET")
        code = request.GET.get("code", None)
        # print(f"--------------{code}<<<<<<코드임")
        if code is not None:
            # [[2]]github에서 전달해준 code를 이용해서 다시 POST형태로 github에 access_token을 요청한다
            token_request = requests.post(
                f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
                headers={"Accept": "application/json"},
                # [[2.5]]↑요 주소로 요청을 보내면 access_token과 찌끄레기들이 json형태로 나온다 post(f"", headers={})에 주의할것
            )
            token_json = token_request.json()
            # print(f"--------------------{token_json}<<<<<<<토큰임")
            error = token_json.get("error", None)
            if error is not None:
                raise GithubException("접근 토큰에 억세스 불가능함")
            else:
                access_token = token_json.get("access_token")
                # print(f"-------------------{access_token}<<<<<<<토큰중에 access_token 부분만 뗀거임")
                profile_request = requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json",
                    },
                    # [[3]] 받아온 access_tocken을 https://api.github.com/user 주소로 요청해서 유저의 정보를 가져온다
                    # get("", headers={})에 주의할것
                )
                profile_json = profile_request.json()
                # print(f"-------------------{profile_json}<<<<<<<프로파일 json임")
                username = profile_json.get("login", None)
                # username = radio700
                if username is not None:
                    name = profile_json.get("name")
                    if name is None:  # sejung_kim이 없을 경우
                        name = username  # username(radio700)을 name에 넣어준다
                    email = profile_json.get("email")
                    if email is None:
                        email = name
                    bio = profile_json.get("bio")
                    if bio is None:
                        bio = ""
                    try:
                        user = models.User.objects.get(email=email)
                        # print(f"-------------------------{user}<<<<<<<<<<<유저임")
                        if user.login_method != models.User.LOGIN_GITHUB:
                            raise GithubException(
                                f"정해진 로그인 메소드로 로그인 해주세요 ->{user.login_method}"
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
                    messages.success(request, f"{user.first_name}님 환영합니다")
                    return redirect("core:home")
                else:
                    raise GithubException("프로파일을 얻을 수가 없어요")
        else:
            raise GithubException("깃허브에서 코드가 없어요ㅠ")
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
            raise KakaoException("인증코드에 접근 못함")
        access_token = token_json.get("access_token")

        profile_request = requests.post(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        profile_json = profile_request.json()

        kakao_account = profile_json.get("kakao_account")
        email = kakao_account["email"]
        if email is None:
            raise KakaoException("이메일이 없어요")
        profile = kakao_account["profile"]
        nickname = profile["nickname"]
        profile_image_url = profile["profile_image_url"]

        try:
            user = models.User.objects.get(email=email)
            if user.login_method != models.User.LOGING_KAKAO:
                raise KakaoException(f"{user.login_method}로 로그인 해주세요")
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
        messages.success(request, f"{user.first_name}{user.last_name}님 다시보네요:)")
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
    success_message = "프로파일이 업데이트 됐어요"

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
    success_message = "비밀번호가 업데이트 됐어요"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        print(form)
        form.fields["old_password"].widget.attrs = {"placeholder": "현재 비밀번호"}
        form.fields["new_password1"].widget.attrs = {"placeholder": "새 비밀번호"}
        form.fields["new_password2"].widget.attrs = {"placeholder": "새 비밀번호 확인"}
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

def switch_lang(request):
    lang = request.GET.get("lang", None)
    if lang is not None:
        pass
    return HttpResponse(status=200)
