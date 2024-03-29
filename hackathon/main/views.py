from django.contrib.auth.decorators import login_required

from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth import update_session_auth_hash, login as auth_login, authenticate
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import SignUpForm,SignUpForm1
from .models import Client,Psychologist
from social_django.models import UserSocialAuth
import pickle
import requests

mnb = pickle.load(open('mnb.pkl','rb'))
tfidf = pickle.load(open('tfidf.pkl','rb'))
# Create your views here.
def index(request):
    return render(request,'main/index.html')

@login_required
def home(request):
    return render(request,'main/index.html')

def connect(request):
    return render(request,'main/connect.html')

def login(request):
    return render(request,'main/login.html')

@login_required
def settings(request):
    user = request.user

    try:
        twitter_login = user.social_auth.get(provider='twitter')
    except UserSocialAuth.DoesNotExist:
        twitter_login = None

    try:
        facebook_login = user.social_auth.get(provider='facebook')
    except UserSocialAuth.DoesNotExist:
        facebook_login = None
    
    try:
        instagram_login = user.social_auth.get(provider='instagram')
    except UserSocialAuth.DoesNotExist:
        instagram_login = None

    can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())


    return render(request, 'main/setting.html', {
        'twitter_login': twitter_login,
        'facebook_login': facebook_login,
        'instagram_login':instagram_login,
        'can_disconnect': can_disconnect
    })

@login_required
def password(request):
    if request.user.has_usable_password():
        PasswordForm = PasswordChangeForm
    else:
        PasswordForm = AdminPasswordChangeForm

    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('main:password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordForm(request.user)
    return render(request, 'main/password.html', {'form': form})


def selection(request):
    return render(request,'main/selection.html')

def client(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            client_new = Client(user = user)
            client_new.save()
            auth_login(request, user)
            return redirect('main:home')
    else:
        form = SignUpForm()
    return render(request, 'main/signup.html', {'form': form})

def psychologist(request):
    if request.method == 'POST':
        form = SignUpForm1(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            highest_qualifications = form.cleaned_data.get('highest_qualifications')
            Clinic_location = form.cleaned_data.get('Clinic_location')
            user = authenticate(username=username, password=raw_password)
            psychologist_new = Psychologist(user=user,highest_qualifications = highest_qualifications ,Clinic_location = Clinic_location)
            psychologist_new.save()
            auth_login(request, user)
            return redirect('main:home')
    else:
        form = SignUpForm1()
    return render(request, 'main/signup_psychologist.html', {'form': form})


def depression(string):
    answer = mnb.predict(tfidf.transform([str(string)]))
    return str(answer) == '[1]'



def facebook_login(request):
    user = request.user
    facebook_login = user.social_auth.get(provider='facebook')
    access_token = facebook_login.extra_data['access_token']
    r = requests.get(url = 'https://graph.facebook.com/v4.0/me?fields=id%2Cname%2Cposts&access_token={}'.format(access_token))
    data = r.json()
    request.session['username'] = data['name']
    if data['posts']['data'][0]['message'] != None:
        d = depression(data['posts']['data'][0]['message'])
        if(d==True):
            return redirect('/sad')
    return redirect('/happy')

def happy(request):
    return render(request,'main/happy.html')

def sad(request):
    return render(request,'main/sad.html')