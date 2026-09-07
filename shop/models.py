from decimal import Decimal

from django.db import models
from django.urls import reverse


class Category(models.TextChoices):
    MILK = "Milk", "Milk"
    CURD = "Curd", "Curd"
    BUTTER = "Butter", "Butter"
    GHEE = "Ghee", "Ghee"
    BEVERAGES = "Beverages", "Beverages"
    SWEETS = "Sweets", "Sweets"
    PANEER = "Paneer", "Paneer"


def product_image_path(instance, filename):
    return f"products/{filename}"


class Product(models.Model):
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=20, choices=Category.choices)
    image = models.ImageField(upload_to=product_image_path)
    available = models.BooleanField(default=True, help_text="Untick to hide this item from customers.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("storefront") + f"#product-{self.pk}"

    @property
    def default_variant(self):
        return self.variants.order_by("price").first()


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    size = models.CharField(max_length=40, help_text="e.g. 250 ml, 500 g, 1 kg")
    price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ["price"]

    def __str__(self):
        return f"{self.product.name} - {self.size} (Rs.{self.price})"


class ShopSetting(models.Model):
    """Singleton row (pk=1) holding site-wide, owner-editable settings."""

    upi_id = models.CharField(max_length=120, blank=True, default="")
    qr_image = models.ImageField(upload_to="settings/", blank=True, null=True)
    morning_open = models.CharField(max_length=20, default="6:00 AM")
    morning_close = models.CharField(max_length=20, default="10:00 AM")
    evening_open = models.CharField(max_length=20, default="6:00 PM")
    evening_close = models.CharField(max_length=20, default="9:30 PM")

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Shop Settings"


class Order(models.Model):
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new and not self.order_number:
            self.order_number = f"SS{self.pk:06d}"
            super().save(update_fields=["order_number"])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product_name = models.CharField(max_length=120)
    variant_size = models.CharField(max_length=40)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.product_name} ({self.variant_size}) x{self.quantity}"
