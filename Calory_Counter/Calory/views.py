from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .utils import detect_deficiency
from datetime import date,timedelta,datetime
from .models import *
from .utils import *
import json
import requests
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak



# ---------------- REGISTER ----------------
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .utils import detect_deficiency
from datetime import date,timedelta,datetime
from .models import *
from .utils import *
import json
import requests
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
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


@login_required
def dashboard(request):

    today = date.today()

    # Get profile
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return redirect("profile")

    # Today's meals
    meals = Meal.objects.filter(user=request.user, date=today)

    breakfasts = meals.filter(meal="breakfast")
    lunches = meals.filter(meal="lunch")
    dinners = meals.filter(meal="dinner")
    snacks = meals.filter(meal="snack")

    # Total calories
    total = sum(m.calories for m in meals)

    # Status logic
    status = "normal"
    if total > profile.target:
        status = "over"
    elif total >= 0.9 * profile.target:
        status = "good"

    msg = motivation(status)

    # Save daily summary
    update_summary(request.user, today, total, profile)

    # Read summary (for deficiency)
    summary = DailySummary.objects.filter(
        user=request.user,
        date=today
    ).first()

    deficiency = summary.deficiency if summary else "Not calculated"

    return render(request, "Calory/dashboard.html", {
        "profile": profile,
        "total": round(total, 2),
        "msg": msg,
        "deficiency": deficiency,
        "breakfasts": breakfasts,
        "lunches": lunches,
        "dinners": dinners,
        "snacks": snacks,
    })




def update_summary(user, day, total, profile):

    today = timezone.localdate()

    # If past record already exists → DO NOTHING (HARD FREEZE)
    existing = DailySummary.objects.filter(user=user, date=day).first()
    if existing and day < today:
        return

    # Determine target snapshot
    if existing:
        target = existing.target
        streak = existing.streak
    else:
        target = profile.target

        # calculate streak ONLY for new day
        prev_day = day - timedelta(days=1)
        prev = DailySummary.objects.filter(user=user, date=prev_day, healthy=True).first()
        streak = prev.streak if prev else 0

    meals = Meal.objects.filter(user=user, date=day)

    deficiency = detect_deficiency(meals) or "Balanced diet"
    healthy = (0.9 * target <= total <= 1.1 * target)

    if not existing:   # streak only updates when creating new day
        if healthy:
            streak += 1
        else:
            streak = 0

    DailySummary.objects.update_or_create(
        user=user,
        date=day,
        defaults={
            'total_calories': total,
            'healthy': healthy,
            'streak': streak,
            'deficiency': deficiency,
            'target': target
        }
    )


