from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import *
from datetime import date
from decimal import Decimal
from django.db.models import F , DecimalField, ExpressionWrapper
from django.db.models.functions import ExtractWeekDay
import pytz
from calendar import monthrange

#====================================================================================================================
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='تسجيل دخول',
            action_sort = 'تسجيل دخول',
            model_affected=f'تم تسجيل الدخول للمستخدم',
        )

            return redirect('sales')
        else:
            messages.warning(request, 'كلمة المرور غير صحيحة')

    return render(request, 'login.html')
#====================================================================================================================
def logout_user(request):
    logout(request)
    return render(request, 'logout.html')
#====================================================================================================================
@login_required(login_url="login")
def home(request) :
    clients_number = Client.objects.count()
    items_number = Item.objects.count()
    suppliers_number = Supplier.objects.count
    all_items = Item.objects.all().order_by("-date")
    shorts = [item for item in all_items if item.quantity == 0 ]
    shorts_number = 0
    for short in shorts :
        shorts_number += 1
    context = {
        "clients_number" : clients_number,
        "items_number" : items_number,
        "suppliers_number" : suppliers_number,
        "shorts_number" : shorts_number,
    }
    return render(request, "home.html" , context)
#====================================================================================================================
def kinds(request):
    kinds = Kind.objects.all()
    if "addKind" in request.POST :
        name = request.POST.get('name')
        Kind.objects.create(name=name)
        RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type='أضافة نوع',
        action_sort = 'إضافة',
        model_affected=f'تم إضافة نوع باسم {name}',
    )
        messages.success(request,"تم اضافة نوع بنجاح")
        return redirect("kinds")
    context ={'kinds': kinds}
    return render(request, "kinds.html", context)
#====================================================================================================================
def kind_delete(request, id):
    kind_to_delete = get_object_or_404(Kind, id =id )

    if "kindDelete" in request.POST :
        RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type='حذف نوع',
        action_sort = 'حذف',
        model_affected=f'تم حذف النوع {kind_to_delete.name}',
    )
        kind_to_delete.delete()
        messages.success(request, "تم حذف النوع بنجاح")
        return redirect("kinds")
#====================================================================================================================
def items(request):
    items = Item.objects.all().order_by("-date")
    item_value_total = 0
    for item in items:
        item_value = item.quantity * item.price
        item_value_total += item_value
    
    kinds = Kind.objects.all()
    paginator = Paginator(items ,20)
    page = request.GET.get('page')
    try:
        item_list = paginator.page(page)
    except PageNotAnInteger:
        item_list = paginator.page(1)
    except EmptyPage :
        item_list = paginator.page(paginator.num_pages)

    if "addItem" in request.POST:
        name = request.POST.get('name')
        kind_name = request.POST.get('kind')
        prand = request.POST.get('prand')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        item_date = request.POST.get('date')
        if not item_date:
            item_date = date.today()

        item_id = request.POST.get('item_id', None)
        kind = Kind.objects.get(name=kind_name)
        if Item.objects.filter(name=name, kind = kind).exclude(id=item_id).exists():
            messages.warning(request, f'المنتج ({name})و في نفس النوع موجود بالفعل في قاعدة البيانات')
            return redirect("items")

        Item.objects.create(name=name, kind=kind, prand=prand, quantity=quantity, price=price, date=item_date)
        RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type='إضافة صنف',
        action_sort = 'إضافة',
        model_affected=f'تم إضافة صنف {name} و بسعر {price} جنيها',
    )
        messages.success(request, "تم اضافة صنف بنجاح")
        return redirect("items")
    
    elif 'search' in request.POST :
        search_input = request.POST.get('searchInput')
        results = [result['id'] for result in Item.objects.all().filter(Q(name__icontains=search_input)).values()]
        item_list = [Item.objects.get(pk = id) for id in results]
    
    context ={
        'items': item_list,
        'kinds': kinds,
        'item_value_total': item_value_total,
    }
    return render(request, "items.html", context)
#====================================================================================================================
def item_delete(request, id):
    item_to_delete = get_object_or_404(Item, id =id )

    if "itemDelete" in request.POST :
        RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type='حذف صنف',
        action_sort = 'حذف',
        model_affected=f'تم حذف الصنف {item_to_delete.name}',
    )
        item_to_delete.delete()
        messages.success(request, "تم حذف المنتج بنجاح")
        return redirect("items")
#====================================================================================================================
def item_update(request, id):
    old_item_data = None

    if 'itemUpdate' in request.POST:
        name = request.POST['name']
        kind_name = request.POST['kind_name']
        prand = request.POST['prand']
        quantity = request.POST['quantity']

        kind = Kind.objects.get(name=kind_name)
        edit = Item.objects.get(id=id)

        old_item_data = Item.objects.filter(id=id).values().first()
        old_name = old_item_data['name']
        old_kind_name = old_item_data['kind_id']
        old_prand = old_item_data['prand']
        old_quantity = old_item_data['quantity']

        if name != old_name:
            if Item.objects.filter(name=name, kind=kind).exclude(id=id).exists():
                messages.warning(request, f'المنتج ({name}) و في نفس النوع موجود بالفعل في قاعدة البيانات')
                return redirect("items")

        changes = []
        if name != old_name:
            changes.append(f'اسم المنتج من {old_name} إلى {name}')
        if kind.id != old_kind_name:
            changes.append(f'نوع المنتج من {Kind.objects.get(id=old_kind_name).name} إلى {kind.name}')
        if prand != old_prand:
            changes.append(f'العلامة التجارية من {old_prand} إلى {prand}')
        if quantity != old_quantity:
            changes.append(f'الكمية من {old_quantity} إلى {quantity}')

        edit.name = name
        edit.kind = kind
        edit.prand = prand
        edit.quantity = quantity
        edit.save()

        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='تعديل صنف',
            action_sort='تعديل',
            model_affected=f'تم تعديل بيانات الصنف: {", ".join(changes)}',
        )

        messages.success(request, 'تم تعديل بيانات الصنف بنجاح', extra_tags='success')
        return redirect("items")
    
    if 'itemUpdateShort' in request.POST:
        name = request.POST['name']
        kind_name = request.POST['kind_name']
        prand = request.POST['prand']
        quantity = request.POST['quantity']

        kind = Kind.objects.get(name=kind_name)
        edit = Item.objects.get(id=id)

        old_item_data = Item.objects.filter(id=id).values().first()
        old_name = old_item_data['name']
        old_kind_name = old_item_data['kind_id']
        old_prand = old_item_data['prand']
        old_quantity = old_item_data['quantity']

        if name != old_name:
            if Item.objects.filter(name=name, kind=kind).exclude(id=id).exists():
                messages.warning(request, f'المنتج ({name}) و في نفس النوع موجود بالفعل في قاعدة البيانات')
                return redirect("shorts")

        changes = []
        if name != old_name:
            changes.append(f'اسم المنتج من {old_name} إلى {name}')
        if kind.id != old_kind_name:
            changes.append(f'نوع المنتج من {Kind.objects.get(id=old_kind_name).name} إلى {kind.name}')
        if prand != old_prand:
            changes.append(f'العلامة التجارية من {old_prand} إلى {prand}')
        if quantity != old_quantity:
            changes.append(f'الكمية من {old_quantity} إلى {quantity}')

        edit.name = name
        edit.kind = kind
        edit.prand = prand
        edit.quantity = quantity
        edit.save()

        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='تعديل صنف',
            action_sort='تعديل',
            model_affected=f'تم تعديل بيانات الصنف: {", ".join(changes)}',
        )

        messages.success(request, 'تم تعديل بيانات الصنف بنجاح', extra_tags='success')
        return redirect("shorts")

    else:
        try:
            old_item_data = Item.objects.filter(id=id).values().first()
            item = Item.objects.get(id=id)
        except Item.DoesNotExist:
            messages.error(request, 'حدث خطأ، الصنف غير موجود', extra_tags='error')
            return redirect("items")

    context = {"item": item, "id": id, "old_item_data": old_item_data}
    return render(request, 'itemupdate.html', context)
