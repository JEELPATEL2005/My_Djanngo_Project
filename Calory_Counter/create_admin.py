import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Calory_Counter.settings')
django.setup()

from django.contrib.auth.models import User
from Admin.models import AdminUser

# Create new admin user
user = User.objects.create_user(
    username='admin',
    email='admin@calorrycounter.com',
    password='Admin@12345'
)

# Make them super admin
AdminUser.objects.create(
    user=user,
    role='superadmin',
    is_active=True
)

print("✓ Admin user created successfully!")
print("=" * 50)
print(f"Username: admin")
print(f"Password: Admin@12345")
print(f"Role: Super Admin")
print(f"Status: Active")
print("=" * 50)
print("\nLogin at: http://localhost:8000/login/")
