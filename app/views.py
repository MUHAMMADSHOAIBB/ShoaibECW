from django.shortcuts import render,redirect
from django.views import View
from .models import Cart,Customer,Product,orderplaced
from .forms import CustomerRegistrationForm,MyPasswordChangeForm,CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# def home(request):
#  return render(request, 'app/home.html')
             #Product View Homepage
class Productview(View):
 def get(self,request):
  total_items=0
  top_wears = Product.objects.filter(category='TW')
  bottom_wears = Product.objects.filter(category='BW')
  mobiles = Product.objects.filter(category='M')
  upper_wears = Product.objects.filter(category='C')
  if request.user.is_authenticated:
   total_items=len(Cart.objects.filter(user=request.user))
  return render(request, 'app/home.html',
                {'top_wears':top_wears,'bottom_wears':bottom_wears,'mobiles':mobiles,'upper_wears':upper_wears,'total_items':total_items})


                 #product Detail view when we open the product
class Productdetailview(View):
 def get(self,request,pk):
  total_items = 0
  product= Product.objects.get(pk=pk)
  item_already_in_cart = False
  if request.user.is_authenticated:
   total_items = len(Cart.objects.filter(user=request.user))
   item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
  return render(request,'app/productdetail.html',{'product':product,'item_already_in_cart':item_already_in_cart,'total_items':total_items})
                                 #Add to cart
@login_required()
def add_to_cart(request):
 user = request.user
 product_id =request.GET.get('prod_id')
 product = Product.objects.get(id=product_id)
 Cart(user=user,product=product).save()
 return redirect('/cart')
                                 #Show-Cart
def show_cart(request):
 total_items = 0
 if request.user.is_authenticated:
  total_items = len(Cart.objects.filter(user=request.user))
  user = request.user
  cart =Cart.objects.filter(user=user)
  amount = 0.0
  shipping_amount = 70.0
  total_amount = 0.0
  cart_product = [p for p in Cart.objects.all() if p.user==user]
  # print(cart_product)
  if cart_product:
   for p in cart_product:
    temp_amount= (p.quantity * p.product.discounted_price)
    amount +=temp_amount
    total_amount=amount+shipping_amount
   return render(request, 'app/addtocart.html',{'carts':cart,'total_amount':total_amount,'amount':amount,'total_items':total_items})
  else:
   return render(request,'app/emptycart.html')

def plus_cart(request):
 if request.method =='GET':
  prod_id = request.GET['prod_id']
  c = Cart.objects.get(Q(product=prod_id) &Q(user=request.user))
  c.quantity+=1
  c.save()
  amount = 0.0
  shipping_amount = 70.0

  cart_product = [p for p in Cart.objects.all() if p.user == request.user]
  for p in cart_product:
   temp_amount = (p.quantity * p.product.discounted_price)
   amount += temp_amount

  data ={
    'quantity':c.quantity,
    'amount':amount,
    'totalamount':amount + shipping_amount
   }
  return JsonResponse(data)

def minus_cart(request):
 if request.method =='GET':
  prod_id = request.GET['prod_id']
  c = Cart.objects.get(Q(product=prod_id) &Q(user=request.user))
  c.quantity-=1
  c.save()
  amount = 0.0
  shipping_amount = 70.0

  cart_product = [p for p in Cart.objects.all() if p.user == request.user]
  for p in cart_product:
   temp_amount = (p.quantity * p.product.discounted_price)
   amount += temp_amount

  data ={
    'quantity':c.quantity,
    'amount':amount,
    'totalamount':amount + shipping_amount
   }
  return JsonResponse(data)

def remove_cart(request):
 if request.method =='GET':
  prod_id = request.GET['prod_id']
  c = Cart.objects.get(Q(product=prod_id) &Q(user=request.user))
  c.delete()

  amount = 0.0
  shipping_amount = 70.0

  cart_product = [p for p in Cart.objects.all() if p.user == request.user]
  for p in cart_product:
   temp_amount = (p.quantity * p.product.discounted_price)
   amount += temp_amount

  data ={
    'amount':amount,
    'totalamount':amount + shipping_amount
   }
  return JsonResponse(data)
                                      #buy now
def buy_now(request):
 return render(request, 'app/buynow.html')
#address
def address(request):
 add = Customer.objects.filter(user = request.user)
 return render(request, 'app/address.html',{'add':add, 'active': 'btn-primary'})
                                      #orders
@login_required()
def orders(request):
 op = orderplaced.objects.filter(user=request.user)
 return render(request, 'app/orders.html',{'order_placed':op})


                            # For Mobile slide
