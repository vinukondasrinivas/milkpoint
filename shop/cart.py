"""A tiny session-backed shopping cart keyed by ProductVariant id."""

from decimal import Decimal

from .models import ProductVariant

SESSION_KEY = "cart"


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(SESSION_KEY)
        if cart is None:
            cart = {}
            self.session[SESSION_KEY] = cart
        self.cart = cart

    def save(self):
        self.session[SESSION_KEY] = self.cart
        self.session.modified = True

    def add(self, variant_id, qty=1):
        key = str(variant_id)
        current = self.cart.get(key, {"qty": 0})
        current["qty"] = max(0, current["qty"] + qty)
        if current["qty"] == 0:
            self.cart.pop(key, None)
        else:
            self.cart[key] = current
        self.save()

    def set_qty(self, variant_id, qty):
        key = str(variant_id)
        if qty <= 0:
            self.cart.pop(key, None)
        else:
            self.cart[key] = {"qty": qty}
        self.save()

    def remove(self, variant_id):
        self.cart.pop(str(variant_id), None)
        self.save()

    def clear(self):
        self.cart = {}
        self.session[SESSION_KEY] = self.cart
        self.save()

    def entries(self):
        """Resolve cart contents against live ProductVariant data."""
        results = []
        variant_ids = [int(k) for k in self.cart.keys()]
        variants = ProductVariant.objects.select_related("product").filter(id__in=variant_ids)
        variant_map = {v.id: v for v in variants}
        for key, data in list(self.cart.items()):
            variant = variant_map.get(int(key))
            if not variant:
                continue
            qty = data["qty"]
            results.append({
                "variant": variant,
                "product": variant.product,
                "qty": qty,
                "unit_price": variant.price,
                "line_total": variant.price * qty,
            })
        return results

    def total(self):
        return sum((e["line_total"] for e in self.entries()), Decimal("0.00"))

    def count(self):
        return sum(data["qty"] for data in self.cart.values())
