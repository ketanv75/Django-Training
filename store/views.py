from django.shortcuts import render
from .models import Product, Order, OrderItem, ShippingAddress

from django.http import JsonResponse
import json
import datetime

from .utils import cookieCart, cartData, guestOrder

# Create your views here.


def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
                 
    products = Product.objects.all()
    context={'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def cart(request):

    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
        

    # here the 'created' field is passed just to avoid the compilation warning
    context={'items' : items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):

    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']


    # here the 'created' field is passed just to avoid the compilation warning
    context={'items' : items, 'order': order, 'cartItems': cartItems}

    return render(request, 'store/checkout.html', context)

def updateItem(request):

    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('productID', productId )
    print('action', action )

    # How the customer is accessed using request.user.customer ?? 
    customer = request.user.customer
    product = Product.objects.get(id=productId)

    order, created = Order.objects.get_or_create(
            customer= customer, complete = False
        )
    
    print(created)

    orderItem, created = OrderItem.objects.get_or_create(order = order, 
        product = product )
    
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    else:
        print('Unidentified action')
    
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    
    return JsonResponse('item Added', safe=False)


def processOrder(request):
    transaction_Id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    print(data)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer= customer, complete = False
        )

        print(created)

    else:
        customer, order = guestOrder(request, data)
                
    total = float(data['form']['total'])
    order.transaction_Id = transaction_Id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer = customer,
            order = order,
            address = data['shipping']['address'],
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            zipcode = data['shipping']['zipcode'],
            country = data['shipping']['country']
        )

    return JsonResponse('Payment Complete', safe=False)

