from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import NewProductForm, OwnerPasswordChangeForm, ProductForm, ProductVariantFormSet, ShopSettingForm
from .models import Category, Order, OrderItem, Product, ProductVariant, ShopSetting


# ---------------------------------------------------------------------------
# Storefront
# ---------------------------------------------------------------------------
def storefront(request):
    category = request.GET.get("category", "All")
    products = Product.objects.filter(available=True).prefetch_related("variants")
    if category != "All":
        products = products.filter(category=category)
    categories = ["All"] + list(Category.values)
    return render(request, "shop/storefront.html", {
        "products": products,
        "categories": categories,
        "active_category": category,
    })


@require_POST
def cart_add(request):
    variant_id = request.POST.get("variant_id")
    variant = get_object_or_404(ProductVariant, id=variant_id)
    if not variant.product.available:
        return JsonResponse({"ok": False, "error": "This product is currently unavailable."}, status=400)
    cart = Cart(request)
    cart.add(variant_id, 1)
    return JsonResponse(_cart_payload(cart, changed_variant=variant.id))


@require_POST
def cart_change(request):
    variant_id = request.POST.get("variant_id")
    delta = int(request.POST.get("delta", 0))
    get_object_or_404(ProductVariant, id=variant_id)
    cart = Cart(request)
    cart.add(variant_id, delta)
    return JsonResponse(_cart_payload(cart, changed_variant=int(variant_id)))


@require_POST
def cart_remove(request):
    variant_id = request.POST.get("variant_id")
    cart = Cart(request)
    cart.remove(variant_id)
    return JsonResponse(_cart_payload(cart, changed_variant=int(variant_id)))


def cart_summary(request):
    cart = Cart(request)
    return JsonResponse(_cart_payload(cart))


def _cart_payload(cart, changed_variant=None):
    entries = cart.entries()
    return {
        "ok": True,
        "count": cart.count(),
        "total": str(cart.total()),
        "changed_variant": changed_variant,
        "items": [
            {
                "variant_id": e["variant"].id,
                "product_id": e["product"].id,
                "name": e["product"].name,
                "size": e["variant"].size,
                "qty": e["qty"],
                "unit_price": str(e["unit_price"]),
                "line_total": str(e["line_total"]),
                "image_url": e["product"].image.url if e["product"].image else "",
            }
            for e in entries
        ],
        "quantities": {str(e["variant"].id): e["qty"] for e in entries},
    }


# ---------------------------------------------------------------------------
# Checkout
# ---------------------------------------------------------------------------
def checkout(request):
    cart = Cart(request)
    entries = cart.entries()
    if not entries:
        messages.info(request, "Your cart is empty.")
        return redirect("storefront")
    settings_obj = ShopSetting.load()
    return render(request, "shop/checkout.html", {
        "entries": entries,
        "total": cart.total(),
        "settings": settings_obj,
    })


@require_POST
def confirm_order(request):
    cart = Cart(request)
    entries = cart.entries()
    if not entries:
        messages.info(request, "Your cart is empty.")
        return redirect("storefront")

    order = Order.objects.create(total=cart.total())
    for e in entries:
        OrderItem.objects.create(
            order=order,
            product_name=e["product"].name,
            variant_size=e["variant"].size,
            unit_price=e["unit_price"],
            quantity=e["qty"],
        )
    cart.clear()
    return redirect("order_success", order_number=order.order_number)


def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, "shop/order_success.html", {"order": order})


# ---------------------------------------------------------------------------
# Owner authentication
# ---------------------------------------------------------------------------
class OwnerLoginView(LoginView):
    template_name = "shop/owner_login.html"
    redirect_authenticated_user = True


class OwnerLogoutView(LogoutView):
    next_page = reverse_lazy("storefront")


# ---------------------------------------------------------------------------
# Owner: product management
# ---------------------------------------------------------------------------
@login_required
def owner_products(request):
    products = Product.objects.prefetch_related("variants").all()
    new_product_form = NewProductForm()
    return render(request, "shop/owner_products.html", {
        "products": products,
        "new_product_form": new_product_form,
    })


