from django import forms
from . import models

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder":"이메일을 입력하세요"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"비밀번호를 입력하세요"}))

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        try :
            user = models.User.objects.get(email=email)
            if user.check_password(password):
                return self.cleaned_data
            else:
                self.add_error("password",forms.ValidationError("패스워드 틀림"))
        except models.User.DoesNotExist:
            self.add_error("email",forms.ValidationError("유저가 존재하지 않아여"))

class SignupForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ("first_name","last_name","email","password")
        widgets ={
            'first_name':forms.TextInput(attrs={"placeholder":"이름을 입력하세요"}),
            'last_name':forms.TextInput(attrs={"placeholder":"성을 입력하세요"}),
            'email':forms.EmailInput(attrs={"placeholder":"이메일을 입력하세요"}),
        }

    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"비밀번호를 입력하세요"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"비밀번호를 입력하세요"}),label='패스확인')

    def clean_password1(self):
        password = self.cleaned_data.get("password")
        password1 = self.cleaned_data.get("password1")
        if password != password1:
            raise forms.ValidationError("Password confirmation does not match")
        else:
            return password

    def save(self,*args,**kwargs):
        user = super().save(commit=False)
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        user.username = email
        user.set_password(password)
        user.save()






