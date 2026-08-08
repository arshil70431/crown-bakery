# Crown Bakery 🍰

A full-stack e-commerce web application for an online bakery, built with Flask and SQLite, featuring a complete cart-to-checkout flow with Razorpay payment integration and Cash on Delivery support.

Originally a static HTML site, rebuilt as a production-ready application with a real backend, database-driven product catalog, and secure server-side payment verification.

---

## Tech Stack

- **Backend:** Flask, Flask-SQLAlchemy
- **Database:** SQLite
- **Payments:** Razorpay (Test Mode)
- **Frontend:** Jinja2 templates, vanilla JS, CSS
- **Config:** Environment-variable-based secrets

---

## Features

- Product catalog served from a database (no hardcoded product data)
- Session-based shopping cart with add/update/remove
- User registration and login
- Checkout flow supporting:
  - **Razorpay** (UPI, cards, netbanking, wallets)
  - **Cash on Delivery**
- Server-side order and price validation
- Razorpay payment signature verification on the backend
- Basic error handling across cart, checkout, and payment routes

---

## Architecture & Key Design Decisions

**1. Prices are never trusted from the frontend.**
All order totals are recalculated server-side from the database at checkout time, rather than trusting values submitted by the client. This prevents a user from tampering with prices before submitting an order.

**2. Razorpay payments are verified server-side.**
After a successful payment on the frontend, the backend independently verifies the Razorpay payment signature using the order ID, payment ID, and secret key before marking an order as paid. A payment is never trusted purely because the frontend says it succeeded — this is the step most student implementations skip.

**3. Secrets are kept out of source control.**
Razorpay API keys are loaded via environment variables rather than hardcoded in `config.py`. `.env`, the SQLite database, and the virtual environment are all excluded via `.gitignore`.

**4. Two payment paths, one order model.**
Both Razorpay and Cash on Delivery orders flow through the same order-creation logic, keeping order status handling consistent regardless of payment method.

---

## Project Structure

```
crown_bakery/
├── app.py              # Routes and application logic
├── models.py            # SQLAlchemy models (Product, User, Order, etc.)
├── config.py             # App configuration, loads secrets from environment
├── requirements.txt
├── templates/            # Jinja2 templates
│   ├── base.html
│   ├── home.html
│   ├── products.html
│   ├── checkout.html
│   ├── login.html
│   ├── register.html
│   ├── about.html
│   └── contact.html
└── static/
    ├── style.css
    └── script.js
```

---

## Setup & Run Locally

```bash
# Clone the repo
git clone https://github.com/arshil70431/crown-bakery.git
cd crown-bakery

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set your Razorpay test keys as environment variables
export RAZORPAY_KEY_ID="rzp_test_xxxxxxxx"
export RAZORPAY_KEY_SECRET="your_secret_here"

# Run the app
python app.py
```

The app will be available at `http://127.0.0.1:5000`.

---

## Notes

- Currently configured for **Razorpay Test Mode** — use Razorpay's official test card numbers to simulate payments.
- The SQLite database (`instance/`) is excluded from version control; running the app will initialize it locally.
- Built as part of an internship project, migrating a static bakery site into a production-style full-stack application.
