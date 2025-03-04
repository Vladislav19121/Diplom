from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
from .forms import ProductForm, CategoryForm, DiscountForm, RegistrationForm, BuyingForm, OrderStatusForm
from django.contrib.auth.decorators import login_required,  user_passes_test
from django.contrib import messages


from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.mail import send_mail

def is_admin(user):
    return user.is_staff

@csrf_exempt
def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Активировать ваш аккаунт'
            message = render_to_string('acc_activate_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })


            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return render (request, 'acc_activate_sent.html', {'email': to_email})
    else:
        form = RegistrationForm()

    return render (request, 'register.html', {'form': form})
    
def activate(request, uidb64, token):
    try:
        print(f"Функция activate вызвана!" )
        uid = force_str(urlsafe_base64_decode(uidb64))
        print(f'Раскодированный юид: {uid}')
        user = User.objects.get(pk=uid)


    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'acc_active_success.html')
    else:
        return render(request, 'acc_active_fail.html')

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

def user_page(request, id):
    user = get_object_or_404(User, id=id)
    show_button = True
    return render(request, 'user_page.html', {'show_button': show_button})

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

@login_required
@user_passes_test(is_admin)
def add_discount(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        form = DiscountForm(request.POST)
        if form.is_valid():
            discount_value = form.cleaned_data['discount']
            product.discount = discount_value
            product.save()
            return redirect('category_products', id=product.category.id)
    else:
        form = DiscountForm()

    
    return render(request, 'add_discount.html', {'form': form, 'product': product})

@login_required
@user_passes_test(is_admin)
def delete_discount(request, id):
    product = get_object_or_404(Product, id=id)
    product.discount = 0.00
    product.save()
    return redirect('category_products', id=product.category.id)


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
    product.delete()
    return redirect('category_products', id = product.category.id)

@login_required   
def cart(request):
    cart_products = Cart.objects.filter(user=request.user).order_by('added_at')
    print("Содержимое корзины:")
    for item in cart_products:
        print(f"ID: {item.id}, Product: {item.product.name}, Quantity: {item.quantity}")
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
def remove_form_cart(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    cart_item.delete()
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

def order_product(request, id):
    product = get_object_or_404(Product, id=id)
    calculated_price = product.price + 100
    if request.method == 'POST':
        form = BuyingForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity_product']
            calculated_price = product.price * quantity + 1000
            if quantity <= product.stock:
                order = form.save(commit=False)
                order.product = product
                order.user = request.user
                order.price = calculated_price 
                product.stock -= quantity
                product.save()           
                order.save()
                
                cart_items = Cart.objects.filter(product=product, user=request.user)
                for item in cart_items:
                    item.delete()
                
                subject = f'Вы сделали заказ {order.product.name}!'
                message = render_to_string('order_email.html',{
                    'order': order,
                    'product': product,
                    'quantity': quantity,
                    'calculated_price': calculated_price,
                })
                from_email = 'pyshop1912@gmail.com'
                recipient_list = ['pyshop1912@gmail.com', request.user.email]
                send_mail(subject, message, from_email, recipient_list, html_message=message)

                return redirect('orders')
            
            else:
                messages.error(request, f'Вы не можете заказать больше {product.stock} {product.name}, т.к на складе столько нет')
                return render(request, 'buy_product.html', {'form': form, 'calculated_price': calculated_price, 'product': product})
        else:
            messages.error(request, "Ошибка в форме. Проверьте введенные данные.")
            return render(request, 'buy_product.html', {'form': form, 'product': product})
    else:
        form = BuyingForm()

    return render(request, 'buy_product.html', {'form': form, 'product': product, 'calculated_price': calculated_price})

def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    total = sum(order.total_price() for order in orders)
    return render(request, 'orders.html', {'orders': orders, 'total': total})

def delete_order(request, id):
    order = get_object_or_404(Order, id=id, user=request.user)
    order.delete()
    return redirect('orders')

def change_status(request, id):
    order = get_object_or_404(Order, id=id)
    form = OrderStatusForm(instance=order)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('orders')
        else:
            messages.error(request, "Ошибка в форме. Проверьте введенные данные.")
            return render(request, 'orders.html', {'form': form, 'order': order})
        
    return render(request, 'change_status.html', {'form': form, 'order': order})

def change_announcement(request, id):
    announcement = get_object_or_404(Product, id=id)
    form = ProductForm(instance=announcement)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            return redirect('category_products', id=announcement.category.id)
        else:
            messages.error(request, "Ошибка в форме. Проверьте введенные данные.")
            return render(request, 'orders.html', {'form': form, 'announcement': announcement})
        
    return render(request, 'change_announcement.html', {'form': form, 'announcement': announcement})

def my_announcements(request):
    announcements = Product.objects.filter(user=request.user)
    return render(request, 'my_announcements.html', {'announcements': announcements})

def product_annoucnement(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'product_announcement.html', {'product': product})