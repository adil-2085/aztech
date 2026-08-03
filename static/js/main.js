document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Sticky Header Shadow on Scroll
    const header = document.getElementById('main-header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 10) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }

    // 2. Mega Menu Hover Logic
    const navTriggers = document.querySelectorAll('.nav-trigger');
    const megaMenus = document.querySelectorAll('.mega-menu');
    let timeoutId;

    // Function to close all menus safely
    const closeAllMenus = () => {
        megaMenus.forEach(menu => menu.classList.remove('active'));
        navTriggers.forEach(btn => btn.classList.replace('border-black', 'border-transparent'));
    };

    // Setup triggers for desktop navigation
    navTriggers.forEach(trigger => {
        const targetId = trigger.getAttribute('data-target');
        const targetMenu = document.getElementById(targetId);

        if (targetMenu) {
            // Open on hover
            trigger.addEventListener('mouseenter', () => {
                clearTimeout(timeoutId);
                closeAllMenus();
                targetMenu.classList.add('active');
                trigger.classList.replace('border-transparent', 'border-black');
            });

            // Start close timer when leaving the trigger
            trigger.addEventListener('mouseleave', () => {
                timeoutId = setTimeout(closeAllMenus, 150); // Small delay allows moving mouse to the menu
            });

            // Clear close timer if entering the menu itself
            targetMenu.addEventListener('mouseenter', () => {
                clearTimeout(timeoutId);
            });

            // Start close timer when leaving the menu
            targetMenu.addEventListener('mouseleave', () => {
                timeoutId = setTimeout(closeAllMenus, 150);
            });
        }
    });

    // Close menu if clicking outside the header area
    document.addEventListener('click', (e) => {
        if (header && !header.contains(e.target)) {
            closeAllMenus();
        }
    });

    // 3. Product Catalog window (grid page + detail page)
    if (document.getElementById('product-grid')) {
        initProductGrid();
    }
    if (document.getElementById('product-detail-root')) {
        initProductDetail();
    }
});

// ==========================================
// PRODUCT GRID (store/index.html)
// ==========================================

async function initProductGrid() {
    const grid = document.getElementById('product-grid');
    const emptyMsg = document.getElementById('product-grid-empty');
    const filterBar = document.getElementById('category-filters');

    let products = [];
    try {
        const res = await fetch('/api/products/');
        if (!res.ok) throw new Error(`API returned ${res.status}`);
        products = await res.json();
    } catch (err) {
        grid.innerHTML = `<p class="col-span-full text-center text-red-500 py-16">Couldn't load products right now.</p>`;
        console.error('Failed to load products:', err);
        return;
    }

    buildCategoryChips(products, filterBar, (categorySlug) => {
        const filtered = categorySlug
            ? products.filter(p => p.category_slug === categorySlug)
            : products;
        renderProductCards(filtered, grid, emptyMsg);
    });

    renderProductCards(products, grid, emptyMsg);
}

function buildCategoryChips(products, filterBar, onSelect) {
    if (!filterBar) return;

    const seen = new Map();
    products.forEach(p => {
        if (p.category_slug && !seen.has(p.category_slug)) {
            seen.set(p.category_slug, p.category_name);
        }
    });

    // Keep the existing "All" chip, append one chip per category found.
    seen.forEach((name, slug) => {
        const chip = document.createElement('button');
        chip.dataset.category = slug;
        chip.className = 'filter-chip px-5 py-2 rounded-full text-sm font-bold uppercase tracking-wide border border-gray-300 whitespace-nowrap hover:border-asos-black transition';
        chip.textContent = name;
        filterBar.appendChild(chip);
    });

    filterBar.addEventListener('click', (e) => {
        const chip = e.target.closest('.filter-chip');
        if (!chip) return;

        filterBar.querySelectorAll('.filter-chip').forEach(c => {
            c.classList.remove('active', 'bg-asos-black', 'text-white', 'border-asos-black');
            c.classList.add('border-gray-300');
        });
        chip.classList.add('active', 'bg-asos-black', 'text-white', 'border-asos-black');
        chip.classList.remove('border-gray-300');

        onSelect(chip.dataset.category);
    });
}

