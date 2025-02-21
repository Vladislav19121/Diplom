from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
from .forms import ProductForm, CategoryForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required,  user_passes_test

def is_admin(user):
    return user.is_staff

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

@login_required
@user_passes_test(is_admin)
def add_category(request):
    categories = Category.objects.all()
    show_form = False
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            category.save()
            return redirect('home')
    else:
        form = CategoryForm()
        if 'add_category' in request.GET:  
            show_form = True

    return render(request, 'home.html', {'categories': categories, 'form': form, 'show_form': show_form})

@login_required
@user_passes_test(is_admin)
def delete_category(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    return redirect('home')

def open_category(request, id):
    category = get_object_or_404(Category, id=id)
    products = category.products.all()
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    error_message = None
    try:
        if min_price:
            min_price = float(min_price)
            products = products.filter(price__gte=min_price) #Это "look-up" (поиск) в Django ORM. Он означает "greater than or equal to" (больше или равно).
        if max_price:
            max_price = float(max_price)
            products = products.filter(price__lte=max_price) #less than or equal to
    except ValueError:
        error_message = "Пожалуйста, введите корректные числовые значения для цены."

    if min_price and max_price and min_price > max_price:
        error_message = "Минимальная цена не может быть больше максимальной."
    return render(request, 'category_products.html', {'products': products, 'category': category, 
                                                          'min_price': min_price, 'max_price': max_price, 'error': error_message})
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


