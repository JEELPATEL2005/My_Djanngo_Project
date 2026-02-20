def calculate_bmr(age,height,weight,gender):

    if gender=='M':
        return 10*weight+6.25*height-5*age+5

    return 10*weight+6.25*height-5*age-161


def calculate_tdee(bmr,activity):

    factor={
        'low':1.2,
        'medium':1.55,
        'high':1.9
    }

    return bmr*factor[activity]


def motivation(status):

    if status == "good":
        return "🔥 Great job! You are on track today."

    elif status == "over":
        return "⚠️ You exceeded your calorie limit today."

    else:
        return "🙂 Keep going! Try to stay within your goal."


def detect_deficiency(meals):

 
    protein = sum(m.food.protein * m.qty for m in meals)
    carbs = sum(m.food.carbs * m.qty for m in meals)
    fat = sum(m.food.fat * m.qty for m in meals)


    if protein < 50 and carbs >= 130 and fat >= 20:
        return "⚠️ Low Protein"

    if carbs < 130 and protein >= 50 and fat >= 20:
        return "⚠️ Low Carbs"

    if fat < 20 and protein >= 50 and carbs >= 130:
        return "⚠️ Low Fat"
    
    if protein < 50 and carbs < 130 and fat < 20:
        return "⚠️ Low protein, carbs, and fat"
    
    if protein >= 50 and carbs >= 130 and fat >= 20:
        return "✅ Healthy Diet"
    
    if not meals.exists():
        return "No meals recorded"
    
def recalc_day(user, day):
    from .models import Meal, Profile
    from .views import update_summary

    profile = Profile.objects.get(user=user)

    meals = Meal.objects.filter(user=user, date=day)
    total = sum(m.calories for m in meals)

    update_summary(user, day, total, profile)


