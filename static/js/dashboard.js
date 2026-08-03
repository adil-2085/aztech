// ==========================================
// dashboard.js — Product Management window
// Kept separate from static/js/main.js on purpose: the storefront and the
// internal ERP are different surfaces with different concerns, and one
// growing monolithic JS file for both would get unwieldy fast. Only
// dashboard pages load this file.
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('product-management-root')) {
        initProductList();
    }
    if (document.getElementById('product-form-root')) {
        initProductForm();
    }
});

function authHeaders(extra = {}) {
    return { 'X-CSRFToken': CSRF_TOKEN, ...extra };
}

// ==========================================
// PRODUCT LIST PAGE
// ==========================================

async function initProductList() {
    const tbody = document.getElementById('product-table-body');

    let products;
    try {
        const res = await fetch('/dashboard/api/products/');
        if (!res.ok) throw new Error(`API returned ${res.status}`);
        products = await res.json();
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="7" class="px-4 py-8 text-center text-red-500">Couldn't load products.</td></tr>`;
        console.error(err);
        return;
    }

    if (!products.length) {
        tbody.innerHTML = `<tr><td colspan="7" class="px-4 py-8 text-center text-gray-400">No products yet — add your first one.</td></tr>`;
        return;
    }

    tbody.innerHTML = '';
    products.forEach(p => {
        const thumb = p.images && p.images.length
            ? `<img src="${p.images[0].image}" class="w-10 h-12 object-cover rounded">`
            : `<div class="w-10 h-12 bg-gray-100 rounded"></div>`;

        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="px-4 py-3">${thumb}</td>
            <td class="px-4 py-3 font-semibold">${p.title}</td>
            <td class="px-4 py-3 text-gray-500">${p.category_name || '—'}</td>
            <td class="px-4 py-3">£${p.price}</td>
            <td class="px-4 py-3">${p.stock_quantity}</td>
            <td class="px-4 py-3">
                <span class="text-xs font-semibold px-2 py-1 rounded-full ${statusBadgeClass(p.status_name)}">
                    ${p.status_name || 'No status'}
                </span>
            </td>
            <td class="px-4 py-3 text-right space-x-3">
                <a href="/dashboard/products/${p.id}/edit/" class="text-sm font-semibold hover:underline">Edit</a>
                <button data-id="${p.id}" data-title="${p.title}" class="delete-product-btn text-sm font-semibold text-red-600 hover:underline">Delete</button>
            </td>
        `;
        tbody.appendChild(row);
    });

    tbody.addEventListener('click', async (e) => {
        const btn = e.target.closest('.delete-product-btn');
        if (!btn) return;
        if (!confirm(`Delete "${btn.dataset.title}"? This can't be undone.`)) return;

        try {
            const res = await fetch(`/dashboard/api/products/${btn.dataset.id}/`, {
                method: 'DELETE',
                headers: authHeaders(),
            });
            if (!res.ok) throw new Error(`API returned ${res.status}`);
            btn.closest('tr').remove();
        } catch (err) {
            alert("Couldn't delete this product.");
            console.error(err);
        }
    });
}

function statusBadgeClass(statusName) {
    switch (statusName) {
        case 'Published': return 'bg-green-100 text-green-700';
        case 'Draft': return 'bg-gray-100 text-gray-600';
        case 'Archived': return 'bg-red-100 text-red-600';
        default: return 'bg-gray-100 text-gray-400';
    }
}

// ==========================================
// PRODUCT FORM PAGE (create + edit)
// ==========================================

