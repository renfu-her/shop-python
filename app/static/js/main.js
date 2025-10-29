// Main JavaScript for DEMO Mall E-commerce

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Add to cart form validation
    const addToCartForms = document.querySelectorAll('form[action*="add_to_cart"]');
    addToCartForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const quantityInput = form.querySelector('input[name="quantity"]');
            if (quantityInput && quantityInput.value <= 0) {
                e.preventDefault();
                alert('請輸入有效的數量');
                return false;
            }
        });
    });

    // Cart quantity update
    const quantityInputs = document.querySelectorAll('input[name="quantity"]');
    quantityInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            if (this.value < 0) {
                this.value = 0;
            }
        });
    });

    // Coupon validation
    const couponForm = document.querySelector('form[action*="apply_coupon"]');
    if (couponForm) {
        couponForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const couponCode = this.querySelector('input[name="coupon_code"]').value;
            if (!couponCode.trim()) {
                alert('請輸入優惠券代碼');
                return;
            }
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>驗證中...';
            submitBtn.disabled = true;
            
            // Simulate AJAX request (replace with actual AJAX call)
            setTimeout(function() {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
                // Handle response here
            }, 1000);
        });
    }

    // Image lazy loading
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(function(img) {
        imageObserver.observe(img);
    });

    // Search suggestions (if needed)
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            if (query.length >= 2) {
                // Implement search suggestions here
                console.log('Searching for:', query);
            }
        });
    }

    // Product image zoom (if needed)
    const productImages = document.querySelectorAll('.product-card img');
    productImages.forEach(function(img) {
        img.addEventListener('click', function() {
            // Implement image zoom modal here
            console.log('Image clicked:', this.src);
        });
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Price formatting
    const priceElements = document.querySelectorAll('.price');
    priceElements.forEach(function(element) {
        const price = parseFloat(element.textContent);
        if (!isNaN(price)) {
            element.textContent = '$' + price.toLocaleString();
        }
    });

    // Stock status check
    const stockElements = document.querySelectorAll('.stock-status');
    stockElements.forEach(function(element) {
        const stock = parseInt(element.textContent);
        if (stock <= 0) {
            element.classList.add('text-danger');
            element.textContent = '缺貨';
        } else if (stock <= 5) {
            element.classList.add('text-warning');
            element.textContent = '庫存不足';
        } else {
            element.classList.add('text-success');
            element.textContent = '有庫存';
        }
    });

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card, .product-card');
    cards.forEach(function(card, index) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(function() {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});

// Utility functions
function formatPrice(price) {
    return '$' + parseFloat(price).toLocaleString();
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-TW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertContainer, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alertContainer);
            bsAlert.close();
        }, 5000);
    }
}

// AJAX helper function
function makeRequest(url, method = 'GET', data = null) {
    return fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: data ? JSON.stringify(data) : null
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('發生錯誤，請重試', 'danger');
    });
}
