import os
import sys
import csv
import django

# 1. Setup path to include the project root (Calory_Counter folder)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# 2. Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Calory_Counter.settings')
django.setup()

from Calory.models import Food

def import_data():
    # 3. Correctly locate calories.csv in the parent directory
    csv_file_path = os.path.join(project_root, 'calories.csv')
    
    if not os.path.exists(csv_file_path):
        print(f"Error: Could not find CSV file at: {csv_file_path}")
        return

    count = 0
    print("Starting import...")
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # 4. Check for duplicates to prevent errors
                # Ensure the CSV headers (e.g., 'name', 'calories') match these keys
                name = row.get('name', '').strip()
                
                if name and not Food.objects.filter(name=name).exists():
                    try:
                        Food.objects.create(
                            name=name,
                            # Use .get() with defaults to handle missing columns safely
                            calories_100g=float(row.get('calories', 0)),
                            protein=float(row.get('protein', 0)),
                            carbs=float(row.get('carbs', 0)),
                            fat=float(row.get('fat', 0)),
                            serving_grams=100.0,  # Default value
                            verified=True
                        )
                        count += 1
                    except ValueError as e:
                        print(f"Skipping row {name}: Invalid data format - {e}")

        print(f"{count} rows inserted.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    import_data()

