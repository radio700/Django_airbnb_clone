# import os
# import dotenv
import requests

from django.views import View
from django.views.generic import FormView
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from . import forms
from . import models

# Create your views here.


class LoginView(View):
    def get(self, request):
        form = forms.LoginForm()
        return render(request, "users/login.html", {"form": form})

    def post(self, request):
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(self.request, username=email, password=password)
            if user is not None:
                login(self.request, user)
                return redirect("core:home")
        return render(request, "users/login.html", {"form": form})


def log_out(request):
    logout(request)
    return redirect("core:home")


class SignupView(FormView):
    template_name = "users/signup.html"
    form_class = forms.SignupForm
    success_url = reverse_lazy("core:home")
    initial = {
        "first_name": "kim",
        "last_name": "sejung",
        "email": "radio700@hanmail.net",
    }

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        user.verify_email()
        return super().form_valid(form)


# 인증코드요청 -> 인증코드전달 -> 인증코드로 토큰요청 -> 토큰전달 -> 토큰으로 API 호출 -> 응답전달
def github_login(request):
    client_id = "193455c9cd3ca7ed7ede"
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
        client_id = "193455c9cd3ca7ed7ede"
        client_secret = "2f3ad78a6cb6b4795385705862d118562a5f5894"
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
                raise GithubException()
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
                    return redirect("core:home")
                else:
                    raise GithubException("유저 네임이 존재하지 않아여")
        else:
            raise GithubException("깃허브에서 코드가 없어요ㅠ")
    except GithubException:
        return redirect("users:login")


def kakao_login(request):
    client_id = "f50c5cef45ce31fb7c8b90aa5e5b5073"
    redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    )


class KakaoException(Exception):
    pass


def kakao_callback(request):
    try:
        code = request.GET.get("code")
        client_id = "f50c5cef45ce31fb7c8b90aa5e5b5073"
        redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
        token_request = requests.get(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={redirect_uri}&code={code}"
        )
        token_json = token_request.json()
        error = token_json.get("error", None)
        if error is not None:
            raise KakaoException()
        access_token = token_json.get("access_token")


        profile_request = requests.post("https://kapi.kakao.com/v2/user/me",headers={"Authorization": f"Bearer {access_token}"},)

        profile_json = profile_request.json()
        print(profile_json)
        kakao_account = profile_json.get("kakao_account")
        email = kakao_account["email"]
        profile = kakao_account["profile"]
        nickname = profile["nickname"]
        profile_image_url = profile['profile_image_url']

        try:
            user = models.User.objects.get(email=email)
            if user.login_method != models.User.LOGING_KAKAO:
                raise KakaoException()
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
            login(request, user)
            return redirect("core:home")
    except KakaoException:
        return redirect("users:login")