async function initProductForm() {
    const root = document.getElementById('product-form-root');
    const productId = root.dataset.productId || null;
    const isEdit = Boolean(productId);

    const [categories, brands, statuses] = await Promise.all([
        fetchJSON('/dashboard/api/categories/'),
        fetchJSON('/dashboard/api/brands/'),
        fetchJSON('/dashboard/api/workflow-states/'),
    ]);

    populateSelect('f-category', categories, { placeholder: null });
    populateSelect('f-brand', brands, { placeholder: '— None —', keepFirst: true });
    populateSelect('f-status', statuses, { placeholder: null, textKey: 'label' });

    if (isEdit) {
        const product = await fetchJSON(`/dashboard/api/products/${productId}/`);
        fillForm(product);
        loadImages(productId);
        loadVariants(productId);
        wireImageUpload(productId);
        wireVariantAdd(productId);
    } else {
        // New product — default to "Published" if that status exists, so a
        // straightforward fill-and-save shows up on the storefront immediately.
        const publishedOption = [...document.getElementById('f-status').options].find(o => o.text === 'Published');
        if (publishedOption) publishedOption.selected = true;
        wireSlugAutofill();
    }

    document.getElementById('product-form').addEventListener('submit', (e) => handleSubmit(e, productId));
}

function fetchJSON(url) {
    return fetch(url).then(res => {
        if (!res.ok) throw new Error(`${url} returned ${res.status}`);
        return res.json();
    });
}

function populateSelect(elId, items, { placeholder, keepFirst, textKey = 'name' } = {}) {
    const select = document.getElementById(elId);
    if (placeholder && !keepFirst) {
        select.innerHTML = '';
    }
    items.forEach(item => {
        const option = document.createElement('option');
        option.value = item.id;
        option.textContent = item[textKey];
        select.appendChild(option);
    });
}

function fillForm(product) {
    document.getElementById('f-title').value = product.title;
    document.getElementById('f-slug').value = product.slug;
    document.getElementById('f-category').value = product.category;
    document.getElementById('f-brand').value = product.brand || '';
    document.getElementById('f-description').value = product.description;
    document.getElementById('f-sku').value = product.sku;
    document.getElementById('f-status').value = product.status || '';
    document.getElementById('f-price').value = product.price;
    document.getElementById('f-compare-at-price').value = product.compare_at_price || '';
    document.getElementById('f-cost-per-item').value = product.cost_per_item || '';
    document.getElementById('f-stock-quantity').value = product.stock_quantity;
}

function wireSlugAutofill() {
    const titleEl = document.getElementById('f-title');
    const slugEl = document.getElementById('f-slug');
    let slugEdited = false;

    slugEl.addEventListener('input', () => { slugEdited = true; });
    titleEl.addEventListener('input', () => {
        if (slugEdited) return;
        slugEl.value = titleEl.value
            .toLowerCase()
            .trim()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/(^-|-$)/g, '');
    });
}

async function handleSubmit(e, productId) {
    e.preventDefault();
    const statusMsg = document.getElementById('f-status-msg');
    const submitBtn = document.getElementById('f-submit');
    submitBtn.disabled = true;
    statusMsg.textContent = 'Saving…';
    statusMsg.className = 'text-sm text-gray-500';

    const payload = {
        title: document.getElementById('f-title').value,
        slug: document.getElementById('f-slug').value,
        category: document.getElementById('f-category').value,
        brand: document.getElementById('f-brand').value || null,
        description: document.getElementById('f-description').value,
        sku: document.getElementById('f-sku').value,
        status: document.getElementById('f-status').value || null,
        price: document.getElementById('f-price').value,
        compare_at_price: document.getElementById('f-compare-at-price').value || null,
        cost_per_item: document.getElementById('f-cost-per-item').value || null,
        stock_quantity: document.getElementById('f-stock-quantity').value || 0,
    };

    const isEdit = Boolean(productId);
    const url = isEdit ? `/dashboard/api/products/${productId}/` : '/dashboard/api/products/';
    const method = isEdit ? 'PATCH' : 'POST';

    try {
        const res = await fetch(url, {
            method,
            headers: authHeaders({ 'Content-Type': 'application/json' }),
            body: JSON.stringify(payload),
        });
        if (!res.ok) {
            const errorBody = await res.json().catch(() => ({}));
            throw new Error(JSON.stringify(errorBody));
        }
        const saved = await res.json();

        if (isEdit) {
            statusMsg.textContent = 'Saved.';
            statusMsg.className = 'text-sm text-green-600';
        } else {
            // First save — redirect into edit mode so Images/Variants unlock.
            window.location = `/dashboard/products/${saved.id}/edit/`;
        }
    } catch (err) {
        statusMsg.textContent = "Couldn't save — check the fields above.";
        statusMsg.className = 'text-sm text-red-600';
        console.error(err);
    } finally {
        submitBtn.disabled = false;
    }
}

