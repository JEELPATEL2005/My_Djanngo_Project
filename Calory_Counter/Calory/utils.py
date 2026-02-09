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


    if protein < 50:
        return "⚠️ Low Protein"

    if carbs < 130:
        return "⚠️ Low Carbs"

    if fat < 20:
        return "⚠️ Low Fat"

    return "✅ Balanced Diet"

