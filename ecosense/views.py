from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from order.models import Order, OrderItem, OrderStatus
from sensor.models import Sensor, SensorData, SensorItem
from group.models import *
from sensor.forms import SelectGroupForm
from django.contrib import messages
from django.db.models import Sum
from django.utils.timezone import now
from collections import defaultdict
import calendar
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def unauthorized(request):

    return render(request, template_name="unauthorized.html", context={
        "title": "Unauthorized"
    })

# Home page
def home(request):

    title = "Home"

    context = {
        "title": title
    }

    if request.user.is_authenticated:
        
        # Customer dashboard
        if hasattr(request.user, 'customer'):
            
            # Get all customer sensorItems that are not used in any group
            sensorItemsNotUsed = SensorItem.objects.filter(customer=request.user.customer, group=None).order_by("registration_code")

            # Get all customer groups
            groups = Group.objects.filter(customer=request.user.customer).order_by("name")

            selectGroupForm = SelectGroupForm()

            context = {
                "title": title,
                "sensorItemsNotUsed": sensorItemsNotUsed,
                "groups": groups,
                "selectGroupForm": selectGroupForm
            }

        elif hasattr(request.user, 'staff') and request.user.staff.is_sales:
            
            try:
                
                orders = Order.objects.exclude(status=OrderStatus.CANCELLED)
                
                if orders:

                    # (1) Most purchased sensors

                    sensorTime = request.GET.get("sensorTime", "Today")
                    order_items = OrderItem.objects.filter(order__in=orders)

                    # Filter by time
                    if sensorTime == "Today":
                        today = now().date()
                        order_items = order_items.filter(order__created_at__date=today)

                    elif sensorTime == "Week":
                        today = now()
                        start_of_month = today.replace(day=1)
                        order_items = order_items.filter(order__created_at__date__gte=start_of_month)

                    elif sensorTime == "Month":
                        today = now()
                        start_of_month = today.replace(day=1)
                        order_items = order_items.filter(order__created_at__date__gte=start_of_month)

                    elif sensorTime == "Year":
                        today = now()
                        start_of_year = today.replace(month=1, day=1)
                        order_items = order_items.filter(order__created_at__date__gte=start_of_year)

                    mostPurchasedSensors = (
                        order_items.values("sensor")
                        .annotate(quantity=Sum("quantity"))
                        .order_by("-quantity")[:10]
                    )

                    sensor_ids = [item["sensor"] for item in mostPurchasedSensors]
                    sensors = Sensor.objects.in_bulk(sensor_ids)

                    mostPurchasedSensorsResult = []
                    for item in mostPurchasedSensors:
                        sensor_obj = sensors.get(item["sensor"])
                        if sensor_obj:
                            mostPurchasedSensorsResult.append({
                                "sensor": {
                                    "id": sensor_obj.id,
                                    "name": sensor_obj.name,  # o il campo che usi per visualizzare il nome
                                    # aggiungi altri campi se ti servono nel grafico
                                },
                                "quantity": item["quantity"]
                            })

                    # ------------------------------------------------------------------------------------------------------

                    # (2) Geographical distribution of sensors

                    # Get all sensorItem purchased
                    sensorItems = SensorItem.objects.filter(order__isnull=False)

                    # Ex: countries: [
                    #     {
                    #         "country": 'Italy',
                    #         "quantity": 10
                    #     }
                    # ]
                    
                    country_data = defaultdict(int)

                    for sensorItem in sensorItems:

                        # For each sensor Item:
                        # If the country of the shipping address is already in the list, I just increase the counter; 
                        # otherwise, I create a new item in the list.

                        country = sensorItem.order.customer.shippingAddress.country
                        country_data[country] += 1

                    # Convert country_data in list
                    countries = [{"country": c, "quantity": q} for c,q in country_data.items()]

                    #----------------------------------------------------------------------------------------------------

                    # (3) Number of Orders

                    # Ex: ordersGraph: [
                    #     {
                    #         "country": 'Italy',
                    #         "quantity": 10
                    #     }
                    # ]

                    orders_current_year = orders.filter(created_at__year=now().year)

                    orders_data = {calendar.month_name[m]: 0 for m in range(1, 13)}

                    for order in orders_current_year:
                        month_name = calendar.month_name[order.created_at.month]
                        orders_data[month_name] += 1

                    ordersGraph = [
                        {"month": month, "quantity": orders_data[month]}
                        for month in calendar.month_name[1:]
                    ]

                    #----------------------------------------------------------------------------------------------------

                    # (4) Profit

                    orders_data = {calendar.month_name[m]: 0 for m in range(1, 13)}

                    for order in orders_current_year:
                        month_name = calendar.month_name[order.created_at.month]
                        orders_data[month_name] += order.total_price

                    profits = [
                        {"month": month, "profit": orders_data[month]}
                        for month in calendar.month_name[1:]
                    ]

                    totalProfit = sum(float(x["profit"]) for x in profits if x["profit"])
                    totalProfit_str = f"{totalProfit:.2f}"

                    context = {
                        "title": title,
                        "ordersExist": True,
                        "mostPurchasedSensors": mostPurchasedSensorsResult,
                        "sensorTime": sensorTime,
                        "countries": countries,
                        "ordersGraph": ordersGraph,
                        "profits": profits,
                        "totalProfit": totalProfit_str
                    }
                
                else:

                    context = {
                        "title": title,
                        "ordersExist": False
                    }

            except Exception as e:
                messages.error(request, f"An error occured while loading the homepage: {str(e)}")

        elif hasattr(request.user, 'staff') and request.user.staff.is_technical:
            
            try:

                # Get all registered sensors
                registeredSensors = SensorItem.objects.filter(is_registered=True,customer__isnull=False, order__isnull=False)

                # Recover params from query
                code = request.GET.get('filter_code')
                customer = request.GET.get('filter_customer')

                if code:
                    sensor_ids = []

                    for sensor in registeredSensors:

                        if sensor.get_registration_code() == code:
                            sensor_ids.append(sensor.pk)

                    registeredSensors = registeredSensors.filter(id__in=sensor_ids)

                if customer:
                    registeredSensors = registeredSensors.filter(customer__user__username=customer)           
                                   
                if registeredSensors:
                    
                    paginate_by = 20

                    # Create the paginator
                    paginator = Paginator(registeredSensors, paginate_by)

                    # Recove the page number from querystring
                    page_number = request.GET.get("page")

                    try:
                        page_obj = paginator.page(page_number)
                    except PageNotAnInteger:
                        page_obj = paginator.page(1)
                    except EmptyPage:
                        page_obj = paginator.page(paginator.num_pages)

                    context = {
                        "title": title,
                        'registeredSensors': registeredSensors,      
                        'page_obj': page_obj,     
                        'paginator': paginator,  
                        'is_paginated': paginator.num_pages > 1,
                    }


                else:
                    context = {
                        "title": title,
                        "registeredSensors": registeredSensors
                    }

            except Exception as e:
                messages.error(request, f"An error occured while loading the homepage: {str(e)}")

        else:
            logout(request)
            return redirect("home")
        
    return render(request, 'home.html', context=context)
