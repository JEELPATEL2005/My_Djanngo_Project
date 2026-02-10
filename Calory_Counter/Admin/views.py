from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from Calory.models import Food
from .models import AdminUser


def is_admin(user):
    """Check if user is an admin"""
    try:
        return user.admin_profile.is_active
    except AdminUser.DoesNotExist:
        return False


def admin_required(view_func):
    """Decorator to require admin access"""
    def wrapper(request, *args, **kwargs):
        if not is_admin(request.user):
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ============= ADMIN LOGIN =============
def admin_login(request):
    """Admin login page"""
    
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        user = authenticate(username=username, password=password)
        
        if user and is_admin(user):
            login(request, user)
            return redirect('admin_dashboard')
        else:
            return render(request, 'Admin/login.html', {
                'error': 'Invalid credentials or not an admin user.'
            })

    return render(request, 'Admin/login.html')


def admin_logout(request):
    """Admin logout"""
    logout(request)
    return redirect('admin_login')


# ============= ADMIN DASHBOARD =============
@admin_required
@login_required
def admin_dashboard(request):
    """Main admin dashboard"""
    
    # Get statistics
    total_foods = Food.objects.count()
    total_users = User.objects.count()
    total_admins = AdminUser.objects.filter(is_active=True).count()
    
    context = {
        'total_foods': total_foods,
        'total_users': total_users,
        'total_admins': total_admins,
    }
    
    return render(request, 'Admin/dashboard.html', context)


# ============= FOOD MANAGEMENT =============
@admin_required
@login_required
def manage_foods(request):
    """Manage all food items"""
    
    foods = Food.objects.all().order_by('name')
    
    return render(request, 'Admin/manage_foods.html', {'foods': foods})


@admin_required
@login_required
def add_food_admin(request):
    """Add a new food item"""
    
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

        return redirect('admin_manage_foods')

    return render(request, 'Admin/edit_food.html', {'food': None})


@admin_required
@login_required
def edit_food_admin(request, food_id):
    """Edit an existing food item"""
    
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

        return redirect('admin_manage_foods')

    return render(request, 'Admin/edit_food.html', {'food': food})


@admin_required
@login_required
def delete_food_admin(request, food_id):
    """Delete a food item"""
    
    food = get_object_or_404(Food, id=food_id)
    food.delete()

    return redirect('admin_manage_foods')


# ============= USER MANAGEMENT =============
@admin_required
@login_required
def manage_users(request):
    """Manage all users"""
    
    users = User.objects.all()
    
    return render(request, 'Admin/manage_users.html', {'users': users})


@admin_required
@login_required
def toggle_admin(request, user_id):
    """Grant or revoke admin access to a user"""
    
    user = get_object_or_404(User, id=user_id)
    
    if user == request.user:
        return render(request, 'Admin/manage_users.html', {
            'users': User.objects.all(),
            'error': 'You cannot revoke your own admin access.'
        })
    
    admin_profile, created = AdminUser.objects.get_or_create(user=user)
    admin_profile.is_active = not admin_profile.is_active
    admin_profile.save()
    
    return redirect('admin_manage_users')


@admin_required
@login_required
def manage_admins(request):
    """Manage admin users and their roles"""
    
    admins = AdminUser.objects.all()
    
    return render(request, 'Admin/manage_admins.html', {'admins': admins})


@admin_required
@login_required
def edit_admin_role(request, admin_id):
    """Edit admin role"""
    
    admin = get_object_or_404(AdminUser, id=admin_id)
    
    if request.method == 'POST':
        role = request.POST.get('role', 'admin')
        if role in dict(AdminUser.ROLE_CHOICES):
            admin.role = role
            admin.save()
        return redirect('admin_manage_admins')
    
    return render(request, 'Admin/edit_admin_role.html', {'admin': admin})

