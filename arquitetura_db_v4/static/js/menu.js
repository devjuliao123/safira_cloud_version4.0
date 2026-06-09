document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const toastContainer = document.getElementById('toast-container');

    // Sidebar Toggle
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');

            // On mobile, toggle active class instead
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle('active');
            }
        });
    }

    // Navigation Feedback (Toasts for development)
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');

            // If it's a placeholder link (not menu index)
            if (!['/menu'].includes(href)) {
                showToast(`Navegando para: ${link.innerText.trim()}`);
            }
        });
    });

    /**
     * Show a simple toast message
     * @param {string} message
     */
    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.innerHTML = `
            <i class="fas fa-info-circle"></i>
            <span>${message}</span>
        `;

        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease-in';

            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3000);
    }
});
