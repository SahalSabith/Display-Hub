"""
URL configuration for displayHub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/addCategory',views.addCategory,name='addCategory'),
    path('admin/addBrand',views.addBrand,name='addBrand'),
    path('admin/addProduct',views.addProduct,name='addProduct'),
    path('admin/products',views.allProducts,name='allProducts'),
    path('admin/addVarient <vId>',views.addVarient,name='addVarient'),
    path('admin/allVarients/<int:vId>',views.allVerients,name='allVarients'),
    path('admin/allCategory',views.allCategory,name='allCategory'),
    path('admin/allBrand',views.allBrand,name='allBrand'),
    path('admin/blockBrand/<int:bId>/',views.blockBrand,name='blockBrand'),
    path('admin/blockProduct/<int:pId>/',views.blockProduct,name='blockProduct'),
    path('admin/blockCategory/<int:cId>/',views.blockCategory,name='blockCategory'),
    path('admin/allVarients/editVarient/<int:vId>',views.editVarient,name='editVarient'),
    path('admin/editProduct/<int:pId>',views.editProduct,name='editProduct'),
    path('admin/editCategory/<int:cId>',views.editCategory,name='editCategory'),
    path('admin/editBrand/<int:bId>',views.editBrand,name='editBrand'),
    path('admin/allOrders',views.listOrders,name='allOrders'),
    path('admin/orderDetails/<int:oId>/',views.orderDetail,name='adminOrderDeatils'),
    path('admin/newSize',views.addSize,name='createSize'),
    path('admin/newrefreshrate',views.addRefreshRate,name='createRefreshRate'),
    path('admin/announceProduct/',views.announceNewProduct,name="announceProduct")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)