@login_required
def summary_page(request):

    selected_date = request.GET.get("date")

    if selected_date:
        selected_date = date.fromisoformat(selected_date)
    else:
        selected_date = date.today()

    meals = Meal.objects.filter(user=request.user, date=selected_date)

    total = sum(m.calories for m in meals)

    summary = DailySummary.objects.filter(
        user=request.user,
        date=selected_date
    ).first()

    profile = Profile.objects.get(user=request.user)

    target = summary.target if summary else profile.target
    deficiency = summary.deficiency if summary else "Not calculated"

    return render(request,"Calory/summary.html",{
        "meals": meals,
        "total": round(total,2),
        "target": target,
        "deficiency": deficiency,
        "date": selected_date
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


        # Save profile
        profile.weight = new_weight
        profile.bmr = round(bmr,2)
        profile.target = round(target,2)
        profile.save()


        # ✅ Update ONLY today summary
        today = timezone.localdate()

        summary = DailySummary.objects.filter(
            user=request.user,
            date=today
        ).first()

        if summary:
            summary.target = profile.target
            summary.save()


        return redirect("dashboard")


    return render(request,"Calory/update_weight.html",{
        "profile": profile
    })

@login_required
def meal_page(request):

    selected_date = request.GET.get("date")

    if selected_date:
        selected_date = date.fromisoformat(selected_date)
    else:
        selected_date = timezone.localdate()

    meals = Meal.objects.filter(
        user=request.user,
        date=selected_date
    ).select_related("food")

    return render(request, "Calory/meals.html", {
        "meals": meals,
        "date": selected_date,
        "today": timezone.localdate()
    })

# ...existing code...
@login_required
def add_meal(request):

    if request.method == "POST":

        date_str = request.POST.get("date")
        
        # Try parsing standard YYYY-MM-DD first
        try:
            meal_date = date.fromisoformat(date_str)
        except ValueError:
            # Fallback for formats like 'Feb. 15, 2026'
            try:
                # Remove period after month abbreviation if present (Feb. -> Feb)
                clean_date_str = date_str.replace(".", "")
                meal_date = datetime.strptime(clean_date_str, "%b %d, %Y").date()
            except ValueError:
                # If all parsing fails, default to today
                meal_date = timezone.localdate()

        # ❗ Freeze past logic
        if meal_date < timezone.localdate():
            # If you want to prevent adding to past, redirect or show error
            # For now, just redirecting back to meal page
            return redirect(f"/meal/?date={meal_date.isoformat()}")

        food_id = request.POST.get("food")
        
        # Check if food was actually selected
        if not food_id:
             return redirect(f"/meal/?date={meal_date.isoformat()}")

        food = Food.objects.get(id=food_id)
        qty = float(request.POST["qty"])

        grams = food.serving_grams * qty
        calories = (food.calories_100g / 100) * grams

        Meal.objects.create(
            user=request.user,
            food=food,
            date=meal_date,
            meal=request.POST["meal"],
            qty=qty,
            calories=round(calories,2)
        )
        
        # Update daily summary
        update_summary(request.user, meal_date, 0, Profile.objects.get(user=request.user)) # 0 is placeholder, function recalculates total

        # Redirect with standard ISO format date string
        return redirect(f"/meal/?date={meal_date.isoformat()}")

    # GET request logic
    foods = Food.objects.filter(verified=True).values("id","name","meal_type")
    
    return render(request,"Calory/add_meal.html",{
        "foods": json.dumps(list(foods)),
        "today": timezone.localdate()
    })
# ...existing code...
@login_required
def edit_meal(request, meal_id):

    meal = get_object_or_404(Meal, id=meal_id, user=request.user)

    if meal.date < timezone.localdate():
        return redirect("meal_page")

    if request.method == "POST":

        qty = float(request.POST["qty"])
        grams = meal.food.serving_grams * qty

        meal.qty = qty
        meal.calories = (meal.food.calories_100g / 100) * grams
        meal.save()

        recalc_day(request.user, meal.date)
    

        return redirect(f"/meal/?date={meal.date}")

    return render(request,"Calory/edit_meal.html",{"meal":meal})

@login_required
def delete_meal(request, meal_id):

    meal = get_object_or_404(Meal, id=meal_id, user=request.user)

    if meal.date < timezone.localdate():
        return redirect("meal_page")

    meal_date = meal.date
    meal.delete()

    recalc_day(request.user, meal.date)

    return redirect(f"/meal/?date={meal_date}")


# ---------------- BOT PAGE ----------------
def bot_page(request):
    return render(request, "Calory/bot.html")


def bot_page(request):
    return render(request, "Calory/bot.html")


@login_required
def bot_api(request):

    if request.method != "POST":
        return JsonResponse({"reply": "Invalid request."}, status=400)


    try:
        data = json.loads(request.body)
        user_msg = data.get("text", "").strip()

        if not user_msg:
            return JsonResponse({"reply": "Empty message."})


        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-2.5-flash:generateContent"
            f"?key=AIzaSyBR1dMD40HRNvilB0_37fxRzRPVlqLv-DQ"
        )


        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": user_msg}
                    ]
                }
            ]
        }


        response = requests.post(
            url,
            json=payload,
            timeout=20   # ✅ prevent hanging
        )


        result = response.json()
        print(response.status_code, result) # Debug log



        # ❗ API error
        if response.status_code != 200:
            return JsonResponse({
                "reply": "Gemini API error. Try later.",
                "details": result
            }, status=502)


        # ❗ Empty response
        if "candidates" not in result:
            return JsonResponse({
                "reply": "No response from AI."
            })


        reply = result["candidates"][0]["content"]["parts"][0]["text"].strip()


        return JsonResponse({"reply": reply})


    except requests.exceptions.Timeout:
        return JsonResponse({
            "reply": "AI is taking too long. Try again."
        })


    except Exception as e:

        print("Bot Error:", e)

        return JsonResponse({
            "reply": "Server error. Contact admin."
        }, status=500)
        

