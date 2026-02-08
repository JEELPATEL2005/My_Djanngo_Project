import csv
import random
from faker import Faker


fake = Faker()


def generate_csv(rows=2000):

    filename = "calories.csv"

    food_base = [
        "Rice", "Bread", "Milk", "Egg", "Paneer", "Chicken",
        "Apple", "Banana", "Orange", "Mango", "Curd", "Dal",
        "Roti", "Pasta", "Burger", "Pizza", "Salad", "Soup",
        "Fish", "Cheese", "Butter", "Potato", "Tomato",
        "Carrot", "Beans", "Corn", "Noodles", "Sandwich"
    ]


    with open(filename, "w", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        # Header
        writer.writerow([
            "name",
            "calories_100g",
            "protein",
            "carbs",
            "fat",
            "serving_grams",
            "verified"
        ])


        for i in range(rows):

            name = random.choice(food_base) + " " + fake.word().title()

            calories = round(random.uniform(40, 350), 2)
            protein = round(random.uniform(0, 30), 2)
            carbs = round(random.uniform(5, 70), 2)
            fat = round(random.uniform(0, 25), 2)

            serving = random.choice([50, 80, 100, 120, 150, 180, 200])

            verified = True


            writer.writerow([
                name,
                calories,
                protein,
                carbs,
                fat,
                serving,
                verified
            ])


    print(f"✅ {rows} rows written to {filename}")


# Run generator
if __name__ == "__main__":

    generate_csv(1000)