#====================================================================================================================
def sale_page(request):
    items = Item.objects.all().order_by("-date")
    clients = Client.objects.all()

    paginator = Paginator(items ,20)
    page = request.GET.get('page')
    try:
        items_list = paginator.page(page)
    except PageNotAnInteger:
        items_list = paginator.page(1)
    except EmptyPage :
        items_list = paginator.page(paginator.num_pages)

    if 'search' in request.POST :
        search_input = request.POST.get('searchInput')
        results = [result['id'] for result in Item.objects.all().filter(Q(name__icontains=search_input)).values()]
        items_list = [Item.objects.get(pk = id) for id in results]

    context ={
        "items" : items_list,
        "clients" : clients,
    }

    return render(request, "sales.html", context)
#====================================================================================================================
@login_required(login_url="login")
def sell(request, id):
    if "sell" in request.POST:
        item_id = request.POST.get('item')
        item = get_object_or_404(Item, pk=item_id)
        
        item_id = request.POST.get('item')
        sale_date = request.POST.get('date')  
        client_name = request.POST.get('client_name')
        client_phone = request.POST.get('client_phone')
        crash = request.POST.get('crash')
        paid = request.POST.get('paid')
        remain = request.POST.get('remain')
        method = request.POST.get('method')
        sale_price = request.POST.get('sale_price')
        sale_quantity = request.POST.get('sale_quantity')

        client_name = client_name.strip()

        sale_price = Decimal(sale_price)
        sale_quantity = Decimal(sale_quantity)
        paid = Decimal(paid)
        remain = Decimal(remain)

        if not client_name:
            client_name = "-"
        if not sale_date :
            sale_date = date.today()
        if sale_quantity > item.quantity:
            messages.error(request, "الكمية المباعة اكبر من الكمية المتبقية")
            return redirect("sales")
        if not paid:
            paid = 0
        if not crash:
            crash = "-"
        if not client_phone:
            client_phone = "-"
        if client_name :
            if Client.objects.filter(name=client_name).exclude(id=id).exists():
                client = Client.objects.get(name=client_name) 
                Sale.objects.create(client=client, item_id=item_id, date=sale_date, crash=crash,
                            sale_price=sale_price, remain=remain, paid=paid, sale_quantity=sale_quantity,
                            client_phone=client_phone, method=method)
                RecentAction.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action_type='إضافة عملية بيع',
                action_sort = 'إضافة',
                model_affected=f'تم بيع كمية {sale_quantity} من صنف {item.name} باجمالي تكلفة {sale_quantity*sale_price} جنيها',
            )

                Item.objects.filter(id=item_id).update(quantity=F('quantity') - sale_quantity)
                messages.success(request, "تمت إضافة عملية بيع بنجاح")
                return redirect("sales")       

            else :
                try :
                    client = Client.objects.get(name=client_name)
                except Client.DoesNotExist:
                    client = Client.objects.create(name=client_name, phone = "-", opening_balance = 0, notes="-")
                    Sale.objects.create(client=client, item_id=item_id, date=sale_date, crash=crash,
                                sale_price=sale_price, remain=remain, paid=paid, sale_quantity=sale_quantity,
                                client_phone=client_phone, method=method)
                    RecentAction.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    action_type='إضافة عملية بيع',
                    action_sort = 'إضافة',
                    model_affected=f'تم بيع كمية {sale_quantity} من صنف {item.name} باجمالي تكلفة {sale_quantity*sale_price} جنيها',
                )

                    Item.objects.filter(id=item_id).update(quantity=F('quantity') - sale_quantity)
                    messages.success(request, "تمت إضافة عملية بيع بنجاح")
                    return redirect("sales")       
            
        
        Sale.objects.create(client_name=client_name, item_id=item_id, date=sale_date, crash=crash,
                                   sale_price=sale_price, remain=remain, paid=paid, sale_quantity=sale_quantity,
                                   client_phone=client_phone, method=method)
        RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type='إضافة عملية بيع',
        action_sort = 'إضافة',
        model_affected=f'تم بيع كمية {sale_quantity} من صنف {item.name} باجمالي تكلفة {sale_quantity*sale_price} جنيها',
    )
        Item.objects.filter(id=item_id).update(quantity=F('quantity') - sale_quantity)

        messages.success(request, "تمت إضافة عملية بيع بنجاح")
        return redirect("sales")  
    
def sell3(request):
    if "sell3" in request.POST :
        sale_date = request.POST.get('date')  
        client_name = request.POST.get('client_name')
        client_phone = request.POST.get('client_phone')
        crash = request.POST.get('crash')
        paid = request.POST.get('paid')
        sale_price = request.POST.get('sale_price')
        sale_price = Decimal(sale_price)

        client_name = client_name.strip()
        paid = Decimal(paid)
        if not client_name:
            client_name = "-"
        if not sale_date :
            sale_date = date.today()
        if not paid:
            paid = 0
        if not client_phone:
            client_phone = "-"
        if client_name :
            if Client.objects.filter(name=client_name).exists():
                client = Client.objects.get(name=client_name) 
                Sale.objects.create(client=client, date=sale_date, crash=crash,
                            paid=paid,sale_quantity=1,
                              client_phone=client_phone,
                                sale_price =sale_price)
                RecentAction.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action_type='إضافة عملية بيع',
                action_sort = 'إضافة',
                model_affected=f'تم اضافة عملية بيع كصيانة من نوع {crash} بقيمة {sale_price} جنيها',
            )
                messages.success(request, "تمت إضافة عملية بيع بنجاح")
                return redirect("sales")       

            else :
                try :
                    client = Client.objects.get(name=client_name)
                except Client.DoesNotExist:
                    client = Client.objects.create(name=client_name, phone = "-", opening_balance = 0, notes="-")
                Sale.objects.create(client=client, date=sale_date, crash=crash,
                            paid=paid,sale_quantity=1,
                              client_phone=client_phone,
                                sale_price =sale_price)
                RecentAction.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action_type='إضافة عملية بيع',
                action_sort = 'إضافة',
                model_affected=f'تم اضافة عملية بيع كصيانة من نوع {crash} بقيمة {sale_price} جنيها',
            )         
                messages.success(request, "تمت إضافة عملية بيع بنجاح")
                return redirect("sales")       
            
        messages.success(request, "تمت إضافة عملية بيع بنجاح")
        return redirect("sales")  