def update_summary(user, day, total, profile):

    today = timezone.localdate()

    # If past record already exists → DO NOTHING (HARD FREEZE)
    existing = DailySummary.objects.filter(user=user, date=day).first()
    if existing and day < today:
        return

    # Determine target snapshot
    if existing:
        target = existing.target
    else:
        target = profile.target

    meals = Meal.objects.filter(user=user, date=day)

    deficiency = detect_deficiency(meals) or "Balanced diet"
    # Check if within range: 0.9*target <= total <= 1.1*target
    healthy = (0.9 * target <= total <= 1.1 * target)

    # Calculate streak based on whether goal is met (0.9*target <= total <= 1.1*target)
    # Get previous day's summary
    prev_day = day - timedelta(days=1)
    prev = DailySummary.objects.filter(user=user, date=prev_day).first()
    
    if healthy:
        # If within range, continue or start streak
        if prev and prev.healthy:
            # Previous day was healthy, continue streak
            streak = prev.streak + 1
        else:
            # Previous day wasn't healthy or doesn't exist, start new streak
            streak = 1
    else:
        # If outside range (below 0.9*target OR above 1.1*target), reset streak to 0
        streak = 0

    DailySummary.objects.update_or_create(
        user=user,
        date=day,
        defaults={
            'total_calories': total,
            'healthy': healthy,
            'streak': streak,
            'deficiency': deficiency,
            'target': target
        }
    )





def _generate_summary_pdf(user, profile, days_count):
    """Generate PDF report for the given number of days."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
    )
    elements.append(Paragraph(f"Calory Counter - {days_count} Day Summary Report", title_style))
    elements.append(Spacer(1, 12))

    # User info
    info_style = ParagraphStyle(
        name='Info',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
    )
    elements.append(Paragraph(f"<b>User:</b> {user.username}", info_style))
    elements.append(Paragraph(f"<b>Report Generated:</b> {date.today().strftime('%B %d, %Y')}", info_style))
    elements.append(Paragraph(f"<b>Daily Target:</b> {profile.target} kcal", info_style))
    elements.append(Spacer(1, 20))

    # Date range
    end_date = date.today()
    start_date = end_date - timedelta(days=days_count - 1)
    elements.append(Paragraph(f"<b>Period:</b> {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}", info_style))
    elements.append(Spacer(1, 20))

    # Fetch summaries
    summaries = DailySummary.objects.filter(
        user=user,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')

    # Build table data
    table_data = [['Date', 'Total (kcal)', 'Target (kcal)', 'Status', 'Streak']]
    total_cal_sum = 0
    healthy_days = 0

    for s in summaries:
        status = '✓ On Target' if s.healthy else '✗ Off Target'
        table_data.append([
            s.date.strftime('%Y-%m-%d'),
            str(round(s.total_calories, 1)),
            str(round(s.target, 1)),
            status,
            str(s.streak),
        ])
        total_cal_sum += s.total_calories
        if s.healthy:
            healthy_days += 1

    if len(table_data) == 1:
        table_data.append(['No data for this period', '-', '-', '-', '-'])

    # Create table
    table = Table(table_data, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 1.5*inch, 0.8*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 25))

    # Summary stats
    count = len(summaries)
    avg_cal = round(total_cal_sum / count, 1) if count > 0 else 0
    elements.append(Paragraph(f"<b>Summary:</b> healthy_days {healthy_days} of {count}  Average intake: {avg_cal} kcal/day.", info_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer


@login_required
def pdf_report_7day(request):
    """Generate 7-day summary PDF report."""
    profile = get_object_or_404(Profile, user=request.user)
    buffer = _generate_summary_pdf(request.user, profile, 7)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="calory_7day_report.pdf"'
    return response


@login_required
def pdf_report_30day(request):
    """Generate 30-day summary PDF report."""
    profile = get_object_or_404(Profile, user=request.user)
    buffer = _generate_summary_pdf(request.user, profile, 30)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="calory_30day_report.pdf"'
    return response







