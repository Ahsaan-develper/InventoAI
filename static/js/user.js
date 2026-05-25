/* InventoAI — User Page JavaScript (Cart, Search, Chatbot) */

// ── CART (localStorage based) ──────────────────
const Cart = {
    KEY: 'inventoai_cart',
    get() { return JSON.parse(localStorage.getItem(this.KEY) || '[]'); },
    save(items) { localStorage.setItem(this.KEY, JSON.stringify(items)); this.updateUI(); },
    add(product) {
        const items = this.get();
        if (!items.find(i => i.id === product.id)) { items.push(product); this.save(items); }
    },
    remove(productId) {
        const items = this.get().filter(i => i.id !== productId);
        this.save(items);
    },
    has(productId) { return this.get().some(i => i.id === productId); },
    total() { return this.get().reduce((sum, i) => sum + parseFloat(i.price), 0); },
    count() { return this.get().length; },
    clear() { this.save([]); },

    updateUI() {
        // Badge
        const badge = document.getElementById('cart-badge');
        const count = this.count();
        if (badge) { badge.textContent = count; badge.classList.toggle('show', count > 0); }

        // Update all add/remove buttons
        document.querySelectorAll('.product-card__add-btn').forEach(btn => {
            const id = parseInt(btn.dataset.productId);
            if (this.has(id)) {
                btn.classList.add('in-cart');
                btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg> Remove';
            } else {
                btn.classList.remove('in-cart');
                btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg> Add';
            }
        });

        // Cart sidebar items
        this.renderCartSidebar();
    },

    renderCartSidebar() {
        const container = document.getElementById('cart-items');
        const totalEl = document.getElementById('cart-total');
        if (!container) return;
        const items = this.get();
        if (items.length === 0) {
            container.innerHTML = '<div class="cart-sidebar__empty"><svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>Your cart is empty</div>';
        } else {
            container.innerHTML = items.map(item => `
                <div class="cart-item" data-id="${item.id}">
                    <div class="cart-item__color" style="background:${item.image_color}">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
                    </div>
                    <div class="cart-item__info">
                        <div class="cart-item__name">${item.title}</div>
                        <div class="cart-item__price-tag">$${parseFloat(item.price).toFixed(2)}</div>
                    </div>
                    <button class="cart-item__remove" onclick="Cart.remove(${item.id})" title="Remove">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                    </button>
                </div>
            `).join('');
        }
        if (totalEl) totalEl.textContent = '$' + this.total().toFixed(2);
    }
};

// ── CART SIDEBAR TOGGLE ────────────────────
function toggleCart() {
    document.getElementById('cart-sidebar').classList.toggle('open');
    document.getElementById('cart-overlay').classList.toggle('open');
}

// ── PRODUCT ADD/REMOVE TOGGLE ──────────────
function toggleCartItem(btn) {
    const id = parseInt(btn.dataset.productId);
    const product = {
        id, title: btn.dataset.title, price: btn.dataset.price,
        image_color: btn.dataset.color, description: btn.dataset.desc
    };
    if (Cart.has(id)) { Cart.remove(id); } else { Cart.add(product); }
}

// ── SEARCH ─────────────────────────────────
function initSearch() {
    const input = document.getElementById('search-input');
    const grid = document.getElementById('products-grid');
    if (!input || !grid) return;
    let debounce;
    input.addEventListener('input', () => {
        clearTimeout(debounce);
        debounce = setTimeout(() => {
            const q = input.value.trim();
            fetch(`/store/api/search/?q=${encodeURIComponent(q)}`)
                .then(r => r.json())
                .then(data => {
                    if (data.products.length === 0) {
                        grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:60px 0;color:#475569">No products found</div>';
                    } else {
                        grid.innerHTML = data.products.map(p => buildProductCard(p)).join('');
                        Cart.updateUI();
                    }
                    const countEl = document.getElementById('products-count');
                    if (countEl) countEl.textContent = `${data.products.length} product${data.products.length !== 1 ? 's' : ''}`;
                });
        }, 300);
    });
}

function buildProductCard(p) {
    return `<div class="product-card" id="product-${p.id}">
        <div class="product-card__image" style="background:linear-gradient(135deg,${p.image_color},${p.image_color}88)">
            <span class="product-card__category">${p.category}</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
        </div>
        <div class="product-card__body">
            <h3 class="product-card__title">${p.title}</h3>
            <p class="product-card__desc">${p.description}</p>
            <div class="product-card__footer">
                <div class="product-card__price">$${parseFloat(p.price).toFixed(2)} <span>USD</span></div>
                <button class="product-card__add-btn" data-product-id="${p.id}" data-title="${p.title}" data-price="${p.price}" data-color="${p.image_color}" data-desc="${p.description}" onclick="toggleCartItem(this)">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg> Add
                </button>
            </div>
        </div>
    </div>`;
}

