/**
 * Z Kuşağı Çevirici - Oylama ve Düzenleme Önerisi İşlevleri
 */

document.addEventListener('DOMContentLoaded', function() {
    // Oylama butonları için işlevsellik
    setupVotingButtons();
    
    // Düzenleme öner butonları için işlevsellik
    setupEditRequestButtons();
});

// Oylama işlevselliği
function setupVotingButtons() {
    const voteButtons = document.querySelectorAll('.vote-btn');
    
    voteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const meaningId = this.getAttribute('data-id');
            const voteType = this.getAttribute('data-vote');
            const voteForm = new FormData();
            
            voteForm.append('meaning_id', meaningId);
            voteForm.append('vote_type', voteType);
            
            // Oy verme isteği gönder
            fetch('/vote', {
                method: 'POST',
                body: voteForm,
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Oy sayılarını güncelle
                    const meaningCard = button.closest('.meaning-item');
                    const upvoteCount = meaningCard.querySelector('.upvote-count');
                    const downvoteCount = meaningCard.querySelector('.downvote-count');
                    
                    if (upvoteCount) upvoteCount.textContent = data.upvotes;
                    if (downvoteCount) downvoteCount.textContent = data.downvotes;
                    
                    // Aktif buton stilini uygula
                    if (voteType === 'up') {
                        button.classList.add('voted');
                        const downButton = meaningCard.querySelector('.vote-btn[data-vote="down"]');
                        if (downButton) downButton.classList.remove('voted');
                    } else {
                        button.classList.add('voted');
                        const upButton = meaningCard.querySelector('.vote-btn[data-vote="up"]');
                        if (upButton) upButton.classList.remove('voted');
                    }
                    
                    // Bildirim göster
                    showNotification('Oyunuz kaydedildi.', 'success');
                } else {
                    showNotification(data.message || 'Oy verilirken bir hata oluştu.', 'error');
                }
            })
            .catch(error => {
                console.error('Oy verme hatası:', error);
                showNotification('Bir bağlantı hatası oluştu.', 'error');
            });
        });
    });
}

// Düzenleme önerisi işlevselliği
function setupEditRequestButtons() {
    const editButtons = document.querySelectorAll('.edit-request-btn');
    
    editButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const wordId = this.getAttribute('data-id');
            window.location.href = `/request-edit/${wordId}`;
        });
    });
}

// Bildirim gösterme işlevi
function showNotification(message, type = 'info') {
    // Eğer sayfada bir bildirim konteynerı yoksa oluştur
    let notificationContainer = document.getElementById('dynamic-notifications');
    
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'dynamic-notifications';
        notificationContainer.style.position = 'fixed';
        notificationContainer.style.top = '20px';
        notificationContainer.style.right = '20px';
        notificationContainer.style.zIndex = '9999';
        document.body.appendChild(notificationContainer);
    }
    
    // Yeni bildirim oluştur
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.style.opacity = '0';
    notification.style.transform = 'translateY(-20px)';
    notification.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    
    notification.innerHTML = `
        <div class="notification-content">
            <p class="notification-message">${message}</p>
        </div>
        <button class="notification-close" onclick="this.parentNode.remove()">×</button>
    `;
    
    notificationContainer.appendChild(notification);
    
    // Animasyon için gecikmeli göster
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateY(0)';
    }, 10);
    
    // 5 saniye sonra kaldır
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}
