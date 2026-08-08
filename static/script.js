// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {

    // ---------- Product Search ----------
    const productSearch = document.getElementById('productSearch');
    if (productSearch) {
        productSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            const productCards = document.querySelectorAll('.product-card');
            let hasResults = false;
            productCards.forEach(card => {
                const name = card.querySelector('h3').textContent.toLowerCase();
                const desc = card.querySelector('p').textContent.toLowerCase();
                if (name.includes(searchTerm) || desc.includes(searchTerm)) {
                    card.style.display = 'block';
                    hasResults = true;
                } else {
                    card.style.display = 'none';
                }
            });
            // Show no-results if needed – you can reuse the existing logic
        });
    }

    // ---------- Add to Cart ----------
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            const name = this.getAttribute('data-name');
            const price = parseFloat(this.getAttribute('data-price'));

            fetch('/api/cart/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ product_id: parseInt(productId), quantity: 1 })
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    showToast(`${name} added to cart!`, 'success');
                } else {
                    showToast('Error adding item', 'error');
                }
            })
            .catch(err => showToast('Error: ' + err.message, 'error'));
        });
    });

    // ---------- Contact Form ----------
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            showToast('Thank you for your message! We will get back to you soon.', 'success');
            this.reset();
        });
    }

    // ---------- Login Form ----------
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            showToast('Login functionality would be implemented with backend system.', 'success');
            this.reset();
        });
    }

    // ---------- Register Form ----------
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            showToast('Registration functionality would be implemented with backend system.', 'success');
            this.reset();
        });
    }

    // ---------- Checkout Page ----------
    const shippingSame = document.getElementById('shipping-same');
    if (shippingSame) {
        shippingSame.addEventListener('change', function() {
            const shippingAddress = document.getElementById('shipping-address');
            if (this.checked) {
                shippingAddress.classList.add('hidden');
            } else {
                shippingAddress.classList.remove('hidden');
            }
        });
    }

    // ---------- Payment method selection (UPDATED) ----------
    document.querySelectorAll('.payment-option').forEach(option => {
        option.addEventListener('click', function() {
            const method = this.getAttribute('data-method');
            // Hide all payment details (only card-details exists now)
            document.querySelectorAll('.payment-details').forEach(detail => detail.classList.add('hidden'));
            // Show card details only if "card" is selected
            if (method === 'card') {
                document.getElementById('card-details').classList.remove('hidden');
            }
            // For UPI, we DO NOT show any extra fields because Razorpay handles UPI inside its popup.
            // For COD, we hide everything (already hidden by default).
            document.querySelectorAll('.payment-option').forEach(opt => opt.classList.remove('selected'));
            this.classList.add('selected');
        });
    });

    // ---------- Place Order with Razorpay ----------
    const placeOrderBtn = document.getElementById('place-order');
    if (placeOrderBtn) {
        placeOrderBtn.addEventListener('click', function() {
            // Validate billing form
            const billingForm = document.getElementById('billingForm');
            const inputs = billingForm.querySelectorAll('input[required]');
            let valid = true;
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    valid = false;
                    input.style.borderColor = 'red';
                } else {
                    input.style.borderColor = '#ddd';
                }
            });
            if (!valid) {
                showToast('Please fill out all required billing fields.', 'error');
                return;
            }

            const paymentMethod = document.querySelector('input[name="payment-method"]:checked').value;

            // For Cash on Delivery – submit order directly
            if (paymentMethod === 'cod') {
                const billingData = getBillingData();
                fetch('/place-order', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ...billingData, payment_method: 'cod' })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        document.getElementById('order-items').classList.add('hidden');
                        document.querySelector('.cart-total').classList.add('hidden');
                        document.getElementById('payment-success').classList.remove('hidden');
                        showToast('Order placed successfully! (COD)', 'success');
                    } else {
                        showToast('Error placing order', 'error');
                    }
                })
                .catch(err => showToast('Error: ' + err.message, 'error'));
                return;
            }

            // For online payment (Card/UPI) – create Razorpay order
            const total = parseFloat(document.getElementById('order-total').textContent.replace('₹', ''));
            if (total <= 0) {
                showToast('Cart is empty. Please add items.', 'error');
                return;
            }

            // Create order on backend
            fetch('/create-order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ amount: total })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showToast('Error: ' + data.error, 'error');
                    return;
                }
                // Open Razorpay checkout
                const options = {
                    key: data.razorpay_key,
                    amount: data.amount,
                    currency: 'INR',
                    name: 'Crown Bakery',
                    description: 'Order Payment',
                    order_id: data.order_id,
                    handler: function(response) {
                        // Payment success – verify on backend
                        fetch('/payment-callback', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                            body: new URLSearchParams({
                                razorpay_payment_id: response.razorpay_payment_id,
                                razorpay_order_id: response.razorpay_order_id,
                                razorpay_signature: response.razorpay_signature
                            })
                        })
                        .then(res => res.json())
                        .then(callbackData => {
                            if (callbackData.status === 'success') {
                                document.getElementById('order-items').classList.add('hidden');
                                document.querySelector('.cart-total').classList.add('hidden');
                                document.getElementById('payment-success').classList.remove('hidden');
                                showToast('Payment successful! Order placed.', 'success');
                            } else {
                                showToast('Payment verification failed.', 'error');
                            }
                        })
                        .catch(err => showToast('Error verifying payment: ' + err.message, 'error'));
                    },
                    prefill: {
                        name: document.getElementById('billing-name').value,
                        email: document.getElementById('billing-email').value,
                        contact: document.getElementById('billing-phone').value
                    },
                    theme: {
                        color: '#d17842'
                    },
                    modal: {
                        ondismiss: function() {
                            showToast('Payment cancelled.', 'error');
                        }
                    }
                };
                const rzp = new Razorpay(options);
                rzp.open();
            })
            .catch(err => showToast('Error creating order: ' + err.message, 'error'));
        });
    }

    // ---------- Helper: Get billing data ----------
    function getBillingData() {
        return {
            billing_name: document.getElementById('billing-name').value,
            billing_email: document.getElementById('billing-email').value,
            billing_phone: document.getElementById('billing-phone').value,
            billing_address: document.getElementById('billing-address').value,
            billing_city: document.getElementById('billing-city').value,
            billing_state: document.getElementById('billing-state').value,
            billing_zip: document.getElementById('billing-zip').value
        };
    }

    // ---------- Toast Notification ----------
    function showToast(message, type = 'success') {
        const container = document.getElementById('toastContainer');
        if (!container) return;
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            <div class="toast-content">
                <h4>${type === 'success' ? 'Success' : 'Error'}</h4>
                <p>${message}</p>
            </div>
            <button class="close-toast">&times;</button>
        `;
        container.appendChild(toast);
        toast.querySelector('.close-toast').addEventListener('click', () => toast.remove());
        setTimeout(() => { if (toast.parentNode) toast.remove(); }, 3000);
    }
});