#====================================================================================================================
def sale_update(request, id):
    old_sale_data = None

    if "saleUpdate" in request.POST:
        client_name = request.POST["client_name"]
        paid = request.POST["paid"]
        method = request.POST["method"]

        old_sale_data = Sale.objects.filter(id=id).values().first()
        edit = Sale.objects.get(id=id)

        old_client_name = old_sale_data['client_name']
        old_paid = old_sale_data['paid']
        old_method = old_sale_data['method']

        changes = []
        if client_name != old_client_name:
            changes.append(f'اسم العميل من {old_client_name} إلى {client_name}')
        if paid != old_paid:
            changes.append(f'المبلغ المدفوع من {old_paid} إلى {paid}')
        if method != old_method:
            changes.append(f'طريقة الدفع من {old_method} إلى {method}')

        edit.client_name = client_name
        edit.paid = paid
        edit.method = method
        edit.save()

        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='تعديل عملية',
            action_sort='تعديل',
            model_affected=f'تم تعديل بيانات العملية: {", ".join(changes)}',
        )

        messages.success(request, 'تم تعديل بيانات العملية بنجاح', extra_tags='success')
        return redirect("profits")  
    
    if "saleUpdate2" in request.POST:
        client_name = request.POST["client_name"]
        paid = request.POST["paid"]
        method = request.POST["method"]

        old_sale_data = Sale.objects.filter(id=id).values().first()
        edit = Sale.objects.get(id=id)

        old_client_name = old_sale_data['client_name']
        old_paid = old_sale_data['paid']
        old_method = old_sale_data['method']

        changes = []
        if client_name != old_client_name:
            changes.append(f'اسم العميل من {old_client_name} إلى {client_name}')
        if paid != old_paid:
            changes.append(f'المبلغ المدفوع من {old_paid} إلى {paid}')
        if method != old_method:
            changes.append(f'طريقة الدفع من {old_method} إلى {method}')

        edit.client_name = client_name
        edit.paid = paid
        edit.method = method
        edit.save()

        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='تعديل عملية',
            action_sort='تعديل',
            model_affected=f'تم تعديل بيانات العملية: {", ".join(changes)}',
        )

        messages.success(request, 'تم تعديل بيانات العملية بنجاح', extra_tags='success')
        return redirect("tempsales")  

    if "saleUpdate3" in request.POST:
        sale = get_object_or_404(Sale, id=id)
        client_id = sale.client.id

        client_name = request.POST["client_name"]
        paid = request.POST["paid"]
        method = request.POST["method"]

        old_sale_data = Sale.objects.filter(id=id).values().first()
        edit = Sale.objects.get(id=id)

        old_client_name = old_sale_data['client_name']
        old_paid = old_sale_data['paid']
        old_method = old_sale_data['method']

        changes = []
        if client_name != old_client_name:
            changes.append(f'اسم العميل من {old_client_name} إلى {client_name}')
        if paid != old_paid:
            changes.append(f'المبلغ المدفوع من {old_paid} إلى {paid}')
        if method != old_method:
            changes.append(f'طريقة الدفع من {old_method} إلى {method}')

        edit.client_name = client_name
        edit.paid = paid
        edit.method = method
        edit.save()

        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='تعديل عملية',
            action_sort='تعديل',
            model_affected=f'تم تعديل بيانات العملية: {", ".join(changes)}',
        )

        messages.success(request, 'تم تعديل بيانات العملية بنجاح', extra_tags='success')
        return redirect("clientpage", id=client_id)  
    
    if "restore" in request.POST:
        sale_restore = get_object_or_404(Sale, id=id)
        client_id = sale_restore.client.id

        sale_quantity = sale_restore.sale_quantity
        item = sale_restore.item
        Item.objects.filter(id=item.id).update(quantity=F('quantity') + sale_quantity)
        Restore.objects.create(
            client=sale_restore.client, 
            item=sale_restore.item, 
            date=sale_restore.date, 
            crash=sale_restore.crash,
            sale_price=sale_restore.sale_price, 
            remain=sale_restore.remain, 
            paid=sale_restore.paid, 
            sale_quantity=sale_restore.sale_quantity,
            client_phone=sale_restore.client_phone, 
            method=sale_restore.method
        )

        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='مرتجع',
            action_sort='إضافة',
            model_affected=f'تم إضافة مرتجع للعميل {sale_restore.client.name} و قيمة المرتجع {sale_restore.total} جنيها',
        )
        sale_restore.delete()
        messages.success(request, "تم تسجيل مرتجع بنجاح")
        return redirect("clientpage", id=client_id)

#====================================================================================================================
def sale_delete(request, id):
    sale_to_delete = get_object_or_404(Sale, id=id)

    if "saleDelete" in request.POST:
        sale_quantity = sale_to_delete.sale_quantity
        item = sale_to_delete.item
        Item.objects.filter(id=item.id).update(quantity=F('quantity') + sale_quantity)
        RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type='حذف عملية بيع',
        action_sort = 'حذف',
        model_affected=f'تم حذف عملية بيع من صنف {sale_to_delete.item} و بقيمة {sale_to_delete.total} جنيها',
    )
        sale_to_delete.delete()

        messages.success(request, "تم حذف العملية بنجاح")
        return redirect("profits")    
    
    if "saleDelete2" in request.POST:
        sale_quantity = sale_to_delete.sale_quantity
        item = sale_to_delete.item
        Item.objects.filter(id=item.id).update(quantity=F('quantity') + sale_quantity)
        RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type='حذف عملية بيع',
        action_sort = 'حذف',
        model_affected=f'تم حذف عملية بيع من صنف {sale_to_delete.item} و بقيمة {sale_to_delete.total} جنيها',
    )
        sale_to_delete.delete()

        messages.success(request, "تم حذف العملية بنجاح")
        return redirect("tempsales")    

    if "saleDelete3" in request.POST:
        sale_quantity = sale_to_delete.sale_quantity
        item = sale_to_delete.item
        Item.objects.filter(id=item.id).update(quantity=F('quantity') + sale_quantity)
        RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type='حذف عملية بيع',
        action_sort = 'حذف',
        model_affected=f'تم حذف عملية بيع من صنف {sale_to_delete.item} و بقيمة {sale_to_delete.total} جنيها',
    )
        sale_to_delete.delete()
        client_id = sale_to_delete.client.id

        messages.success(request, "تم حذف العملية بنجاح")
        return redirect("clientpage" , id=client_id)    
#====================================================================================================================
def paid_done(request, id):
    sale_to_done = get_object_or_404(Sale, id=id)

    if "paidDone" in request.POST:
        total = sale_to_done.total
        sale_to_done.paid = total
        sale_to_done.remain = 0
        sale_to_done.save()
        RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type='تسجيل دفع مديونية',
        action_sort = 'إضافة',
        model_affected=f'تم تسجيل دفع مديونية باسم العميل {sale_to_done.client_name}{sale_to_done.client.name} بقيمة {sale_to_done.total - sale_to_done.paid} لتصفية حساب عملية بيع',
    )
        messages.success(request, "تم تأكيد الدفع بنجاح")
        return redirect("tempsales")   
