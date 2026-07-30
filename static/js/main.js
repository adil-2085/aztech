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
});