from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# from django.shortcuts import render
from store.models import Item

def landing_view(request):
    """Public landing page"""
    items = Item.objects.all()[:8]
    return render(request, 'components/landingpage.html', {'items': items})

def signup_view(request):
    """Handle user registration with username, password, confirm password."""
    if request.user.is_authenticated:
        return redirect('landing')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Validation
        if not username or not password or not confirm_password:
            messages.error(request, 'All fields are required.')
            return render(request, 'auth/signup.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'auth/signup.html')

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return render(request, 'auth/signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'auth/signup.html')

        # Create user and log in
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        messages.success(request, f'Welcome to InventoAI, {username}!')
        return redirect('landing')

    return render(request, 'auth/signup.html')




@login_required(login_url='login')
def user_home(request):
    """User home page - shows all products with add to cart"""
    items = Item.objects.all()
    return render(request, 'user/home.html', {'items': items})


def login_view(request):
    """Handle user login with username and password."""
    if request.user.is_authenticated:
        return redirect('landing')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'auth/login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('user_home')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'auth/login.html')

    return render(request, 'auth/login.html')


def logout_view(request):
    """Log the user out and redirect to landing page."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('landing')




# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.contrib.auth import login
from inventoai.form import AdminSignupForm   # Make sure you have this!

def admin_signup_view(request):
    """Signup the admin and redirect to admin page"""
    if request.method == 'POST':
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Admin account created.')
            return redirect('admin_add_items')
    else:
        form = AdminSignupForm()
    
    return render(request, "admin/adminSignup.html", {'form': form})


from .form import AuthenticationForm

def admin_login_view(request):
    """Log the admin in and redirect to admin page"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('add_items')
            else:
                messages.error(request, 'You do not have admin privileges.')
                return redirect('admin_login')
    else:
        form = AuthenticationForm()
    
    # Style the form fields
    form.fields['username'].widget.attrs.update({
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition',
        'placeholder': 'Enter username',
        'id': 'id_username'
    })
    form.fields['password'].widget.attrs.update({
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition',
        'placeholder': '••••••••',
        'id': 'id_password'
    })
    
    return render(request, 'admin/adminLogin.html', {'form': form})


    



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from store.models import Item
from store.addForm import ItemForm


def admin_dashboard(request):
    return redirect('show_items')


def add_item_view(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)  # ← Removed request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, 'Item added successfully!')
            return redirect('show_items')
    else:
        form = ItemForm()
    
    return render(request, 'admin/add_items.html', {'form': form})


def show_items_view(request):
    items = Item.objects.all()
    return render(request, 'admin/show_items.html', {'items': items})


def update_item_view(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)  # ← Removed request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully!')
            return redirect('show_items')
    else:
        form = ItemForm(instance=item)
    
    return render(request, 'admin/update_item.html', {'form': form, 'item': item})


def delete_item_view(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item deleted successfully!')
        return redirect('show_items')
    
    return render(request, 'admin/delete_confirm.html', {'item': item})