#====================================================================================================================
@login_required(login_url="login")
def clients(request):
    client = Client.objects.all()
    paginator = Paginator(client ,20)
    page = request.GET.get('page')
    try:
        client_list = paginator.page(page)
    except PageNotAnInteger:
        client_list = paginator.page(1)
    except EmptyPage :
        client_list = paginator.page(paginator.num_pages)

    if "addClient" in request.POST:
        name = request.POST.get("name")
        opening_balance = request.POST.get("opening_balance")
        phone = request.POST.get("phone")

        if Client.objects.filter(name=name).exists():
            messages.warning(request, f'اسم العميل ({name}) موجود بالفعل في قاعدة البيانات')
            return redirect("clients")
        
        if not opening_balance :
            opening_balance = 0

        Client.objects.create(name=name, opening_balance =opening_balance, phone=phone)
        RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type='إضاقة عميل',
        action_sort = 'إضافة',
        model_affected=f'تم إضافة عميل باسم {name} و برصيد افتتاحي {opening_balance} جنيها',
    )
        messages.success(request, "تم اضافة عميل جديد بنجاح")
        return redirect("clients")


    if 'search' in request.POST :
        search_input = request.POST.get('searchInput')
        results = [result['id'] for result in Client.objects.all().filter(Q(name__icontains=search_input)).values()]
        client_list = [Client.objects.get(pk = id) for id in results]


    context = {"clients" : client_list}
    return render(request,"clients.html", context)
#====================================================================================================================
def client_update(request, id):
    old_client_data = None

    if 'clientUpdate' in request.POST:
        name = request.POST['name']
        opening_balance = request.POST['opening_balance']
        phone = request.POST['phone']

        name = name.strip()
        old_client_data = Client.objects.filter(id=id).values().first()

        if Client.objects.filter(name=name).exclude(id=id).exists():
            messages.warning(request, f'اسم العميل ({name}) موجود بالفعل في قاعدة البيانات')
            return redirect("clientpage", id=id)
        
        edit = Client.objects.get(id=id)

        old_name = old_client_data['name']
        old_opening_balance = old_client_data['opening_balance']
        old_phone = old_client_data['phone']

        changes = []
        if name != old_name:
            changes.append(f'اسم العميل من {old_name} إلى {name}')
        if str(opening_balance) != str(old_opening_balance):
            changes.append(f'الرصيد الافتتاحي من {old_opening_balance} إلى {opening_balance}')
        if phone != old_phone:
            changes.append(f'الهاتف من {old_phone} إلى {phone}')

        edit.name = name
        edit.opening_balance = opening_balance
        edit.phone = phone
        edit.save()

        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='تعديل عميل',
            action_sort='تعديل',
            model_affected=f'تم تعديل بيانات العميل: {", ".join(changes)}',
        )

        messages.success(request, 'تم تعديل بيانات العميل بنجاح', extra_tags='success')
        return redirect("clients")
    
    else:
        try:
            old_client_data = Client.objects.filter(id=id).values().first()
            client = Client.objects.get(id=id)
        except Client.DoesNotExist:
            messages.error(request, 'حدث خطأ، العميل غير موجود', extra_tags='error')
            return redirect("clients")

    context = {"client": client, "id": id, "old_client_data": old_client_data}
    return render(request, 'clientupdate.html', context)
#====================================================================================================================
def client_delete(request, id):
    client_to_delete = get_object_or_404(Client, id =id )

    if "clientDelete" in request.POST :
        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='حذف عميل',
            action_sort = 'حذف',
            model_affected=f'تم حذف العميل ({client_to_delete.name})',
        )
        client_to_delete.delete()
        messages.success(request, "تم حذف العميل بنجاح")
        return redirect("clients")
#====================================================================================================================
@login_required(login_url="login")
def client_page(request, id):
    items = Item.objects.all()
    client = get_object_or_404(Client, id=id)
    sales = Sale.objects.filter(client=client).order_by("-date")
    sales_by_date = Sale.objects.filter(client=client).values('date').annotate(
    total_meal=Sum('sale_price')
    )
    restores = Restore.objects.filter(client=client).order_by("-date")
    if "sell2" in request.POST :
        item_id = request.POST.get('id')
        sale_date = request.POST.get('date')  
        client = client
        paid = request.POST.get('paid')
        remain = request.POST.get('remain')
        method = request.POST.get('method')
        sale_price = request.POST.get('sale_price')
        sale_quantity = request.POST.get('sale_quantity')

        sale_price = Decimal(sale_price)
        sale_quantity = Decimal(sale_quantity)
        paid = Decimal(paid)

        try:
            item = Item.objects.get(id =item_id ) 
            if sale_quantity > item.quantity:
                messages.error(request, "الكمية المباعة اكبر من الكمية المتبقية")
                return redirect("clientpage", id=id)
            
            Sale.objects.create(client=client, item=item, date=sale_date,sale_price=sale_price, remain=remain, paid=paid, sale_quantity=sale_quantity, method=method)
            Item.objects.filter(id=item_id).update(quantity=F('quantity') - sale_quantity)
            RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='إضافة عملية بيع',
            action_sort = 'إضافة',
            model_affected=f'تم بيع كمية {sale_quantity} من صنف {item.name} باجمالي تكلفة {sale_quantity*sale_price} جنيها',
        )
            messages.success(request, "تمت إضافة عملية بيع بنجاح")
            return redirect("clientpage", id=id)
        except :
            messages.error(request,"المنتج غير موجود")

    if 'addPayment' in request.POST:
        client = client
        paid = request.POST.get('paid')
        method = request.POST.get('method')
        date = request.POST.get('date')
        Payment.objects.create(client=client, paid_money=paid, date=date, method=method)
        RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type='إضاقة دفع',
        action_sort = 'إضافة',
        model_affected=f'تم إضافة دفع باسم العميل {client.name} بقيمة {paid} جنيها',
        )

        messages.success(request, "تمت اضافة عملية دفع بنجاح")
        return redirect("clientpage", id=id)            

    payments = Payment.objects.filter(client=client).order_by('-date')
    context = {"client": client, "sales": sales, "items":items,'sales_by_date': sales_by_date, 'payments':payments, 'restores':restores}
    return render(request, "clientpage.html", context)
#====================================================================================================================
@login_required(login_url="login")
def profits(request):
    sales = Sale.objects.all().order_by("-date")
    paginator = Paginator(sales ,20)
    page = request.GET.get('page')
    try:
        sale_list = paginator.page(page)
    except PageNotAnInteger:
        sale_list = paginator.page(1)
    except EmptyPage :
        sale_list = paginator.page(paginator.num_pages)

    if 'search' in request.POST :
        search_input = request.POST.get('searchInput')
        results = [result['id'] for result in Sale.objects.all().filter(Q(client_name__icontains=search_input)).values()]
        sale_list = [Sale.objects.get(pk = id) for id in results]

        
    context ={
        "sales" : sale_list,
    }
    return render(request,"profits.html", context)
