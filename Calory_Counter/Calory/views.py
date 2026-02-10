from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .utils import detect_deficiency
from datetime import date,timedelta
from .models import *
from .utils import *
import json
import requests
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404



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
            
            # Check if user is an admin
            try:
                from Admin.models import AdminUser
                admin_profile = AdminUser.objects.get(user=user, is_active=True)
                return redirect('admin_dashboard')
            except:
                pass
            
            return redirect('profile')

    return render(request,'Calory/login.html')


# ---------------- LOGOUT ----------------
def user_logout(request):

    logout(request)
    return redirect('login')


# ---------------- PROFILE ----------------
@login_required
def profile(request):

    profile = Profile.objects.filter(user=request.user).first()

    # If profile already exists → go dashboard
    if profile and request.method != "POST":
        return redirect("dashboard")


    if request.method == "POST":

        age = request.POST['age']
        height = request.POST['height']
        weight = request.POST['weight']
        gender = request.POST['gender']
        activity = request.POST['activity']


        bmr = calculate_bmr(
            int(age),
            float(height),
            float(weight),
            gender
        )

        target = calculate_tdee(bmr, activity)


        Profile.objects.update_or_create(

            user=request.user,

            defaults={
                'age': age,
                'height': height,
                'weight': weight,
                'gender': gender,
                'activity': activity,
                'bmr': round(bmr,2),
                'target': round(target,2)
            }
        )

        return redirect("dashboard")


    return render(request,'Calory/profile.html')

# ---------------- DASHBOARD ----------------
@login_required
def dashboard(request):

    today = date.today()

    # Get profile
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return redirect('profile')


    # ✅ Get today's meals (FIXED)
    meals = Meal.objects.filter(
        user=request.user,
        date=today
    )


    # Calculate total calories
    total = sum(m.calories for m in meals)


    # Status
    status = "normal"

    if total > profile.target:
        status = "over"

    elif total >= 0.9 * profile.target:
        status = "good"


    # Motivation
    msg = motivation(status)


    # Save daily summary
    update_summary(request.user, today, total, profile)


    # Get saved summary
    summary = DailySummary.objects.filter(
        user=request.user,
        date=today
    ).first()


    # Get deficiency
    deficiency = summary.deficiency if summary else "Not calculated"


    # Render page
    return render(request, 'Calory/dashboard.html', {

        'profile': profile,
        'total': round(total, 2),
        'msg': msg,
        'deficiency': deficiency,
        'meals': meals   # (optional: for showing meals list)
    })

@login_required
def update_weight(request):

    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":

        new_weight = float(request.POST["weight"])


        # Recalculate BMR
        bmr = calculate_bmr(
            profile.age,
            profile.height,
            new_weight,
            profile.gender
        )


        # Recalculate Target
        target = calculate_tdee(bmr, profile.activity)


        # Save
        profile.weight = new_weight
        profile.bmr = round(bmr,2)
        profile.target = round(target,2)

        profile.save()


        return redirect("dashboard")


    return render(request,"Calory/update_weight.html",{
        "profile": profile
    })


# ---------------- ADD MEAL ----------------
@login_required
def add_meal(request):

    foods = Food.objects.filter(verified=True)

    if request.method=="POST":

        food = Food.objects.get(id=request.POST['food'])
        qty = float(request.POST['qty'])

        grams = food.serving_grams * qty

        cal = (food.calories_100g / 100) * grams


        Meal.objects.update_or_create(

            user=request.user,
            food=food,
            date=timezone.now(),   # ✅ FIX
            meal=request.POST['meal'],

            defaults={
                'qty': qty,
                'calories': round(cal,2)
            }
        )

        return redirect('dashboard')

    return render(request,'Calory/add_meal.html',{'foods':foods})


# ---------------- SUMMARY ----------------
def update_summary(user, today, total, profile):

    yesterday = today - timedelta(days=1)


    prev = DailySummary.objects.filter(
        user=user,
        date=yesterday,
        healthy=True
    ).first()


    streak = prev.streak if prev else 0


    # Get today's meals
    meals = Meal.objects.filter(
        user=user,
        date=today
    )


    deficiency = detect_deficiency(meals)


    healthy = (0.9 * profile.target <= total <= 1.1 * profile.target)


    if healthy:
        streak += 1
    else:
        streak = 0


    DailySummary.objects.update_or_create(

        user=user,
        date=today,

        defaults={
            'total_calories': total,
            'healthy': healthy,
            'streak': streak,
            'deficiency': deficiency
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


# ---------------- MANAGE FOODS (CRUD) ----------------
@login_required
def foods_list(request):

    # Only staff can manage food items
    if not request.user.is_staff:
        return redirect('dashboard')

    foods = Food.objects.all().order_by('name')

    return render(request, 'Calory/manage_foods.html', {'foods': foods})


@login_required
def add_food(request):

    if not request.user.is_staff:
        return redirect('dashboard')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        try:
            calories = float(request.POST.get('calories_100g') or 0)
        except ValueError:
            calories = 0
        try:
            protein = float(request.POST.get('protein') or 0)
        except ValueError:
            protein = 0
        try:
            carbs = float(request.POST.get('carbs') or 0)
        except ValueError:
            carbs = 0
        try:
            fat = float(request.POST.get('fat') or 0)
        except ValueError:
            fat = 0
        try:
            serving = float(request.POST.get('serving_grams') or 100)
        except ValueError:
            serving = 100
        verified = True if request.POST.get('verified') else False

        if name:
            Food.objects.create(
                name=name,
                calories_100g=calories,
                protein=protein,
                carbs=carbs,
                fat=fat,
                serving_grams=serving,
                verified=verified
            )

        return redirect('foods_list')

    return render(request, 'Calory/edit_food.html', {'food': None})


@login_required
def edit_food(request, food_id):

    if not request.user.is_staff:
        return redirect('dashboard')

    food = get_object_or_404(Food, id=food_id)

    if request.method == 'POST':
        food.name = request.POST.get('name', food.name).strip()
        try:
            food.calories_100g = float(request.POST.get('calories_100g') or food.calories_100g)
        except ValueError:
            pass
        try:
            food.protein = float(request.POST.get('protein') or food.protein)
        except ValueError:
            pass
        try:
            food.carbs = float(request.POST.get('carbs') or food.carbs)
        except ValueError:
            pass
        try:
            food.fat = float(request.POST.get('fat') or food.fat)
        except ValueError:
            pass
        try:
            food.serving_grams = float(request.POST.get('serving_grams') or food.serving_grams)
        except ValueError:
            pass
        food.verified = True if request.POST.get('verified') else False
        food.save()

        return redirect('foods_list')

    return render(request, 'Calory/edit_food.html', {'food': food})


@login_required
def delete_food(request, food_id):

    if not request.user.is_staff:
        return redirect('dashboard')

    food = get_object_or_404(Food, id=food_id)
    if request.method == 'POST' or request.method == 'GET':
        food.delete()

    return redirect('foods_list')
