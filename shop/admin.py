from django.contrib import admin

from .models import Order, OrderItem, Product, ProductVariant, ShopSetting


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "available", "created_at")
    list_filter = ("category", "available")
    search_fields = ("name",)
    inlines = [ProductVariantInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "variant_size", "unit_price", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "created_at", "total")
    readonly_fields = ("order_number", "created_at", "total")
    inlines = [OrderItemInline]


@admin.register(ShopSetting)
class ShopSettingAdmin(admin.ModelAdmin):
    pass
