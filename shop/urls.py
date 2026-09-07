from django.urls import path

from . import views

urlpatterns = [
    path("", views.storefront, name="storefront"),

    path("cart/add/", views.cart_add, name="cart_add"),
    path("cart/change/", views.cart_change, name="cart_change"),
    path("cart/remove/", views.cart_remove, name="cart_remove"),
    path("cart/summary/", views.cart_summary, name="cart_summary"),

    path("checkout/", views.checkout, name="checkout"),
    path("checkout/confirm/", views.confirm_order, name="confirm_order"),
    path("order/<str:order_number>/success/", views.order_success, name="order_success"),

    path("owner/login/", views.OwnerLoginView.as_view(), name="owner_login"),
    path("owner/logout/", views.OwnerLogoutView.as_view(), name="owner_logout"),

    path("owner/products/", views.owner_products, name="owner_products"),
    path("owner/products/add/", views.owner_product_add, name="owner_product_add"),
    path("owner/products/<int:pk>/toggle/", views.owner_product_toggle_available, name="owner_product_toggle_available"),
    path("owner/products/<int:pk>/rename/", views.owner_product_rename, name="owner_product_rename"),
    path("owner/products/<int:pk>/delete/", views.owner_product_delete, name="owner_product_delete"),
    path("owner/variants/<int:pk>/update/", views.owner_variant_update, name="owner_variant_update"),
    path("owner/variants/<int:pk>/delete/", views.owner_variant_delete, name="owner_variant_delete"),
    path("owner/products/<int:product_id>/variants/add/", views.owner_variant_add, name="owner_variant_add"),

    path("owner/orders/", views.owner_orders, name="owner_orders"),
    path("owner/settings/", views.owner_settings, name="owner_settings"),
]
