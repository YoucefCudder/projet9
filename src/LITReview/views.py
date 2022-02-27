from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.conf import settings
from LITReview import forms


def index(request):
    return render(request, "index.html")


"""
class LoginPage(View):
    form_class = forms.LoginForm
    template_name = 'user/login.html'

    def get(self, request):
        form = self.form_class
        message = ''
        return render(request, self.template_name, context={'form': form, 'message': message})

    def post(self, request):
        if request.method == 'POST':
            form = self.form_class(request.POST)
            if form.is_valid():
                user = authenticate(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'],
                )
                if user is not None:
                    login(request, user)
                    return redirect('home')

            message = f'Identifiants invalides.'
            return render(request, self.template_name, context={'form': form, 'message': message})


def login_page(request):
    form = forms.LoginForm()
    message = ''
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('home')


        message = f'Identifiants invalides.'

    return render(request, 'user/login.html', context={'form': form, 'message': message})
"""


def signup_page(request):
    form = forms.SignupForm()
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, 'user/signup.html', context={'form': form})
