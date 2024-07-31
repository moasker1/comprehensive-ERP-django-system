from django.urls import path
from . import views

urlpatterns = [
    path('',views.login_user, name='login' ),
    path('logout',views.logout_user, name='logout' ),
    path('sales',views.sale_page, name='sales' ),
    path('home',views.home, name='home' ),
    path('kinds',views.kinds, name='kinds' ),
    path('items',views.items, name='items' ),
    path('clients',views.clients, name='clients' ),
    path('suppliers',views.suppliers, name='suppliers' ),
    path('clientpage/<int:id>',views.client_page, name='clientpage' ),
    path('safe',views.safe, name='safe' ),
    path('loses',views.loses, name='loses' ),
    path('shorts',views.shorts, name='shorts' ),
    path('tempsales',views.tempsales, name='tempsales' ),
    path('daycome',views.daycome, name='daycome' ),
    path('admin',views.admin_page, name='admin' ),
    path('employees',views.employees, name='employees' ),
    path('employeePage/<int:id>',views.employee_page, name='employeePage' ),
    path('sell/<int:id>',views.sell, name='sell' ),
    path('sell3',views.sell3, name='sell3' ),
    path('loseDelete/<int:id>',views.lose_delete, name='loseDelete' ),
    path('daycomeDelete/<int:id>',views.daycome_delete, name='daycomeDelete' ),
    path('loseUpdate/<int:id>',views.lose_update, name='loseUpdate' ),
    path('daycomeUpdate/<int:id>',views.daycome_update, name='daycomeUpdate' ),
    path('kindDelete/<int:id>',views.kind_delete, name='kindDelete' ),
    path('itemDelete/<int:id>',views.item_delete, name='itemDelete' ),
    path('supplierDelete/<int:id>',views.supplier_delete, name='supplierDelete' ),
    path('paymentUpdate/<int:id>',views.pay_update, name='paymentUpdate' ),
    path('paydelete/<int:id>',views.pay_delete, name='paydelete' ),
    path('itemUpdate/<int:id>',views.item_update, name='itemUpdate' ),
    path('saleDelete/<int:id>',views.sale_delete, name='saleDelete' ),
    path('supplierUpdate/<int:id>',views.supplier_update, name='supplierUpdate' ),
    path('saleUpdate/<int:id>',views.sale_update, name='saleUpdate' ),
    path('safeUpdate/<int:id>',views.safe_update, name='safeUpdate' ),
    path('salepaid/<int:id>',views.paid_done, name='salepaid' ),
    path('clients',views.clients, name='clients' ),
    path('restoreDelete/<int:id>',views.restore_delete, name='restoreDelete' ),
    path('clientDelete/<int:id>',views.client_delete, name='clientDelete' ),
    path('clientUpdate/<int:id>',views.client_update, name='clientUpdate' ),
    path('clientpage/<int:id>',views.client_page, name='clientpage' ),
    path('supplierpage/<int:id>',views.supplier_page, name='supplierpage' ),
    path('profits',views.profits, name='profits' ),
    path('payupdate/<int:id>',views.pay_update, name='payupdate' ),
    path('supplierpaydelete/<int:id>',views.supplier_pay_delete, name='supplierpaydelete' ),
]