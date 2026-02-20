
from django.db import models
from django.contrib.auth.models import User


# USER PROFILE
class Profile(models.Model):

    GENDER = [('M','Male'),('F','Female')]
    ACTIVITY = [('low','Low'),('medium','Medium'),('high','High')]

    user = models.OneToOneField(User,on_delete=models.CASCADE)

    age = models.IntegerField()
    height = models.FloatField()
    weight = models.FloatField()
    gender = models.CharField(max_length=1,choices=GENDER)
    activity = models.CharField(max_length=10,choices=ACTIVITY)

    bmr = models.FloatField(default=0)
    target = models.FloatField(default=0)

    def __str__(self):
        return self.user.username


# FOOD DATABASE
class Food(models.Model):

    MEAL_CHOICES = [
        ("breakfast","Breakfast"),
        ("lunch","Lunch"),
        ("dinner","Dinner"),
        ("snack","Snack"),
    ]

    name = models.CharField(max_length=100)
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES)   
    calories_100g = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()
    serving_grams = models.FloatField(default=100)
    verified = models.BooleanField(default=True)



# MEAL LOG
class Meal(models.Model):

    MEAL = [
        ('breakfast','Breakfast'),
        ('lunch','Lunch'),
        ('dinner','Dinner'),
        ('snack','Snack')
    ]

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    food = models.ForeignKey(Food,on_delete=models.CASCADE)

    date = models.DateField()
    meal = models.CharField(max_length=20,choices=MEAL)

    qty = models.FloatField()
    calories = models.FloatField()


# DAILY SUMMARY
class DailySummary(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    date = models.DateField()

    total_calories = models.FloatField()
    healthy = models.BooleanField()
    streak = models.IntegerField()

    deficiency = models.CharField(max_length=100, default="Not calculated")

    target = models.FloatField(default=0)   # ✅ ADD THIS