// ==========================================
// IMAGES (edit mode only)
// ==========================================

async function loadImages(productId) {
    document.getElementById('product-subsections').classList.remove('hidden');
    const images = await fetchJSON(`/dashboard/api/product-images/?product=${productId}`);
    renderImages(images);
}

function renderImages(images) {
    const container = document.getElementById('image-list');
    container.innerHTML = '';
    images.forEach(img => {
        const el = document.createElement('div');
        el.className = 'relative group';
        el.innerHTML = `
            <img src="${img.image}" class="w-full aspect-square object-cover rounded ${img.is_primary ? 'ring-2 ring-asos-black' : ''}">
            <button data-id="${img.id}" class="delete-image-btn absolute top-1 right-1 bg-white/90 text-red-600 rounded-full w-6 h-6 text-xs opacity-0 group-hover:opacity-100 transition">✕</button>
        `;
        container.appendChild(el);
    });
    container.querySelectorAll('.delete-image-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            await fetch(`/dashboard/api/product-images/${btn.dataset.id}/`, { method: 'DELETE', headers: authHeaders() });
            btn.closest('div').remove();
        });
    });
}

function wireImageUpload(productId) {
    document.getElementById('image-upload-input').addEventListener('change', async (e) => {
        const files = [...e.target.files];
        for (const [index, file] of files.entries()) {
            const formData = new FormData();
            formData.append('product', productId);
            formData.append('image', file);
            formData.append('display_order', index);
            await fetch('/dashboard/api/product-images/', {
                method: 'POST',
                headers: authHeaders(), // no Content-Type — browser sets multipart boundary
                body: formData,
            });
        }
        loadImages(productId);
        e.target.value = '';
    });
}

// ==========================================
// VARIANTS (edit mode only)
// ==========================================

async function loadVariants(productId) {
    const variants = await fetchJSON(`/dashboard/api/product-variants/?product=${productId}`);
    renderVariants(variants);
}

function renderVariants(variants) {
    const container = document.getElementById('variant-list');
    container.innerHTML = '';
    if (!variants.length) {
        container.innerHTML = `<p class="text-sm text-gray-400">No variants — this product sells against its base stock quantity.</p>`;
        return;
    }
    variants.forEach(v => {
        const row = document.createElement('div');
        row.className = 'flex items-center justify-between text-sm border border-gray-200 rounded-md px-3 py-2';
        row.innerHTML = `
            <span>${v.attribute_name}: <strong>${v.attribute_value}</strong> — ${v.sku} — stock ${v.stock_quantity}</span>
            <button data-id="${v.id}" class="delete-variant-btn text-red-600 hover:underline">Remove</button>
        `;
        container.appendChild(row);
    });
    container.querySelectorAll('.delete-variant-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            await fetch(`/dashboard/api/product-variants/${btn.dataset.id}/`, { method: 'DELETE', headers: authHeaders() });
            btn.closest('div').remove();
        });
    });
}

function wireVariantAdd(productId) {
    document.getElementById('variant-add-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
            product: productId,
            attribute_name: document.getElementById('v-attribute-name').value,
            attribute_value: document.getElementById('v-attribute-value').value,
            sku: document.getElementById('v-sku').value,
            stock_quantity: document.getElementById('v-stock-quantity').value,
        };
        const res = await fetch('/dashboard/api/product-variants/', {
            method: 'POST',
            headers: authHeaders({ 'Content-Type': 'application/json' }),
            body: JSON.stringify(payload),
        });
        if (res.ok) {
            e.target.reset();
            loadVariants(productId);
        } else {
            alert("Couldn't add variant — check the SKU is unique.");
        }
    });
}