def mobile(request,data =None):
 total_items = 0
 if request.user.is_authenticated:
  total_items = len(Cart.objects.filter(user=request.user))
 if data == None:
  mobiles=Product.objects.filter(category='M')
 elif data == "samsung" or data == "Iphone":
  mobiles = Product.objects.filter(category='M').filter (brand=data)
 elif data == 'below':
  mobiles = Product.objects.filter(category='M').filter(Selling_price__lt=30000)
 elif data == 'above':
  mobiles = Product.objects.filter(category='M').filter(Selling_price__gt=30000)
 return render(request, 'app/mobile.html',{'mobiles':mobiles,'total_items':total_items})

# def login(request):
#  return render(request, 'app/login.html')
                                      #Coat slide
def coat(request):
 return render(request, 'app/upper_wear.html')

                                 #customer registration
class CustomerRegistrationView(View):
 def get(self,request):
  form = CustomerRegistrationForm
  return render(request, 'app/customerregistration.html',{'form':form})
 def post(self,request):
  form = CustomerRegistrationForm(request.POST)
  if form.is_valid():
   messages.success(request,'Congratulations !! Registered successfully')
   form.save()
  return render(request, 'app/customerregistration.html', {'form': form})
                                #CheckOUT
@login_required()
def checkout(request):
 user = request.user
 add = Customer.objects.filter(user=user)
 cart_items = Cart.objects.filter(user=user)
 amount = 0.0
 shipping_amount = 70.0
 total_amount = 0.0
 cart_product = [p for p in Cart.objects.all() if p.user == request.user]
 if cart_product:
  for p in cart_product:
   temp_amount = (p.quantity * p.product.discounted_price)
   amount += temp_amount
  total_amount = amount+shipping_amount
 return render(request, 'app/checkout.html',{'add':add,'total_amount':total_amount,'cart_items':cart_items})
                                    # paymentdone
@login_required()
def payment_done(request):
 user = request.user
 custid = request.GET.get('custid')
 customer = Customer.objects.get(id=custid)
 cart = Cart.objects.filter(user=user)
 for c in cart:
  orderplaced(user=user,customer=customer,product=c.product,quantity=c.quantity).save()
  c.delete()
 return redirect('orders')
                                    #shirt slide
def shirt(request,data =None):
 total_items = 0
 if request.user.is_authenticated:
  total_items = len(Cart.objects.filter(user=request.user))
 if data == None:
  shirt=Product.objects.filter(category='TW')
 elif data =='outerfit' or data =='edenrobe':
  shirt = Product.objects.filter(category='TW').filter (brand=data)
 elif data == 'below':
  shirt = Product.objects.filter(category='TW').filter(Selling_price__lt=2000)
 elif data == 'above':
  shirt = Product.objects.filter(category='TW').filter(Selling_price__gt=2000)
 return render(request, 'app/topwear.html',{'shirt':shirt,'total_items':total_items})
                                      #jeans slide
def jeans(request,data =None):
 total_items = 0
 if request.user.is_authenticated:
  total_items = len(Cart.objects.filter(user=request.user))
 if data == None:
  jeans=Product.objects.filter(category='BW')
 elif data =='outerfit' or data =='Edenrobe':
  jeans = Product.objects.filter(category='BW').filter (brand=data)
 elif data == 'below':
  jeans = Product.objects.filter(category='BW').filter(Selling_price__lt=2000)
 elif data == 'above':
  jeans = Product.objects.filter(category='BW').filter(Selling_price__gt=2000)
 return render(request, 'app/bottom_wear.html',{'jeans':jeans,'total_items':total_items})

                                  # Coat slide
def coats(request,data =None):
 total_items = 0
 if request.user.is_authenticated:
  total_items = len(Cart.objects.filter(user=request.user))
 if data == None:
  coats=Product.objects.filter(category='C')
 elif data =='outerfit' or data =='Edenrobe':
  coats = Product.objects.filter(category='C').filter (brand=data)
 elif data == 'below':
  coats = Product.objects.filter(category='C').filter(discounted_price__lt=2000)
 elif data == 'above':
  coats = Product.objects.filter(category='C').filter(discounted_price__gt=2000)
 return render(request, 'app/upper_wear.html',{'coats':coats,'total_items':total_items})
                                      #Profile
@method_decorator(login_required, name='dispatch')
class ProfileView(View):
 def get(self,request):
  form = CustomerProfileForm()
  return render(request,'app/profile.html',{'form':form,'active':'btn-primary'})

 def post(self,request):
  form = CustomerProfileForm(request.POST)
  if form.is_valid():
   usr = request.user
   name= form.cleaned_data['name']
   locality= form.cleaned_data['locality']
   city= form.cleaned_data['city']
   Zipcode= form.cleaned_data['Zipcode']
   state= form.cleaned_data['state']
   reg = Customer(user=usr,name=name,locality=locality,city=city,Zipcode=Zipcode,state=state)
   reg.save()
   messages.success(request, 'Congratulations !! Profile Updated successfully')
  return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary'})