#====================================================================================================================
def pay_update(request, id):
    payment = get_object_or_404(Payment, id=id)
    client_id = payment.client.id

    if "payupdate" in request.POST:
        paid_money = request.POST["paid_money"]
        method = request.POST["method"]
        paid_money = Decimal(paid_money)

        old_payment_data = Payment.objects.filter(id=id).values().first()

        edit = Payment.objects.get(id=id)

        old_paid_money = old_payment_data['paid_money']
        old_method = old_payment_data['method']

        changes = []
        if str(paid_money) != str(old_paid_money):
            changes.append(f'المبلغ المدفوع من {old_paid_money} إلى {paid_money}')
        if method != old_method:
            changes.append(f'طريقة الدفع من {old_method} إلى {method}')

        edit.paid_money = paid_money
        edit.method = method
        edit.save()

        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='تعديل دفع',
            action_sort='تعديل',
            model_affected=f'تم تعديل بيانات الدفع: {", ".join(changes)}',
        )

        messages.success(request, 'تم تعديل بيانات الدفع بنجاح', extra_tags='success')
        return redirect("clientpage", id=client_id)
#====================================================================================================================
def pay_delete(request, id):
    pay_to_delete = get_object_or_404(Payment, id =id )
    client_id = pay_to_delete.client.id

    if "paydelete" in request.POST :
        RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type='حذف عملية دفع',
        action_sort = 'حذف',
        model_affected=f'تم حذف عملية دفع للعميل {pay_to_delete.client.name} بقيمة {pay_to_delete.paid_money} جنيها',
    )
        pay_to_delete.delete()
        messages.success(request, "تم حذف العملية بنجاح")
        return redirect("clientpage", id=client_id)
#====================================================================================================================
def loses(request):
    loses = Lose.objects.all().order_by("-date")
    paginator = Paginator(loses ,20)
    page = request.GET.get('page')
    try:
        loses_list = paginator.page(page)
    except PageNotAnInteger:
        loses_list = paginator.page(1)
    except EmptyPage :
        loses_list = paginator.page(paginator.num_pages)

    if "addLose" in request.POST :
        lose_type = request.POST.get('lose_type')
        lose_money = request.POST.get('lose_money')
        lose_date = request.POST.get('date')
        notes = request.POST.get('notes')

        if not notes :
            notes = "-"

        elif not lose_date :
            lose_date = date.today()
        
        Lose.objects.create(lose_type=lose_type,lose_money=lose_money, date=lose_date, notes=notes)
        RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type='إضافة مصروف',
        action_sort = 'إضافة',
        model_affected=f'تم إضافة مصروف {lose_type} بقيمة {lose_money} جنيها',
    )
        messages.success(request,"تم اضافة مصروف بنجاح")
        return redirect("loses")
    
    context ={
        'loses' : loses_list

    }

    return render(request,'loses.html', context)
#====================================================================================================================
def lose_delete(request, id):
    lose_to_delete = get_object_or_404(Lose, id =id )

    if "loseDelete" in request.POST :
        RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type='حذف مصروف',
        action_sort = 'حذف',
        model_affected=f'تم حذف مصروف بقيمة {lose_to_delete.lose_money} جنيها',
    )
        lose_to_delete.delete()
        messages.success(request, "تم حذف المصروف بنجاح")
        return redirect("loses")
#====================================================================================================================
def lose_update(request, id):
    if 'loseUpdate' in request.POST:
        lose_type = request.POST['lose_type']
        lose_money = request.POST['lose_money']
        notes = request.POST['notes']

        old_lose_data = Lose.objects.filter(id=id).values().first()

        edit = Lose.objects.get(id=id)

        old_lose_type = old_lose_data['lose_type']
        old_lose_money = old_lose_data['lose_money']
        old_notes = old_lose_data['notes']

        changes = []
        if lose_type != old_lose_type:
            changes.append(f'نوع المصروف من {old_lose_type} إلى {lose_type}')
        if str(lose_money) != str(old_lose_money):
            changes.append(f'المبلغ من {old_lose_money} إلى {lose_money}')
        if notes != old_notes:
            changes.append(f'الملاحظات من {old_notes} إلى {notes}')

        edit.lose_type = lose_type
        edit.lose_money = lose_money
        edit.notes = notes
        edit.save()

        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='تعديل مصروف',
            action_sort='مصروف',
            model_affected=f'تم تعديل بيانات المصروف: {", ".join(changes)}',
        )

        messages.success(request, 'تم تعديل بيانات المصروف بنجاح', extra_tags='success')
        return redirect("loses")
#====================================================================================================================
def shorts(request):
    all_items = Item.objects.all().order_by("-date")
    shorts = [item for item in all_items if item.quantity == 0 ]
    paginator = Paginator(shorts, 30)

    page = request.GET.get('page')
    try:
        shorts_list = paginator.page(page)
    except PageNotAnInteger:
        shorts_list = paginator.page(1)
    except EmptyPage :
        shorts_list = paginator.page(paginator.num_pages)


    if 'search' in request.POST :
        search_input = request.POST.get('searchInput')
        results = [result['id'] for result in Item.objects.all().filter(Q(name__icontains=search_input)).values()]
        shorts_list = [Item.objects.get(pk = id) for id in results]

    context = {
        'items': shorts_list,
    }

    return render(request, 'shorts.html', context)
#====================================================================================================================
def tempsales(request):
    all_sales = Sale.objects.all().order_by("-date")
    tempsales = [sale for sale in all_sales if sale.remain > 0 ]
    paginator = Paginator(tempsales, 30)

    page = request.GET.get('page')
    try:
        temp_list = paginator.page(page)
    except PageNotAnInteger:
        temp_list = paginator.page(1)
    except EmptyPage :
        temp_list = paginator.page(paginator.num_pages)


    if 'search' in request.POST :
        search_input = request.POST.get('searchInput')
        results = [result['id'] for result in Sale.objects.all().filter(Q(client_name__icontains=search_input)).values()]
        temp_list = [Sale.objects.get(pk = id) for id in results]

    context = {
        'sales': temp_list,
    }

    return render(request, 'tempsales.html', context)
