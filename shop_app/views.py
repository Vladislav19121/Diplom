from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
from .forms import ProductForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

def registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user:
                login(request, user)
                return redirect('home')
    else:
        form = UserCreationForm()
        
    
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user_log = authenticate(request, username=username, password=password)
        
        if user_log is not None:
            login(request, user_log)  
            return redirect('home')  
        else:
            error_message = "Неверное имя пользователя или пароль."
            return render(request, 'login.html', {'error': error_message})

    return render(request, 'login.html')    
            
def logout_view(request):
    logout(request)
    return redirect('home')

def home(request):
    categories = Category.objects.all()
    return render(request, 'home.html', {'categories': categories})

def open_category(request, id):
    category = get_object_or_404(Category, id=id)
    products = category.products.all()
    return render(request, 'category_products.html', {'products': products, 'category': category})

@login_required
def add_product(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.category = category 
            product.user = request.user
            product.save()
            return redirect('category_products', id=category.id)
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form, 'category': category})

def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.user == product.user:
        product.delete()
        return redirect('category_products', id = product.category.id)

@login_required   
def cart(request):
    cart_products = Cart.objects.filter(user=request.user).order_by('added_at')
    total = sum(product.total_price() for product in cart_products)
    return render(request, 'cart.html', {'cart_products': cart_products, 'total': total})

@login_required   
def add_product_in_cart(request, id):
    product = get_object_or_404(Product, id=id)
    cart_item, created = Cart.objects.get_or_create(product=product, user=request.user)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        return redirect('cart')
    else:
        return redirect('category_products', id = product.category.id)

@login_required   
def remove_form_cart(request, cart_product_id):
    cart_product = get_object_or_404(Cart, id=cart_product_id, user=request.user)
    cart_product.delete()
    return redirect('cart')

def search_results(request):
    query = request.GET.get('q')
    product_results = []

    if query:
        product_results = Product.objects.filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query) 
        )

    return render(request, 'search_results.html', {'query': query, 'product_results': product_results})