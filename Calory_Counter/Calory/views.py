from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from datetime import date,timedelta

from .models import *
from .utils import *


import json
import requests
from django.http import JsonResponse
from django.conf import settings


# ---------------- REGISTER ----------------
def register(request):

    if request.method=="POST":

        email = request.POST['email']

        if User.objects.filter(username=email).exists():
            return render(request,'Calory/register.html', {
                'error': 'User already exists. Please log in.'
            })

        User.objects.create_user(
            username=email,
            email=email,
            password=request.POST['password']
        )

        return redirect('login')

    return render(request,'Calory/register.html')


# ---------------- LOGIN ----------------
def user_login(request):

    if request.method=="POST":

        user=authenticate(
            username=request.POST['email'],
            password=request.POST['password']
        )

        if user:
            login(request,user)
            return redirect('profile')

    return render(request,'Calory/login.html')


# ---------------- LOGOUT ----------------
def user_logout(request):

    logout(request)
    return redirect('login')


# ---------------- PROFILE ----------------
@login_required
def profile(request):

    if request.method=="POST":

        age=request.POST['age']
        height=request.POST['height']
        weight=request.POST['weight']
        gender=request.POST['gender']
        activity=request.POST['activity']

        bmr=calculate_bmr(
            int(age),
            float(height),
            float(weight),
            gender
        )

        target=calculate_tdee(bmr,activity)

        Profile.objects.update_or_create(
            user=request.user,
            defaults={
                'age':age,
                'height':height,
                'weight':weight,
                'gender':gender,
                'activity':activity,
                'bmr':round(bmr,2),
                'target':round(target,2)
            }
        )

        return redirect('dashboard')

    return render(request,'Calory/profile.html')


# ---------------- DASHBOARD ----------------
@login_required
def dashboard(request):

    today=date.today()

    profile=Profile.objects.get(user=request.user)

    meals=Meal.objects.filter(
        user=request.user,
        date=today
    )

    total=sum(m.calories for m in meals)

    status="normal"

    if total>profile.target:
        status="over"
    elif total>=0.9*profile.target:
        status="good"

    msg=motivation(status)

    update_summary(request.user,today,total,profile)

    return render(request,'Calory/dashboard.html',{
        'profile':profile,
        'total':round(total,2),
        'msg':msg
    })


# ---------------- ADD MEAL ----------------
@login_required
def add_meal(request):

    foods=Food.objects.filter(verified=True)

    if request.method=="POST":

        food=Food.objects.get(id=request.POST['food'])
        qty=float(request.POST['qty'])

        grams=food.serving_grams*qty

        cal=(food.calories_100g/100)*grams

        Meal.objects.create(
            user=request.user,
            food=food,
            date=date.today(),
            meal=request.POST['meal'],
            qty=qty,
            calories=round(cal,2)
        )

        return redirect('dashboard')

    return render(request,'Calory/add_meal.html',{'foods':foods})


# ---------------- SUMMARY ----------------
def update_summary(user,today,total,profile):

    yesterday=today-timedelta(days=1)

    prev=DailySummary.objects.filter(
        user=user,
        date=yesterday,
        healthy=True
    ).first()

    streak=0

    if prev:
        streak=prev.streak

    healthy=(0.9*profile.target<=total<=1.1*profile.target)

    if healthy:
        streak+=1
    else:
        streak=0

    DailySummary.objects.update_or_create(
        user=user,
        date=today,
        defaults={
            'total_calories':total,
            'healthy':healthy,
            'streak':streak
        }
    )

# ---------------- BOT PAGE ----------------
def bot_page(request):
    return render(request, "Calory/bot.html")


@login_required
def bot_api(request):

    if request.method == "POST":
        data = json.loads(request.body)
        user_msg = data.get("text", "")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={settings.GEMINI_API_KEY}"

        payload = {
            "contents": [
                {"parts": [{"text": user_msg}]}
            ]
        }

        response = requests.post(url, json=payload)
        result = response.json()

        if response.status_code != 200 or "candidates" not in result:
            # return API error safely
            return JsonResponse(
                {"reply": "API error. Check API key, billing, or request limits.", "details": result},
                status=502
            )

        reply = result["candidates"][0]["content"]["parts"][0]["text"]
        return JsonResponse({"reply": reply})
