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

    if status=="good":
        return "🔥 Great job! Keep going!"

    if status=="over":
        return "⚠️ You exceeded your target. Be careful!"

    return "💪 You can do better tomorrow!"
