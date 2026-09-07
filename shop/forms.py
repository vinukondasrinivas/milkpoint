from django import forms
from django.contrib.auth.forms import PasswordChangeForm

from .models import Product, ProductVariant, ShopSetting


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "category", "image", "available"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Cow Milk"}),
        }


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ["size", "price"]
        widgets = {
            "size": forms.TextInput(attrs={"placeholder": "e.g. 500 ml", "class": "vsize"}),
            "price": forms.NumberInput(attrs={"placeholder": "Price", "class": "vprice"}),
        }


ProductVariantFormSet = forms.inlineformset_factory(
    Product, ProductVariant, form=ProductVariantForm, extra=1, can_delete=True
)


class NewProductForm(forms.ModelForm):
    size = forms.CharField(max_length=40, widget=forms.TextInput(attrs={"placeholder": "e.g. 500 ml"}))
    price = forms.DecimalField(max_digits=8, decimal_places=2, widget=forms.NumberInput(attrs={"placeholder": "Price"}))

    class Meta:
        model = Product
        fields = ["name", "category", "image"]


class ShopSettingForm(forms.ModelForm):
    class Meta:
        model = ShopSetting
        fields = ["upi_id", "qr_image", "morning_open", "morning_close", "evening_open", "evening_close"]


class OwnerPasswordChangeForm(PasswordChangeForm):
    """Same as Django's built-in form; kept as a subclass so templates/urls read clearly."""
    pass
