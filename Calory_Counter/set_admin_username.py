import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Calory_Counter.settings')
django.setup()

from django.contrib.auth.models import User

old_username = 'admin'
new_username = 'admin@calorrycounter.com'

try:
    user = User.objects.get(username=old_username)
    # Ensure no conflict
    if User.objects.filter(username=new_username).exists():
        print('A user with the target username already exists. Aborting.')
    else:
        user.username = new_username
        user.email = new_username
        user.save()
        print(f'Username updated: {old_username} -> {new_username}')
except User.DoesNotExist:
    print('No user with username "admin" found.')
