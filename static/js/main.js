/**
 * Z Kuşağı Çevirici - Ana JavaScript Dosyası
 * Modern animasyonlar ve etkileşimler
 */

document.addEventListener('DOMContentLoaded', function() {
    // Sayfa yükleme animasyonu
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.style.opacity = '0';
        mainContent.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            mainContent.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            mainContent.style.opacity = '1';
            mainContent.style.transform = 'translateY(0)';
        }, 100);
    }
    
    // Navbar scroll efekti
    const header = document.querySelector('header');
    let lastScrollTop = 0;
    
    window.addEventListener('scroll', function() {
        let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Aşağı kaydırma tespiti ve stilini güncelleme
        if (scrollTop > 50) {
            header.classList.add('scrolled');
            
            if (scrollTop > lastScrollTop) {
                // Aşağı kaydırma
                header.classList.add('header-hidden');
            } else {
                // Yukarı kaydırma
                header.classList.remove('header-hidden');
            }
        } else {
            header.classList.remove('scrolled');
            header.classList.remove('header-hidden');
        }
        
        lastScrollTop = scrollTop;
    });
    
    // Öğe görünürlüğüne göre animasyon
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    
    const animateOnScroll = function() {
        animateElements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementPosition < windowHeight * 0.85) {
                element.classList.add('animate');
            }
        });
    };
    
    // İlk yüklemede ve scroll sırasında kontrol et
    if (animateElements.length > 0) {
        animateOnScroll();
        window.addEventListener('scroll', animateOnScroll);
    }
    
    // Mobil menü açma/kapama
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mainNav = document.querySelector('.main-nav');
    
    if (mobileMenuToggle && mainNav) {
        mobileMenuToggle.addEventListener('click', function() {
            mainNav.classList.toggle('open');
            mobileMenuToggle.classList.toggle('active');
            document.body.classList.toggle('menu-open');
        });
        
        // Dışarı tıklandığında menüyü kapat
        document.addEventListener('click', function(event) {
            if (!event.target.closest('.main-nav') && !event.target.closest('.mobile-menu-toggle') && mainNav.classList.contains('open')) {
                mainNav.classList.remove('open');
                mobileMenuToggle.classList.remove('active');
                document.body.classList.remove('menu-open');
            }
        });
    }
    
    // Form gönderimlerinde kademeli animasyon
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        if (!form.getAttribute('data-no-animation')) {
            form.addEventListener('submit', function(e) {
                // Form normal olarak işlem görmeye devam eder, sadece görsel efekt ekler
                const formElements = this.querySelectorAll('input, textarea, button, select');
                
                formElements.forEach((element, index) => {
                    setTimeout(() => {
                        element.classList.add('submitted');
                    }, index * 50);
                });
            });
        }
    });
    
    // Özel tooltip fonksiyonu
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        const tooltipText = element.getAttribute('data-tooltip');
        const tooltip = document.createElement('div');
        tooltip.className = 'custom-tooltip';
        tooltip.textContent = tooltipText;
        
        element.addEventListener('mouseenter', function() {
            document.body.appendChild(tooltip);
            const rect = element.getBoundingClientRect();
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 10}px`;
            tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)}px`;
            tooltip.classList.add('show');
        });
        
        element.addEventListener('mouseleave', function() {
            tooltip.classList.remove('show');
            setTimeout(() => {
                if (tooltip.parentNode) tooltip.parentNode.removeChild(tooltip);
            }, 300);
        });
    });
    
    // Form validation ve görsel geri bildirim
    const validateForms = document.querySelectorAll('[data-validate]');
    
    validateForms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            // Blur olduğunda kontrol et
            input.addEventListener('blur', function() {
                validateInput(input);
            });
            
            // Input değiştiğinde tekrar kontrol et
            input.addEventListener('input', function() {
                if (input.classList.contains('error')) {
                    validateInput(input);
                }
            });
        });
        
        // Form gönderiminde tüm alanları kontrol et
        form.addEventListener('submit', function(e) {
            let hasErrors = false;
            
            inputs.forEach(input => {
                if (!validateInput(input)) {
                    hasErrors = true;
                }
            });
            
            if (hasErrors) {
                e.preventDefault();
                showNotification('error', 'Lütfen formdaki hataları düzeltin');
                
                // İlk hataya odaklan
                const firstError = form.querySelector('.error');
                if (firstError) {
                    firstError.focus();
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
    });
    
    function validateInput(input) {
        const value = input.value.trim();
        let isValid = true;
        let errorMessage = '';
        
        // Zorunlu alan kontrolü
        if (input.hasAttribute('required') && value === '') {
            isValid = false;
            errorMessage = 'Bu alan zorunludur';
        }
        
        // Email formatı kontrolü
        if (input.type === 'email' && value !== '' && !isValidEmail(value)) {
            isValid = false;
            errorMessage = 'Geçerli bir e-posta adresi girin';
        }
        
        // Min/max uzunluk kontrolü
        if (input.hasAttribute('minlength') && value.length < parseInt(input.getAttribute('minlength'))) {
            isValid = false;
            errorMessage = `En az ${input.getAttribute('minlength')} karakter gerekli`;
        }
        
        if (input.hasAttribute('maxlength') && value.length > parseInt(input.getAttribute('maxlength'))) {
            isValid = false;
            errorMessage = `En fazla ${input.getAttribute('maxlength')} karakter girilebilir`;
        }
        
        // Özel veri şekli kontrolü (data-pattern)
        if (input.hasAttribute('data-pattern')) {
            const pattern = new RegExp(input.getAttribute('data-pattern'));
            if (value !== '' && !pattern.test(value)) {
                isValid = false;
                errorMessage = input.getAttribute('data-pattern-message') || 'Geçersiz format';
            }
        }
        
        // Görsel geri bildirim
        updateInputValidation(input, isValid, errorMessage);
        
        return isValid;
    }
    
    function updateInputValidation(input, isValid, errorMessage) {
        // Eski error mesajını kaldır
        const existingError = input.parentNode.querySelector('.validation-error');
        if (existingError) {
            existingError.remove();
        }
        
        // Eski stilleri kaldır
        input.classList.remove('error', 'success');
        
        if (!isValid) {
            input.classList.add('error');
            
            // Error mesajı ekle
            const errorElement = document.createElement('div');
            errorElement.className = 'validation-error';
            errorElement.textContent = errorMessage;
            input.parentNode.appendChild(errorElement);
            
            // Animasyon ekle
            errorElement.style.opacity = '0';
            errorElement.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                errorElement.style.transition = 'all 0.3s ease';
                errorElement.style.opacity = '1';
                errorElement.style.transform = 'translateY(0)';
            }, 10);
        } else if (input.value.trim() !== '') {
            input.classList.add('success');
        }
    }
    
    function isValidEmail(email) {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(email);
    }
    
    // Düğme ve etki animasyonları için ripple efekti
    const buttons = document.querySelectorAll('button, .btn, .ripple');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const x = e.clientX - button.getBoundingClientRect().left;
            const y = e.clientY - button.getBoundingClientRect().top;
            
            const ripple = document.createElement('span');
            ripple.className = 'ripple-effect';
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            
            button.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Açılır bildirim (notification) gösterme
    window.showNotification = function(type, message, duration = 4000) {
        // Varolan bildirimleri kontrol et
        const existingNotification = document.getElementById('notification');
        
        if (existingNotification) {
            // Varolan bildirim varsa içeriğini güncelle
            const messageElement = existingNotification.querySelector('.notification-message');
            if (messageElement) {
                existingNotification.className = `notification ${type}`;
                messageElement.textContent = message;
                
                // Zaten görüntüleniyorsa, önce gizle sonra tekrar göster
                if (existingNotification.classList.contains('show')) {
                    existingNotification.classList.remove('show');
                    setTimeout(() => {
                        existingNotification.classList.add('show');
                    }, 100);
                } else {
                    existingNotification.classList.add('show');
                }
            }
        } else {
            // Yeni bildirim oluştur
            const notification = document.createElement('div');
            notification.id = 'notification';
            notification.className = `notification ${type}`;
            
            notification.innerHTML = `
                <div class="notification-content">
                    <div class="notification-icon"></div>
                    <div class="notification-message">${message}</div>
                </div>
                <button class="notification-close" onclick="closeNotification()">×</button>
            `;
            
            document.body.appendChild(notification);
            
            // Eklendikten sonra gösterme animasyonu için gecikme ekle
            setTimeout(() => {
                notification.classList.add('show');
            }, 10);
        }
        
        // Otomatik kapanma zamanlayıcısı
        clearTimeout(window.notificationTimeout);
        window.notificationTimeout = setTimeout(() => {
            closeNotification();
        }, duration);
    };
    
    // Bildirimi kapatma
    window.closeNotification = function() {
        const notification = document.getElementById('notification');
        if (notification) {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }
    };
    
    // AJAX form gönderimi için genel yardımcı fonksiyon
    window.submitFormAjax = function(formElement, successCallback, errorCallback) {
        if (!formElement) return;
        
        const formData = new FormData(formElement);
        const url = formElement.getAttribute('action') || window.location.href;
        const method = formElement.getAttribute('method') || 'POST';
        
        // Form verilerini URLSearchParams'a dönüştür (JSON yerine form verisi gönder)
        const formDataObj = {};
        formData.forEach((value, key) => {
            formDataObj[key] = value;
        });
        
        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams(formDataObj)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (typeof successCallback === 'function') {
                successCallback(data);
            } else {
                // Varsayılan başarı işlemi
                if (data.message) {
                    showNotification('success', data.message);
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (typeof errorCallback === 'function') {
                errorCallback(error);
            } else {
                // Varsayılan hata işlemi
                showNotification('error', 'Bir hata oluştu. Lütfen tekrar deneyin.');
            }
        });
    };
    
    // URL değiştiğinde sayfayı yeniden yükleme yerine içeriği güncelleme
    // SPA benzeri davranış için temel özellik (opsiyonel)
    if (window.history && window.history.pushState) {
        document.addEventListener('click', function(e) {
            // Sadece data-spa-link özelliği olan bağlantıları yakala
            const link = e.target.closest('a[data-spa-link="true"]');
            
            if (link && link.href) {
                e.preventDefault();
                const url = link.href;
                const targetElementId = link.getAttribute('data-target-element') || 'main';
                const targetElement = document.getElementById(targetElementId);
                
                if (targetElement) {
                    // Yükleniyor efekti
                    targetElement.classList.add('content-loading');
                    
                    // İçeriği AJAX ile getir
                    fetch(url)
                        .then(response => response.text())
                        .then(html => {
                            // Gelen HTML'den hedef içeriği çıkar
                            const parser = new DOMParser();
                            const doc = parser.parseFromString(html, 'text/html');
                            const newContent = doc.getElementById(targetElementId);
                            
                            if (newContent) {
                                // İçeriği güncelle
                                targetElement.innerHTML = newContent.innerHTML;
                                
                                // URL'yi güncelle
                                window.history.pushState({path: url}, '', url);
                                
                                // Sayfanın başına kaydır
                                window.scrollTo(0, 0);
                                
                                // Yükleniyor durumunu kaldır
                                targetElement.classList.remove('content-loading');
                                
                                // Sayfa başlığını güncelle
                                const newTitle = doc.querySelector('title');
                                if (newTitle) {
                                    document.title = newTitle.textContent;
                                }
                                
                                // Yeni sayfa için JavaScript'leri çalıştır
                                const scripts = newContent.querySelectorAll('script');
                                scripts.forEach(script => {
                                    const newScript = document.createElement('script');
                                    if (script.src) {
                                        newScript.src = script.src;
                                    } else {
                                        newScript.textContent = script.textContent;
                                    }
                                    document.head.appendChild(newScript);
                                });
                            }
                        })
                        .catch(error => {
                            console.error('Error loading page:', error);
                            targetElement.classList.remove('content-loading');
                            showNotification('error', 'Sayfa yüklenirken bir hata oluştu');
                        });
                }
            }
        });
    }
    
    // Sayfa içi hedef bağlantı kaydırma (smooth scroll)
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            // # bağlantısı olmadığını kontrol et
            if (this.getAttribute('href') !== '#') {
                e.preventDefault();
                
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    // Header yüksekliğini hesapla ve offset olarak kullan
                    const headerHeight = document.querySelector('header')?.offsetHeight || 0;
                    const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset;
                    const offsetPosition = targetPosition - headerHeight - 20; // Ekstra boşluk
                    
                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                    
                    // Hedef elemana vurgu efekti ekle
                    targetElement.classList.add('target-highlight');
                    setTimeout(() => {
                        targetElement.classList.remove('target-highlight');
                    }, 1500);
                }
            }
        });
    });
    
    // Tembel (lazy) yükleme görüntüleri
    const lazyImages = document.querySelectorAll('img[data-src]');
    
    if (lazyImages.length > 0) {
        const lazyLoadImage = function(image) {
            const src = image.getAttribute('data-src');
            if (!src) return;
            
            // Resmi yükle
            image.src = src;
            
            // Yükleme tamamlandığında görünür hale getir
            image.onload = function() {
                image.removeAttribute('data-src');
                image.classList.add('lazy-loaded');
            };
        };
        
        // Intersection Observer API kullanarak görünüm alanındaki resimleri yükle
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        lazyLoadImage(entry.target);
                        imageObserver.unobserve(entry.target);
                    }
                });
            });
            
            lazyImages.forEach(image => {
                imageObserver.observe(image);
            });
        } else {
            // Fallback - tüm resimleri yükle
            lazyImages.forEach(image => {
                lazyLoadImage(image);
            });
        }
    }
    
    // Tema geçişi (açık/koyu mod) - localStorage'dan tercih al
    const themeToggle = document.getElementById('theme-toggle');
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Tema tercihini uygula
    function applyTheme(theme) {
        if (theme === 'dark') {
            document.body.classList.add('dark-theme');
            if (themeToggle) themeToggle.classList.add('dark');
        } else {
            document.body.classList.remove('dark-theme');
            if (themeToggle) themeToggle.classList.remove('dark');
        }
    }
    
    // Saklanan tercihi al veya sistem tercihini kullan
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme) {
        applyTheme(storedTheme);
    } else if (prefersDarkScheme.matches) {
        applyTheme('dark');
    }
    
    // Tema değiştirme düğmesi
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            let currentTheme = 'light';
            
            if (document.body.classList.contains('dark-theme')) {
                document.body.classList.remove('dark-theme');
                themeToggle.classList.remove('dark');
            } else {
                document.body.classList.add('dark-theme');
                themeToggle.classList.add('dark');
                currentTheme = 'dark';
            }
            
            // Tercihi sakla
            localStorage.setItem('theme', currentTheme);
        });
    }
});

// Sayfa yükleme göstergesi
window.addEventListener('load', function() {
    const pageLoader = document.getElementById('page-loader');
    if (pageLoader) {
        pageLoader.classList.add('loaded');
        setTimeout(() => {
            pageLoader.style.display = 'none';
        }, 500);
    }
});

// Sayfa geçişleri için tüm bağlantılara hafif gecikme ekle (opsiyonel)
document.addEventListener('click', function(e) {
    if (e.target.tagName === 'A' && !e.target.classList.contains('no-transition') && !e.target.getAttribute('href').startsWith('#')) {
        e.preventDefault();
        const destination = e.target.href;
        
        document.body.classList.add('page-transition');
        
        setTimeout(() => {
            window.location.href = destination;
        }, 300);
    }
}); 