@login_required
@require_POST
def owner_product_add(request):
    form = NewProductForm(request.POST, request.FILES)
    if form.is_valid():
        product = form.save()
        ProductVariant.objects.create(
            product=product,
            size=form.cleaned_data["size"],
            price=form.cleaned_data["price"],
        )
        messages.success(request, f'"{product.name}" was added to the shop.')
    else:
        messages.error(request, "Could not add product: " + "; ".join(
            f"{f}: {', '.join(e)}" for f, e in form.errors.items()
        ))
    return redirect("owner_products")


@login_required
@require_POST
def owner_product_toggle_available(request, pk):
    """Real HTML form submit (checkbox) -- full page reload is fine here."""
    product = get_object_or_404(Product, pk=pk)
    product.available = request.POST.get("available") == "on"
    product.save()
    return redirect("owner_products")


@login_required
@require_POST
def owner_product_rename(request, pk):
    """AJAX endpoint used by the inline name field."""
    product = get_object_or_404(Product, pk=pk)
    name = request.POST.get("value", "").strip()
    if name:
        product.name = name
        product.save()
        return JsonResponse({"ok": True, "name": product.name})
    return JsonResponse({"ok": False, "error": "Name cannot be empty."}, status=400)


@login_required
@require_POST
def owner_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    name = product.name
    product.delete()
    messages.success(request, f'"{name}" was removed from the shop.')
    return redirect("owner_products")


@login_required
@require_POST
def owner_variant_update(request, pk):
    """AJAX endpoint: expects `field` (size|price) and `value`."""
    variant = get_object_or_404(ProductVariant, pk=pk)
    field = request.POST.get("field")
    value = request.POST.get("value", "")
    if field == "size":
        value = value.strip()
        if not value:
            return JsonResponse({"ok": False, "error": "Size cannot be empty."}, status=400)
        variant.size = value
    elif field == "price":
        try:
            variant.price = max(0, float(value))
        except ValueError:
            return JsonResponse({"ok": False, "error": "Invalid price."}, status=400)
    else:
        return JsonResponse({"ok": False, "error": "Unknown field."}, status=400)
    variant.save()
    return JsonResponse({"ok": True, "size": variant.size, "price": str(variant.price)})


@login_required
@require_POST
def owner_variant_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    ProductVariant.objects.create(product=product, size="New size", price=0)
    return redirect("owner_products")


@login_required
@require_POST
def owner_variant_delete(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)
    if variant.product.variants.count() <= 1:
        messages.error(request, "A product needs at least one size.")
    else:
        variant.delete()
    return redirect("owner_products")


# ---------------------------------------------------------------------------
# Owner: orders & earnings
# ---------------------------------------------------------------------------
@login_required
def owner_orders(request):
    today = timezone.localdate()
    orders = Order.objects.prefetch_related("items").all()
    todays_orders = orders.filter(created_at__date=today)
    today_earnings = todays_orders.aggregate(s=Sum("total"))["s"] or 0
    all_earnings = orders.aggregate(s=Sum("total"))["s"] or 0

    daily = (
        orders.annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(order_count=Count("id"), earnings=Sum("total"))
        .order_by("-day")
    )

    return render(request, "shop/owner_orders.html", {
        "orders": orders[:100],
        "today_orders_count": todays_orders.count(),
        "today_earnings": today_earnings,
        "all_orders_count": orders.count(),
        "all_earnings": all_earnings,
        "daily": daily,
    })


# ---------------------------------------------------------------------------
# Owner: settings
# ---------------------------------------------------------------------------
@login_required
def owner_settings(request):
    settings_obj = ShopSetting.load()
    if request.method == "POST":
        if "save_settings" in request.POST:
            form = ShopSettingForm(request.POST, request.FILES, instance=settings_obj)
            if form.is_valid():
                form.save()
                messages.success(request, "Shop settings saved.")
                return redirect("owner_settings")
        elif "change_password" in request.POST:
            pw_form = OwnerPasswordChangeForm(user=request.user, data=request.POST)
            if pw_form.is_valid():
                user = pw_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully.")
                return redirect("owner_settings")
            else:
                form = ShopSettingForm(instance=settings_obj)
                return render(request, "shop/owner_settings.html", {
                    "form": form, "pw_form": pw_form, "settings": settings_obj,
                })
    form = ShopSettingForm(instance=settings_obj)
    pw_form = OwnerPasswordChangeForm(user=request.user)
    return render(request, "shop/owner_settings.html", {
        "form": form, "pw_form": pw_form, "settings": settings_obj,
    })
