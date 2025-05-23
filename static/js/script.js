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
    
    // Popular words to display as chips (same as in the backend)
    const popularWords = [
        "güno", "ajg", "vibe", "sus", "fr", "no cap", "cringe", "yeet", 
        "flex", "slay", "lit", "savage"
    ];
    
    // Initialize word chips
    function initializeWordChips() {
        popularWords.forEach(word => {
            const chip = document.createElement('div');
            chip.className = 'word-chip';
            chip.textContent = word;
            chip.addEventListener('click', () => {
                wordInput.value = word;
                translateForm.dispatchEvent(new Event('submit'));
            });
            wordChipsContainer.appendChild(chip);
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
                // Show translation result
                resultContainer.innerHTML = `
                    <div class="translation-result">
                        <h3>"${data.word}" kelimesinin anlamı:</h3>
                        <p>${data.translation}</p>
                        <div class="result-emoji">✨</div>
                    </div>
                `;
            } else {
                // Show error message
                resultContainer.innerHTML = `
                    <div class="translation-result">
                        <h3>${data.message}</h3>
                        <p>Aşağıdaki formdan yeni kelime önerebilirsin.</p>
                        <div class="result-emoji">👇</div>
                    </div>
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
});
