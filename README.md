<!-- # Sai Srinivasa Milk & Milk Products &mdash; Django E-commerce Site

A full-stack dairy shop website: Django (Python) backend + server-rendered
HTML/CSS/JS frontend + PostgreSQL (or MySQL) database.

## Features

- **Storefront** &mdash; category filters, product cards with multiple pack
  sizes (e.g. Cow Milk in 250 ml / 500 ml / 1 L), add-to-cart with live
  quantity steppers, a slide-in cart drawer.
- **Checkout** &mdash; order summary + your payment QR code, "I've Paid"
  confirms the order and stores it in the database.
- **Owner Dashboard** (`/owner/login/`) &mdash; real, database-backed login
  (Django auth, hashed passwords &mdash; this is what makes the password
  change *actually stick* after a refresh, unlike a plain static site):
  - **Manage Products**: add products, edit names/sizes/prices inline,
    add or remove pack sizes, toggle a product available/unavailable,
    delete products.
  - **Orders & Earnings**: today's orders & earnings, all-time totals, a
    daily breakdown table, and a full order log &mdash; all read straight
    from the database, so it's accurate no matter when you check.
  - **Settings**: upload/replace the payment QR image, set a UPI ID,
    edit the shop's morning/evening timings, and change the owner
    password (properly hashed, not stored in plain text).
- **Footer** with both proprietor names/numbers and the shop address.

## Tech stack

- Backend / middleware: **Python 3 + Django**
- Frontend: server-rendered **HTML + CSS + vanilla JS** (no build step)
- Database: **PostgreSQL** by default, **MySQL** supported via one setting
- Images: Pillow, stored under `media/`

---

## 1. Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# then edit .env with your real database credentials / secret key
```

### Database setup (PostgreSQL &mdash; default)

```bash
# Using psql:
createdb dairy_shop
# or:
psql -c "CREATE DATABASE dairy_shop;"
```

Make sure `.env` has `DB_ENGINE=postgresql` and matching `DB_USER` /
`DB_PASSWORD` / `DB_HOST` / `DB_PORT`.

### Database setup (MySQL &mdash; alternative)

1. In `requirements.txt`, install `mysqlclient` instead of (or alongside)
   `psycopg2-binary`:
   ```bash
   pip install mysqlclient
   ```
2. In `.env`, set:
   ```
   DB_ENGINE=mysql
   DB_NAME=dairy_shop
   DB_USER=root
   DB_PASSWORD=your-mysql-password
   DB_HOST=127.0.0.1
   DB_PORT=3306
   ```
3. Create the database:
   ```sql
   CREATE DATABASE dairy_shop CHARACTER SET utf8mb4;
   ```

No code changes are needed to switch &mdash; `config/settings.py` reads
`DB_ENGINE` and configures itself automatically.

---

## 2. Initialise the app

```bash
python manage.py migrate
python manage.py seed_data
```

`seed_data` is safe to re-run any time (it skips anything that already
exists). It will:
- Create the **owner login**: username `owner`, password `998929`
- Load the 14 starting products (both milks, both curds, both butters,
  both ghees, buttermilk, lassi, badam milk, paneer, doodh peda, palkova)
  with the sizes and prices you specified
- Load the default payment QR image

## 3. Run it

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the shop, and
`http://127.0.0.1:8000/owner/login/` for the owner dashboard.

---

## Project layout

```
config/            Django project settings, root urls
shop/               The e-commerce app
  models.py         Product, ProductVariant, Order, OrderItem, ShopSetting
  views.py          Storefront, cart, checkout, owner dashboard views
  cart.py           Session-based shopping cart
  forms.py          Product / settings / password forms
  urls.py           App routes
  templates/shop/   All HTML templates
  static/shop/      CSS, JS, and the seed product images
  management/commands/seed_data.py   One-time catalog + owner setup
requirements.txt
.env.example
```

## Notes on going to production

This project runs with Django's built-in dev server and `DEBUG=True` by
default, which is fine for local testing but **not for a live public
site**. Before deploying:

- Set `DJANGO_DEBUG=False` and a real, random `DJANGO_SECRET_KEY` in `.env`
- Set `DJANGO_ALLOWED_HOSTS` to your real domain
- Run `python manage.py collectstatic` and serve `staticfiles/` via your
  web server (Nginx, etc.) or a service like WhiteNoise
- Serve the app itself via a production WSGI server such as Gunicorn,
  behind Nginx (or an equivalent managed hosting service)
- Make sure `media/` (uploaded product images, QR codes) is on persistent
  storage that survives deploys
- Use a real, backed-up PostgreSQL/MySQL instance (not the same throwaway
  database used for local development)

Since everything (products, prices, availability, orders, earnings, the
owner password) is now stored in the database instead of in browser
memory, it will correctly persist across page refreshes, server
restarts, and different devices &mdash; that was the main limitation of
the earlier static HTML/CSS/JS version of this site. -->

# 🥛 MilkPoint - Online Dairy Shop

MilkPoint is a Django-based web application for managing and selling
milk and dairy products online.

The application provides a customer storefront for browsing products,
adding products to a cart, placing orders, and viewing order details.
It also includes an owner/admin section for managing products and orders.

## 🚀 Features

### Customer Features
- Browse milk and dairy products
- View product details
- Add products to cart
- Update cart quantities
- Checkout and place orders
- Order success confirmation
- Responsive user interface

### Owner/Admin Features
- Owner login
- Add and manage products
- View customer orders
- Manage product information
- Owner settings

## 🛠️ Technologies Used

- Python
- Django
- HTML5
- CSS3
- JavaScript
- SQLite
- Git & GitHub

## 📂 Project Structure

```text
milkpoint/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── shop/
│   ├── migrations/
│   ├── management/
│   ├── static/
│   ├── templates/
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── cart.py
│
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md