// ── CHATBOT TOGGLE ─────────────────────────
function toggleChatbot() {
    const panel = document.getElementById('chatbot-panel');
    const toggle = document.getElementById('chatbot-toggle');
    panel.classList.toggle('open');
    toggle.classList.toggle('hidden');
}

// ── CHATBOT SEND MESSAGE ───────────────────
function sendChatMessage() {
    const input = document.getElementById('chatbot-input');
    const messages = document.getElementById('chatbot-messages');
    const text = input.value.trim();
    if (!text) return;

    // User message
    messages.innerHTML += `<div class="chatbot-msg chatbot-msg--user">${text}</div>`;
    input.value = '';
    messages.scrollTop = messages.scrollHeight;

    // Bot response (simulated)
    setTimeout(() => {
        const q = text.toLowerCase();
        let response = "I'm your InventoAI assistant. I can help you find products! Try asking about specific items or categories.";
        if (q.includes('hello') || q.includes('hi')) response = "Hello! 👋 How can I help you today? You can ask me to find products, check prices, or browse categories.";
        else if (q.includes('cart')) response = `You have ${Cart.count()} item(s) in your cart. Total: $${Cart.total().toFixed(2)}`;

        // Try to search products
        fetch(`/store/api/search/?q=${encodeURIComponent(text)}`)
            .then(r => r.json())
            .then(data => {
                if (data.products.length > 0 && !q.includes('hello') && !q.includes('hi') && !q.includes('cart')) {
                    response = `I found ${data.products.length} product(s) matching "${text}":\n\n` +
                        data.products.slice(0, 4).map(p => `• ${p.title} — $${parseFloat(p.price).toFixed(2)}`).join('\n');
                    // Also update the product grid
                    const grid = document.getElementById('products-grid');
                    if (grid) {
                        grid.innerHTML = data.products.map(p => buildProductCard(p)).join('');
                        Cart.updateUI();
                    }
                }
                messages.innerHTML += `<div class="chatbot-msg chatbot-msg--bot">${response.replace(/\n/g, '<br>')}</div>`;
                messages.scrollTop = messages.scrollHeight;
            });
    }, 500);
}

// ── SLIDER ─────────────────────────────────
function initSlider() {
    const track = document.getElementById('slider-track');
    const dots = document.querySelectorAll('.slider__dot');
    if (!track || !dots.length) return;
    let current = 0;
    const count = dots.length;

    function goTo(idx) {
        current = idx;
        track.style.transition = 'transform 0.6s cubic-bezier(0.4,0,0.2,1)';
        track.style.animation = 'none';
        track.style.transform = `translateX(-${idx * 100}%)`;
        dots.forEach((d, i) => d.classList.toggle('active', i === idx));
    }

    dots.forEach((d, i) => d.addEventListener('click', () => goTo(i)));
    setInterval(() => goTo((current + 1) % count), 5000);
    goTo(0);
}

// ── RECEIPT PAGE ───────────────────────────
function initReceipt() {
    const container = document.getElementById('receipt-items');
    const totalEl = document.getElementById('receipt-total');
    if (!container) return;
    const items = Cart.get();
    if (items.length === 0) {
        container.innerHTML = '<div class="no-items-msg">No items in cart. Go back and add some products!</div>';
        if (totalEl) totalEl.textContent = '$0.00';
        return;
    }
    container.innerHTML = items.map(item => `
        <div class="receipt-item">
            <span class="receipt-item__name">${item.title}</span>
            <span class="receipt-item__price">$${parseFloat(item.price).toFixed(2)}</span>
        </div>
    `).join('');
    if (totalEl) totalEl.textContent = '$' + Cart.total().toFixed(2);
}

function clearCartAndGoHome() { Cart.clear(); window.location.href = '/store/'; }

// ── INIT ───────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    Cart.updateUI();
    initSearch();
    initSlider();
    if (document.getElementById('receipt-items')) initReceipt();

    // Chatbot enter key
    const chatInput = document.getElementById('chatbot-input');
    if (chatInput) chatInput.addEventListener('keydown', e => { if (e.key === 'Enter') sendChatMessage(); });
});