#====================================================================================================================
def daycome(request):
    all_daycoms = Daycome.objects.all().order_by("-date")
    paginator = Paginator(all_daycoms, 30)
    page = request.GET.get('page')
    try:
        comes_list = paginator.page(page)
    except PageNotAnInteger:
        comes_list = paginator.page(1)
    except EmptyPage:
        comes_list = paginator.page(paginator.num_pages)

    if 'search' in request.POST:
        search_input = request.POST.get('searchInput')
        results = [result['id'] for result in Daycome.objects.all().filter(Q(date__icontains=search_input)).values()]
        comes_list = [Daycome.objects.get(pk=id) for id in results]


    if "show" in request.POST:
        selected_date = request.POST.get('dateInput')
        safe = get_object_or_404(Safe, id=1)
        all_daycoms = Daycome.objects.all().order_by("-date")
        paginator = Paginator(all_daycoms, 30)
        page = request.GET.get('page')
        try:
            comes_list = paginator.page(page)
        except PageNotAnInteger:
            comes_list = paginator.page(1)
        except EmptyPage:
            comes_list = paginator.page(paginator.num_pages)


        today_profits = Sale.objects.filter(date=selected_date)
        total_profits = today_profits.aggregate(Sum('paid'))['paid__sum'] or 0

        today_payments = Payment.objects.filter(date=selected_date)
        total_payments = today_payments.aggregate(Sum('paid_money'))['paid_money__sum'] or 0

        today_loses = Lose.objects.filter(date=selected_date)
        total_loses = today_loses.aggregate(Sum('lose_money'))['lose_money__sum'] or 0

        today_supplier_pay = SupplierPay.objects.filter(date=selected_date)
        total_supplier_pay = today_supplier_pay.aggregate(Sum('paid'))['paid__sum'] or 0

        net_profit =( total_profits + total_payments) - (total_loses + total_supplier_pay)

        today_sales_with_win = Sale.objects.filter(date=selected_date).annotate(win=ExpressionWrapper((F('sale_price')*F('sale_quantity')) - (F('item__price')*F('sale_quantity')), output_field=DecimalField())).values('win')
        total_win = today_sales_with_win.aggregate(Sum('win'))['win__sum'] or 0


        
        return render(request, 'daycome.html', {
        'total_profits': total_profits,
        'total_loses': total_loses,
        'net_profit': net_profit,
        'total_win': total_win,
        'selected_date': selected_date,
        'daycomes': comes_list,
        'today_profits': today_profits,
        'today_loses': today_loses,
        'safe': safe,
        'total_supplier_pay': total_supplier_pay,
        'selected_date': selected_date,
        'payments': total_payments,
        })
    
    if "dayCome" in request.POST:
        total_profits = request.POST.get('total_profits')
        date = request.POST.get('date')
        total_loses = request.POST.get('total_loses')
        net_profit = request.POST.get('net_profit')
        win = request.POST.get('win')
        cash = request.POST.get('cash')
        wallet = request.POST.get('wallet')
        total_supplier_pay = request.POST.get('total_supplier_pay')
        payments = request.POST.get('payments')

        if Daycome.objects.filter(date=date).exists():
            messages.warning(request, f'تقفيل هذا اليوم محفوظ بالفعل في قاعدة البيانات')
            return redirect('daycome')

        Daycome.objects.create(loses=total_loses,payments=payments ,  income=total_profits, date=date, net_profit=net_profit, win = win , cash=cash, wallet=wallet, total_supplier_pay=total_supplier_pay)
        messages.success(request, "تم حفظ تقفيل اليوم")
        return redirect("daycome")

    context= { "daycomes" :comes_list}
    return render(request, 'daycome.html', context)
#====================================================================================================================
def daycome_delete(request, id):
    daycome_to_delete = get_object_or_404(Daycome, id =id )

    if "daycomeDelete" in request.POST :
        RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type='حذف تقفيل ',
        action_sort = 'حذف',
        model_affected=f'تم حذف تقفيل يوم {daycome_to_delete.date}',
    )
        daycome_to_delete.delete()
        messages.success(request, "تم حذف التقفيل بنجاح")
        return redirect("daycome")
#====================================================================================================================
def daycome_update(request, id):
    if 'daycomeUpdate' in request.POST:
        total_profits = request.POST['total_profits']
        total_loses = request.POST['total_loses']
        net_profit = request.POST['net_profit']
        win = request.POST['win']
        cash = request.POST['cash']
        wallet = request.POST['wallet']
        date = request.POST['date']

        old_daycome_data = Daycome.objects.filter(id=id).values().first()

        edit = Daycome.objects.get(id=id)

        old_total_profits = old_daycome_data['income']
        old_total_loses = old_daycome_data['loses']
        old_net_profit = old_daycome_data['net_profit']
        old_win = old_daycome_data['win']
        old_cash = old_daycome_data['cash']
        old_wallet = old_daycome_data['wallet']
        old_date = old_daycome_data['date']

        changes = []
        if total_profits != old_total_profits:
            changes.append(f'الأرباح الإجمالية من {old_total_profits} إلى {total_profits}')
        if total_loses != old_total_loses:
            changes.append(f'الخسائر الإجمالية من {old_total_loses} إلى {total_loses}')
        if net_profit != old_net_profit:
            changes.append(f'صافي الربح من {old_net_profit} إلى {net_profit}')
        if win != old_win:
            changes.append(f'الأرباح من {old_win} إلى {win}')
        if cash != old_cash:
            changes.append(f'النقد من {old_cash} إلى {cash}')
        if wallet != old_wallet:
            changes.append(f'المحفظة من {old_wallet} إلى {wallet}')
        if date != old_date:
            changes.append(f'التاريخ من {old_date} إلى {date}')

        edit.income = total_profits
        edit.loses = total_loses
        edit.net_profit = net_profit
        edit.win = win
        edit.cash = cash
        edit.wallet = wallet
        edit.date = date
        edit.save()

        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='تعديل تقفيل',
            action_sort='تعديل',
            model_affected=f'تم تعديل بيانات التقفيل: {", ".join(changes)}',
        )

        messages.success(request, 'تم تعديل بيانات التقفيل بنجاح', extra_tags='success')
        return redirect("daycome")
#====================================================================================================================
def safe(request):
    safe_instance = get_object_or_404(Safe, id=1)
    cash_month_sales = Sale.objects.filter(date__date=timezone.now().date(), method="نقدية").aggregate(Sum('paid'))['paid__sum'] or 0
    wallet_month_sales = Sale.objects.filter(date__date=timezone.now().date(), method="محفظة").aggregate(Sum('paid'))['paid__sum'] or 0
    cash_month_payment = Payment.objects.filter(date__date=timezone.now().date(), method="نقدية").aggregate(Sum('paid_money'))['paid_money__sum'] or 0
    wallet_month_payment = Payment.objects.filter(date__date=timezone.now().date(), method="محفظة").aggregate(Sum('paid_money'))['paid_money__sum'] or 0
    cash_month = cash_month_sales + cash_month_payment
    wallet_month = wallet_month_sales + wallet_month_payment

    if request.method == 'POST':
        if 'deposit' in request.POST:
            amount = request.POST.get('amount')
            kind = request.POST.get('kind')
            amount = Decimal(amount)

            if kind == 'درج':
                safe_instance.cash += amount
                action_description = f'تم إيداع مبلغ {amount} جنيها في الدرج'
            elif kind == 'محفظة':
                safe_instance.wallet += amount
                action_description = f'تم إيداع مبلغ {amount} جنيها في المحفظة'

            safe_instance.save()

            RecentAction.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action_type='إيداع',
                action_sort='إيداع',
                model_affected=action_description,
            )

            messages.success(request, "تم الإيداع بنجاح")
            return redirect('safe')

        if 'cashToWallet' in request.POST:
            ctw = Decimal(request.POST.get('ctw'))
            if safe_instance.cash >= ctw:
                safe_instance.cash -= ctw
                safe_instance.wallet += ctw
                safe_instance.save()
                
                RecentAction.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    action_type='تحويل',
                    action_sort='تحويل',
                    model_affected=f'تم تحويل مبلغ {ctw} جنيها من الدرج إلى المحفظة',
                )

                messages.success(request, "تم الترحيل بنجاح")
            else:
                messages.error(request, "الرصيد الحالي غير كافي لهذه العملية")
            return redirect('safe')

        if 'walletToCash' in request.POST:
            wtc = Decimal(request.POST.get('wtc'))
            if safe_instance.wallet >= wtc:
                safe_instance.wallet -= wtc
                safe_instance.cash += wtc
                safe_instance.save()
                
                RecentAction.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    action_type='تحويل',
                    action_sort='تحويل',
                    model_affected=f'تم تحويل مبلغ {wtc} جنيها من المحفظة إلى الدرج',
                )

                messages.success(request, "تم الترحيل بنجاح")
            else:
                messages.error(request, "الرصيد الحالي غير كافي لهذه العملية")
            return redirect('safe')

    context = {"safe": safe_instance, "cash_month": cash_month, "wallet_month": wallet_month}

    return render(request, "safe.html", context)
