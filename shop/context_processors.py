from .models import ShopSetting


def shop_globals(request):
    """Makes shop settings and live cart count available in every template."""
    cart = request.session.get("cart", {})
    cart_count = sum(item["qty"] for item in cart.values())
    return {
        "shop_settings": ShopSetting.load(),
        "cart_count": cart_count,
    }
