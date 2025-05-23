document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const translateForm = document.getElementById('translate-form');
    const wordInput = document.getElementById('word-input');
    const resultContainer = document.getElementById('result-container');
    const suggestionForm = document.getElementById('suggestion-form');
    const suggestWordInput = document.getElementById('suggest-word');
    const suggestMeaningInput = document.getElementById('suggest-meaning');
    const suggestNameInput = document.getElementById('suggest-name');
    const notification = document.getElementById('notification');
    const notificationMessage = document.querySelector('.notification-message');
    const notificationClose = document.querySelector('.notification-close');
    const wordChipsContainer = document.getElementById('word-chips');
    
    // Kullanıcının giriş yapıp yapmadığını kontrol et
    let userLoggedIn = document.body.dataset.userLoggedIn === 'true';
    
    // Will fetch popular words from the backend
    let popularWords = [];
    
    // Initialize word chips
    function initializeWordChips() {
        // Clear existing chips
        wordChipsContainer.innerHTML = '';
        
        // Fetch popular words from the backend
        fetch('/popular')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.words) {
                    // Create chips for each word
                    data.words.forEach(wordObj => {
                        const chip = document.createElement('div');
                        chip.className = 'word-chip';
                        chip.textContent = wordObj.word;
                        chip.addEventListener('click', () => {
                            wordInput.value = wordObj.word;
                            translateForm.dispatchEvent(new Event('submit'));
                        });
                        wordChipsContainer.appendChild(chip);
                    });
                } else {
                    console.error('Failed to load popular words');
                }
            })
            .catch(error => {
                console.error('Error fetching popular words:', error);
            });
    }
    
    // Translation form submission
    translateForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const word = wordInput.value.trim();
        
        if (!word) {
            showNotification('Lütfen bir kelime girin! 🙏', 'error');
            return;
        }
        
        // Create form data
        const formData = new FormData();
        formData.append('word', word);
        
        // Send request to translate endpoint
        fetch('/translate', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show translation result with multiple meanings
                document.getElementById('translation-result').style.display = 'block';
                document.getElementById('result-word').textContent = `"${data.word}" kelimesinin anlamları:`;
                
                const meaningsContainer = document.getElementById('translation-meanings');
                meaningsContainer.innerHTML = ''; // Clear previous meanings
                
                if (data.meanings.length === 0) {
                    // No meanings found
                    meaningsContainer.innerHTML = `
                        <div class="meaning-item">
                            <p class="meaning-content">Bu kelime için henüz onaylanmış bir anlam bulunmuyor.</p>
                        </div>
                    `;
                } else {
                    // Display each meaning
                    data.meanings.forEach(meaning => {
                        const meaningItem = document.createElement('div');
                        meaningItem.className = 'meaning-item';
                        
                        // Create content for the meaning
                        meaningItem.innerHTML = `
                            <div class="edit-button-wrapper"></div>
                            <p class="meaning-content">${meaning.meaning}</p>
                            <div class="meaning-meta">
                                <div class="meaning-contributor">
                                    <i class="fas fa-user"></i>
                                    <span>${meaning.contributor || 'Anonim'}</span>
                                </div>
                                <div class="meaning-votes">
                                    <button class="vote-btn vote-up" data-word-id="${meaning.id}" data-vote-type="up">
                                        <i class="fas fa-thumbs-up"></i> ${meaning.votes_up || 0}
                                    </button>
                                    <button class="vote-btn vote-down" data-word-id="${meaning.id}" data-vote-type="down">
                                        <i class="fas fa-thumbs-down"></i> ${meaning.votes_down || 0}
                                    </button>
                                </div>
                            </div>
                        `;
                        
                        // Add edit request button if user is logged in
                        if (data.user_logged_in) {
                            const editButton = document.createElement('button');
                            editButton.className = 'edit-request-btn';
                            editButton.innerHTML = '<i class="fas fa-edit"></i> Düzenleme Öner';
                            editButton.dataset.wordId = meaning.id;
                            editButton.addEventListener('click', () => openEditRequestModal(meaning.id, meaning.meaning));
                            meaningItem.querySelector('.edit-button-wrapper').appendChild(editButton);
                        }
                        
                        meaningsContainer.appendChild(meaningItem);
                    });
                    
                    // Add event listeners for voting buttons
                    document.querySelectorAll('.vote-btn').forEach(button => {
                        button.addEventListener('click', handleVote);
                    });
                }
                
                // Show the result container
                resultContainer.querySelector('.result-placeholder').style.display = 'none';
            } else {
                // Show error message
                document.getElementById('translation-result').style.display = 'none';
                resultContainer.querySelector('.result-placeholder').style.display = 'block';
                
                resultContainer.querySelector('.result-placeholder').innerHTML = `
                    <h3>${data.message}</h3>
                    <p>Aşağıdaki formdan yeni kelime önerebilirsin.</p>
                    <div class="result-emoji">👇</div>
                `;
                
                // Auto-fill the suggestion form
                suggestWordInput.value = word;
                suggestWordInput.focus();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Bir hata oluştu. Lütfen tekrar deneyin.', 'error');
        });
    });
    
    // Suggestion form submission
    suggestionForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const word = suggestWordInput.value.trim();
        const meaning = suggestMeaningInput.value.trim();
        const name = suggestNameInput.value.trim();
        
        if (!word || !meaning) {
            showNotification('Kelime ve anlamı zorunludur!', 'error');
            return;
        }
        
        // Create form data
        const formData = new FormData();
        formData.append('word', word);
        formData.append('meaning', meaning);
        formData.append('name', name);
        
        // Send request to suggest endpoint
        fetch('/suggest', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                
                // Clear form
                suggestionForm.reset();
                
                // If user searched for this word, show the translation now
                if (wordInput.value.toLowerCase().trim() === word.toLowerCase()) {
                    translateForm.dispatchEvent(new Event('submit'));
                }
            } else {
                showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Bir hata oluştu. Lütfen tekrar deneyin.', 'error');
        });
    });
    
    // Show notification
    function showNotification(message, type) {
        notificationMessage.textContent = message;
        notification.className = 'notification show ' + type;
        
        // Auto hide after 5 seconds
        setTimeout(() => {
            hideNotification();
        }, 5000);
    }
    
    // Hide notification
    function hideNotification() {
        notification.className = 'notification';
    }
    
    // Close notification on click
    notificationClose.addEventListener('click', hideNotification);
    
    // Initialize word chips
    initializeWordChips();
    
    // Oylama işlevi
    function handleVote(e) {
        e.preventDefault();
        
        const wordId = this.dataset.wordId;
        const voteType = this.dataset.voteType;
        
        // Giriş yapılmamışsa, giriş yapmaya yönlendir
        if (!userLoggedIn) {
            showNotification('Oy vermek için giriş yapmalısınız.', 'error');
            setTimeout(() => {
                window.location.href = '/login';
            }, 1500);
            return;
        }
        
        // Kullanıcı girişi yapmış
        fetch(`/vote/${wordId}/${voteType}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin' // Oturum bilgilerini gönder
        })
        .then(response => {
            // JSON olmayan yanıtları kontrol et
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('Oturum zaman aşımına uğradı. Lütfen tekrar giriş yapın.');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                // Kullanıcının oy verdiğini göstermek için butonu güncelle
                this.classList.add('voted');
                // Oy sayısını güncelle
                const voteCount = parseInt(this.innerText.trim().split(' ')[1] || '0') + 1;
                this.querySelector('i').innerHTML = ''; // Önce içeriği temizle
                this.querySelector('i').insertAdjacentHTML('afterend', ` ${voteCount}`);
            } else {
                showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Oylama hatası:', error);
            showNotification(error.message || 'Bir hata oluştu. Lütfen tekrar deneyin.', 'error');
        });
    }
    
    // Düzenleme talebi modalı
    function createEditRequestModal() {
        // Modal HTML'i oluştur
        const modalHTML = `
        <div id="editRequestModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Kelime Düzenleme Talebi</h2>
                    <span class="close">&times;</span>
                </div>
                <div class="modal-body">
                    <form id="editRequestForm">
                        <input type="hidden" id="edit-word-id">
                        <div class="form-group">
                            <label for="current-meaning">Mevcut Anlam:</label>
                            <div id="current-meaning" class="readonly-field"></div>
                        </div>
                        <div class="form-group">
                            <label for="new-meaning">Önerilen Yeni Anlam:</label>
                            <textarea id="new-meaning" required></textarea>
                        </div>
                        <div class="form-group">
                            <label for="edit-reason">Değişiklik Gerekçesi (Opsiyonel):</label>
                            <textarea id="edit-reason"></textarea>
                        </div>
                        <div class="form-actions">
                            <button type="button" class="secondary-btn" id="cancel-edit">İptal</button>
                            <button type="submit" class="primary-btn">Gönder</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        `;
        
        // Modal'ı body'nin sonuna ekle
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Modal elementlerine olay dinleyicileri ekle
        const modal = document.getElementById('editRequestModal');
        const closeBtn = modal.querySelector('.close');
        const cancelBtn = document.getElementById('cancel-edit');
        const editForm = document.getElementById('editRequestForm');
        
        // Modal'ı kapat
        function closeModal() {
            modal.style.display = 'none';
        }
        
        // Kapatma düğmesi tıklandığında modal'ı kapat
        closeBtn.addEventListener('click', closeModal);
        cancelBtn.addEventListener('click', closeModal);
        
        // Modal dışına tıklandığında kapat
        window.addEventListener('click', (event) => {
            if (event.target === modal) {
                closeModal();
            }
        });
        
        // Form gönderildiğinde işle
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const wordId = document.getElementById('edit-word-id').value;
            const newMeaning = document.getElementById('new-meaning').value.trim();
            const reason = document.getElementById('edit-reason').value.trim();
            
            if (!newMeaning) {
                showNotification('Yeni anlam zorunludur!', 'error');
                return;
            }
            
            // Form verilerini oluştur
            const formData = new FormData();
            formData.append('new_meaning', newMeaning);
            formData.append('reason', reason);
            
            // Düzenleme talebi gönder
            fetch(`/request-edit/${wordId}`, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');
                    closeModal();
                } else {
                    showNotification(data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Düzenleme talebi hatası:', error);
                showNotification('Bir hata oluştu. Lütfen tekrar deneyin.', 'error');
            });
        });
        
        return modal;
    }
    
    // Modal'ı oluştur ve özelliklerini ayarla
    let editRequestModal;
    
    function openEditRequestModal(wordId, currentMeaning) {
        // Eğer modal henüz oluşturulmadıysa oluştur
        if (!editRequestModal) {
            editRequestModal = createEditRequestModal();
        }
        
        // Modal alanlarını doldur
        document.getElementById('edit-word-id').value = wordId;
        document.getElementById('current-meaning').textContent = currentMeaning;
        document.getElementById('new-meaning').value = currentMeaning;
        document.getElementById('edit-reason').value = '';
        
        // Modal'ı göster
        editRequestModal.style.display = 'block';
    }
});