#====================================================================================================================
def safe_update(request, id):

    if 'cashUpdate' in request.POST:
        cash = request.POST['cash']
        edit = Safe.objects.get(id=id)
        
        old_cash = edit.cash
        
        edit.cash = cash
        edit.save()

        changes = []
        if cash != old_cash:
            changes.append(f'الرصيد النقدي من {old_cash} إلى {cash}')

        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='تعديل رصيد الدرج',
            action_sort='تعديل',
            model_affected=f'تم تعديل رصيد الدرج: {", ".join(changes)}',
        )

        messages.success(request, 'تم تعديل رصيد الدرج', extra_tags='success')
        return redirect("safe")

    if 'walletUpdate' in request.POST:
        wallet = request.POST['wallet']
        edit = Safe.objects.get(id=id)
        
        old_wallet = edit.wallet
        
        edit.wallet = wallet
        edit.save()

        changes = []
        if wallet != old_wallet:
            changes.append(f'رصيد المحفظة من {old_wallet} إلى {wallet}')

        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='تعديل رصيد المحفظة',
            action_sort='تعديل',
            model_affected=f'تم تعديل رصيد المحفظة: {", ".join(changes)}',
        )

        messages.success(request, 'تم تعديل رصيد المحفظة', extra_tags='success')
        return redirect("safe")
#====================================================================================================================
@login_required(login_url="login")
def suppliers(request):
    suppliers = Supplier.objects.all()
    paginator = Paginator(suppliers ,30)
    page = request.GET.get('page')
    try:
        supplier_list = paginator.page(page)
    except PageNotAnInteger:
        supplier_list = paginator.page(1)
    except EmptyPage :
        supplier_list = paginator.page(paginator.num_pages)

    if "addSupplier" in request.POST :
        name = request.POST.get('name')
        for_him = request.POST.get('for_him')
        phone = request.POST.get('phone')
        if Supplier.objects.filter(name=name).exists():
            messages.warning(request, f'اسم ألمورد ({name}) موجود بالفعل في قاعدة البيانات')
            return redirect("suppliers")

        Supplier.objects.create(name=name, for_him=for_him, phone=phone)
        RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type='إضافة مورد',
        action_sort = 'إضافة',
        model_affected=f'تم إضافة مورد باسم {name} و برصيد افتتاحي قدره {for_him} جنيها',
    )
        messages.success(request,"تم اضافة مورد بنجاح")
        return redirect("suppliers")
    
    if 'search' in request.POST :
        search_input = request.POST.get('searchInput')
        results = [result['id'] for result in Supplier.objects.all().filter(Q(name__icontains=search_input)).values()]
        supplier_list = [Supplier.objects.get(pk = id) for id in results]
    
    if 'supplierPaid' in request.POST:
        name = request.POST.get('name')
        paid = request.POST.get('paid')
        supplier = Supplier.objects.get(name= name)
        SupplierPay.objects.create(supplier=supplier, date=date.today(), paid=paid)
        Supplier.objects.filter(name=name).update(for_him=F('for_him') - paid)
        RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type='إضافة دفع لمورد',
        action_sort = 'إضافة',
        model_affected=f'تم دفع مبلغ {paid} جنيها للمورد {name}',
    )
        messages.success(request, "تم التسديد بنجاح")
        return redirect("suppliers")

    context ={'suppliers': supplier_list}

    return render(request,"suppliers.html", context)
#====================================================================================================================
def supplier_update(request, id):
    old_supplier_data = None

    if 'supplierUpdate' in request.POST:
        name = request.POST['name']
        for_him = request.POST['for_him']
        phone = request.POST['phone']

        name = name.strip()

        try:
            if Supplier.objects.filter(name=name).exclude(id=id).exists():
                messages.warning(request, f'اسم المورد ({name}) موجود بالفعل في قاعدة البيانات')
                return redirect("suppliers")

            old_supplier_data = Supplier.objects.filter(id=id).values().first()
            edit = Supplier.objects.get(id=id)

            old_name = old_supplier_data['name']
            old_for_him = old_supplier_data['for_him']
            old_phone = old_supplier_data['phone']

            changes = []
            if name != old_name:
                changes.append(f'اسم المورد من {old_name} إلى {name}')
            if for_him != old_for_him:
                changes.append(f'له من {old_for_him} إلى {for_him}')
            if phone != old_phone:
                changes.append(f'رقم الهاتف من {old_phone} إلى {phone}')

            edit.name = name
            edit.for_him = for_him
            edit.phone = phone
            edit.save()

            RecentAction.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action_type='تعديل مورد',
                action_sort='تعديل',
                model_affected=f'تم تعديل بيانات المورد: {", ".join(changes)}',
            )

            messages.success(request, 'تم تعديل بيانات المورد بنجاح', extra_tags='success')
            return redirect("suppliers")
        except Supplier.DoesNotExist:
            messages.error(request, 'حدث خطأ، المورد غير موجود', extra_tags='error')
            return redirect("suppliers")

    else:
        try:
            old_supplier_data = Supplier.objects.filter(id=id).values().first()
            supplier = Supplier.objects.get(id=id)
        except Supplier.DoesNotExist:
            messages.error(request, 'حدث خطأ، المورد غير موجود', extra_tags='error')
            return redirect("suppliers")

    context = {"supplier": supplier, "id": id, "old_supplier_data": old_supplier_data}
    return render(request, 'supplierupdate.html', context)
#====================================================================================================================
def supplier_delete(request, id):
    supplier_to_delete = get_object_or_404(Supplier, id =id )

    if "supplierDelete" in request.POST :
        RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type='حذف مورد',
        action_sort = 'حذف',
        model_affected=f'تم حذف المورد {supplier_to_delete.name}',
    )
        supplier_to_delete.delete()
        messages.success(request, "تم حذف العميل بنجاح")
        return redirect("suppliers")
