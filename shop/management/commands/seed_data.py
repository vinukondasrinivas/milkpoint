import shutil
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand

from shop.models import Product, ProductVariant, ShopSetting

SEED_IMG_DIR = Path(settings.BASE_DIR) / "shop" / "static" / "shop" / "seed_images"

CATALOG = [
    ("Cow Milk", "Milk", "cow.jpg", [("250 ml", 15), ("500 ml", 30), ("1 L", 60)]),
    ("Buffalo Milk", "Milk", "buffalo_milk.jpg", [("250 ml", 20), ("500 ml", 40), ("1 L", 80)]),
    ("Cow Curd", "Curd", "cow_curd.jpg", [("200 g", 10), ("500 g", 30), ("1 kg", 60)]),
    ("Buffalo Curd", "Curd", "buffalo_curd.jpg", [("200 g", 20), ("500 g", 40), ("1 kg", 80)]),
    ("Cow Butter", "Butter", "cow_butter.jpg", [("250 g", 150), ("500 g", 300), ("1 kg", 600)]),
    ("Buffalo Butter", "Butter", "buffalo_butter.jpg", [("250 g", 150), ("500 g", 300), ("1 kg", 600)]),
    ("Cow Ghee", "Ghee", "cow_ghee_2.jpg", [("250 g", 200), ("500 g", 400), ("1 kg", 800)]),
    ("Buffalo Ghee", "Ghee", "buffalo_ghee2.jpg", [("250 g", 200), ("500 g", 400), ("1 kg", 800)]),
    ("Buttermilk", "Beverages", "buttermilk_tetra.jpg", [("200 ml", 10)]),
    ("Lassi", "Beverages", "lassi.jpg", [("200 ml", 12)]),
    ("Badam Milk", "Beverages", "badam_milk.jpg", [("180 ml", 30)]),
    ("Doodh Peda", "Sweets", "doodh_peda.jpg", [("250 g", 200), ("500 g", 400), ("1 kg", 800)]),
    ("Palkova", "Sweets", "palkova.jpg", [("250 g", 200), ("500 g", 400), ("1 kg", 800)]),
    ("Paneer", "Paneer", "paneer.jpg", [("200 g", 125), ("500 g", 250), ("1 kg", 450)]),
]


class Command(BaseCommand):
    help = "Creates the initial product catalog, shop settings, and the owner login (idempotent)."

    def handle(self, *args, **options):
        # --- Owner account -------------------------------------------------
        User = get_user_model()
        if not User.objects.filter(username="owner").exists():
            User.objects.create_superuser(username="owner", email="", password="998929")
            self.stdout.write(self.style.SUCCESS("Created owner login -> username: owner / password: 998929"))
        else:
            self.stdout.write("Owner account already exists, skipping.")

        # --- Shop settings ---------------------------------------------------
        shop_setting = ShopSetting.load()
        if not shop_setting.qr_image:
            qr_path = SEED_IMG_DIR / "payment_qr.jpg"
            if qr_path.exists():
                with open(qr_path, "rb") as f:
                    shop_setting.qr_image.save("payment_qr.jpg", File(f), save=True)
                self.stdout.write(self.style.SUCCESS("Loaded default payment QR image."))

        # --- Products & variants --------------------------------------------
        created_count = 0
        for name, category, image_name, variants in CATALOG:
            if Product.objects.filter(name=name).exists():
                continue
            image_path = SEED_IMG_DIR / image_name
            product = Product(name=name, category=category, available=True)
            if image_path.exists():
                with open(image_path, "rb") as f:
                    product.image.save(image_name, File(f), save=False)
            product.save()
            for size, price in variants:
                ProductVariant.objects.create(product=product, size=size, price=price)
            created_count += 1

        if created_count:
            self.stdout.write(self.style.SUCCESS(f"Created {created_count} products with their sizes."))
        else:
            self.stdout.write("Catalog already seeded, nothing new to add.")