function renderProductCards(products, grid, emptyMsg) {
    grid.innerHTML = '';

    if (!products.length) {
        emptyMsg.classList.remove('hidden');
        return;
    }
    emptyMsg.classList.add('hidden');

    products.forEach(p => {
        const card = document.createElement('a');
        card.href = `/product/${p.slug}/`;
        card.className = 'group block';

        const image = p.primary_image || '';
        const comparePrice = p.compare_at_price
            ? `<span class="text-xs text-gray-400 line-through">£${p.compare_at_price}</span>`
            : '';

        card.innerHTML = `
            <div class="aspect-3-4 bg-gray-100 rounded-md overflow-hidden">
                ${image
                    ? `<img src="${image}" alt="${p.title}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300">`
                    : `<div class="w-full h-full flex items-center justify-center text-gray-300 text-xs">No image</div>`
                }
            </div>
            <p class="text-xs text-gray-500 mt-3 uppercase tracking-wide">${p.brand_name || ''}</p>
            <p class="text-sm font-semibold mt-0.5 group-hover:underline">${p.title}</p>
            <div class="flex items-center gap-2 mt-1">
                <span class="text-sm font-bold">£${p.price}</span>
                ${comparePrice}
            </div>
        `;
        grid.appendChild(card);
    });
}

// ==========================================
// PRODUCT DETAIL (store/product_detail.html)
// ==========================================

async function initProductDetail() {
    const root = document.getElementById('product-detail-root');
    const slug = root.dataset.productSlug;

    let product;
    try {
        const res = await fetch(`/api/products/${slug}/detail/`);
        if (!res.ok) throw new Error(`API returned ${res.status}`);
        product = await res.json();
    } catch (err) {
        root.innerHTML = `<p class="text-center text-red-500 py-16">Couldn't load this product right now.</p>`;
        console.error('Failed to load product detail:', err);
        return;
    }

    document.getElementById('pd-brand').textContent = product.brand_name || '';
    document.getElementById('pd-title').textContent = product.title;
    document.getElementById('pd-description').textContent = product.description;
    document.getElementById('pd-price').textContent = `£${product.price}`;

    const comparePriceEl = document.getElementById('pd-compare-price');
    if (product.compare_at_price) {
        comparePriceEl.textContent = `£${product.compare_at_price}`;
        comparePriceEl.classList.remove('hidden');
    }

    initGallery(product.images);

    if (product.variants && product.variants.length) {
        initVariantSelector(product.variants);
    }
}

function initGallery(images) {
    const mainImage = document.getElementById('gallery-main-image');
    const thumbsContainer = document.getElementById('gallery-thumbs');

    if (!images || !images.length) {
        mainImage.alt = 'No image available';
        return;
    }

    const setActiveImage = (image, thumbEl) => {
        mainImage.src = image.image;
        mainImage.alt = image.alt_text || '';
        thumbsContainer.querySelectorAll('.gallery-thumb').forEach(t => t.classList.remove('active'));
        if (thumbEl) thumbEl.classList.add('active');
    };

    images.forEach((image, index) => {
        const thumb = document.createElement('button');
        thumb.className = 'gallery-thumb w-16 h-20 rounded-md overflow-hidden border-2 border-transparent flex-shrink-0';
        thumb.innerHTML = `<img src="${image.image}" alt="${image.alt_text || ''}" class="w-full h-full object-cover">`;
        thumb.addEventListener('click', () => setActiveImage(image, thumb));
        thumbsContainer.appendChild(thumb);

        if (index === 0) setActiveImage(image, thumb);
    });
}

function initVariantSelector(variants) {
    const container = document.getElementById('pd-variants');
    const optionsEl = document.getElementById('pd-variant-options');
    const stockEl = document.getElementById('pd-variant-stock');
    const priceEl = document.getElementById('pd-price');
    const addToCartBtn = document.getElementById('pd-add-to-cart');

    container.classList.remove('hidden');

    const selectVariant = (variant, optionEl) => {
        optionsEl.querySelectorAll('.variant-swatch').forEach(o => o.classList.remove('selected'));
        optionEl.classList.add('selected');

        priceEl.textContent = `£${variant.price}`;
        stockEl.textContent = variant.stock_quantity > 0
            ? `${variant.stock_quantity} in stock`
            : 'Out of stock';

        addToCartBtn.disabled = variant.stock_quantity <= 0;
    };

    variants.forEach((variant, index) => {
        const option = document.createElement('button');
        option.className = 'variant-swatch w-11 h-11 rounded-full border-2 border-gray-300 text-sm font-semibold hover:border-asos-black transition';
        option.textContent = variant.attribute_value;
        option.addEventListener('click', () => selectVariant(variant, option));
        optionsEl.appendChild(option);

        if (index === 0) selectVariant(variant, option);
    });
}