#====================================================================================================================
def supplier_page(request, id):
    supplier = get_object_or_404(Supplier, id =id)
    payments = SupplierPay.objects.filter(supplier=supplier).order_by("-date")
    paginator = Paginator(payments, 30)
    page = request.GET.get('page')
    try:
        payment_list = paginator.page(page)
    except PageNotAnInteger:
        payment_list = paginator.page(1)
    except EmptyPage:
        payment_list = paginator.page(paginator.num_pages)

    context = {"payments" : payment_list , "supplier": supplier}
    return render(request,'supplierpage.html', context)
#====================================================================================================================
def supplier_pay_delete(request, id):
    supplier_pay_to_delete = get_object_or_404(SupplierPay, id =id )
    supplier_id = supplier_pay_to_delete.supplier.id
    supplier = supplier_pay_to_delete.supplier
    paid = supplier_pay_to_delete.paid
    if "supplierPayDelete" in request.POST :
        RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type='حذف سداد لمورد',
        action_sort = 'حذف',
        model_affected=f'تم حذف سداد للمورد {supplier_pay_to_delete.supplier.name} بقيمة {supplier_pay_to_delete.paid} حنيها',
    )
        supplier_pay_to_delete.delete()
        Supplier.objects.filter(id = supplier_id).update(for_him=F('for_him') + paid)
        messages.success(request, "تم حذف العملية بنجاح")
        return redirect("supplierpage" , id =supplier_id)
#====================================================================================================================
def restore_delete(request, id):
    if 'restoreDelete' in request.POST :
        restore_to_delete = get_object_or_404(Restore, id =id )
        client_id = restore_to_delete.client.id
        RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type='حذف مرتجع',
        action_sort = 'حذف',
        model_affected=f'تم حذف المرتجع بقيمة {restore_to_delete.total}',
    )
        restore_to_delete.delete()
        messages.success(request, "تم حذف عملية البيع المرتجعة بنجاح")
        return redirect("clientpage", id=client_id)

#====================================================================================================================
def admin_page(request):
    recent_actions = RecentAction.objects.all().order_by("-timestamp")
    recent_dates = Sale.objects.annotate(day_of_week=ExtractWeekDay('date')).values('day_of_week').annotate(max_date=Max('date')).values('day_of_week', 'max_date')
    
    sales_data = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
    
    # Determine the current date and the last day of the current month
    today = timezone.now().date()
    last_day_of_month = monthrange(today.year, today.month)[1]
    end_of_month = timezone.datetime(today.year, today.month, last_day_of_month).date()
    
    # Calculate losses for the current month
    loses = Lose.objects.filter(lose_type="مصروف", date__month=today.month, date__year=today.year).aggregate(Sum('lose_money'))['lose_money__sum'] or 0
    waste = Lose.objects.filter(lose_type="هادر", date__month=today.month, date__year=today.year).aggregate(Sum('lose_money'))['lose_money__sum'] or 0
    rent = Lose.objects.filter(lose_type="ايجار", date__month=today.month, date__year=today.year).aggregate(Sum('lose_money'))['lose_money__sum'] or 0
    depts = Lose.objects.filter(lose_type="ديون", date__month=today.month, date__year=today.year).aggregate(Sum('lose_money'))['lose_money__sum'] or 0
    other = Lose.objects.filter(lose_type="اخرى", date__month=today.month, date__year=today.year).aggregate(Sum('lose_money'))['lose_money__sum'] or 0
    
    for entry in recent_dates:
        day_of_week = entry['day_of_week']
        max_date = entry['max_date']
        total_sales = Sale.objects.filter(date=max_date).aggregate(Sum('total'))['total__sum'] or 0
        sales_data[day_of_week] = total_sales

    context = {
        'sales_data': sales_data,
        'recent_actions': recent_actions,
        'loses': loses,
        'waste': waste,
        'rent': rent,
        'depts': depts,
        'other': other,
        'end_of_month': end_of_month,
    }
    
    return render(request, 'admin.html', context)
#====================================================================================================================
def employees(request):
    employees = Employee.objects.all().order_by("-date")
    loans = Loan.objects.all()
    if "addEmployee" in request.POST:
        name = request.POST.get('name')
        job = request.POST.get('job')
        salary = request.POST.get('salary')

        if Employee.objects.filter(name=name).exists():
            messages.error(request, f'اسم الموظف ({name}) موجود بالفعل في قاعدة البيانات')
            return redirect('employees')
        
        else:
            Employee.objects.create(name=name, job=job, salary=salary)
            messages.success(request,"تم إضافة موظف جديد")
            return redirect('employees')
        
    elif "addLoan" in request.POST:
        employee_id = request.POST.get('employee')
        amount = request.POST.get('amount')
        date_str = request.POST.get('date')
        
        if not date_str:
            egypt_tz = pytz.timezone('Africa/Cairo')
            date = timezone.now().astimezone(egypt_tz).date()
        else:
            try:
                date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                messages.warning(request, 'تاريخ غير صالح. يجب أن يكون الشكل YYYY-MM-DD', extra_tags='warning')
                return redirect('employees')

        employee = Employee.objects.get(pk=int(employee_id))

        Loan.objects.create(employee=employee, amount=amount, date=date)
        messages.success(request,"تم اضافة سلفة")
        return redirect('employees')
    
    elif "deleteAllLoans" in request.POST:
        loans.delete()
        messages.success(request, "تم حذف جميع السلف")
        return redirect('employees')
        
    context={
        'employees':employees,
        'loans' :loans, 
        }

    return render(request,'employees.html', context)
#====================================================================================================================
def employee_page(request,id):
    employee = get_object_or_404(Employee, id =id)
    loans = Loan.objects.filter(employee=employee).order_by("-date")
    deductions = Deduction.objects.filter(employee=employee).order_by("-date")
    prizes = Prize.objects.filter(employee=employee).order_by("-date")

    if "addLoan" in request.POST :
        amount = request.POST.get("amount")
        Loan.objects.create(employee=employee, amount=amount)
        messages.success(request, "تم اضافة سلفة")
        return redirect('employeePage' , id=id)
        
    if "addDeduction" in request.POST :
        amount = request.POST.get("amount")
        Deduction.objects.create(employee=employee, amount=amount)
        messages.success(request, "تم اضافة خصم")
        return redirect('employeePage' , id=id)
        
    if "addPrize" in request.POST :
        amount = request.POST.get("amount")
        Prize.objects.create(employee=employee, amount=amount)
        messages.success(request, "تم اضافة مكافأة")
        return redirect('employeePage' , id=id)
        
    if "settlement" in request.POST :
        Loan.objects.filter(employee=employee).delete()
        Deduction.objects.filter(employee=employee).delete()
        Prize.objects.filter(employee=employee).delete()
        messages.success(request, "تم تصفية حسابات الموظف")
        return redirect('employeePage' , id=id)

    context = {
        "employee":employee,
        "loans":loans,
        "deductions":deductions,
        "prizes":prizes,
    }
    return render(request, "employeepage.html", context)

