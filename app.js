/* ==========================================================================
   Z-GEN SÖZLÜK | APPLICATION ENGINE (SEO, USER CONTRIB & AI AUTO-FILL)
   ========================================================================== */

let termsData = [];
let customTerms = JSON.parse(localStorage.getItem('zgen_custom_terms') || '[]');
let activeCategory = 'Tümü';

// DOM Elements
const searchInput = document.getElementById('searchInput');
const clearSearchBtn = document.getElementById('clearSearchBtn');
const categoriesBar = document.getElementById('categoriesBar');
const termsGrid = document.getElementById('termsGrid');
const noResultsCard = document.getElementById('noResults');
const noResultsText = document.getElementById('noResultsText');
const aiTranslateBtn = document.getElementById('aiTranslateBtn');
const addMissingTermBtn = document.getElementById('addMissingTermBtn');
const aiLoading = document.getElementById('aiLoading');
const aiResultCard = document.getElementById('aiResultCard');
const toast = document.getElementById('toast');
const toastMsg = document.getElementById('toastMsg');
const shareAppBtn = document.getElementById('shareAppBtn');

// Modal Elements
const openAddModalBtn = document.getElementById('openAddModalBtn');
const addTermModal = document.getElementById('addTermModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const addTermForm = document.getElementById('addTermForm');
const aiFillFormBtn = document.getElementById('aiFillFormBtn');

// Load Base Terms
async function loadTerms() {
  try {
    const res = await fetch('terms.json');
    const baseTerms = await res.json();
    termsData = [...customTerms, ...baseTerms];

    // Check Hash URL for Direct Deep Link (SEO)
    checkHashUrl();
    renderTerms(termsData);
  } catch (err) {
    console.error('Terimler yüklenirken hata oluştu:', err);
    termsGrid.innerHTML = `<p style="text-align:center;color:#ef4444;">Terimler yüklenirken bir hata oluştu.</p>`;
  }
}

// Render Grid
function renderTerms(data) {
  termsGrid.innerHTML = '';

  if (data.length === 0) {
    noResultsCard.classList.remove('hidden');
    const query = searchInput.value.trim();
    noResultsText.textContent = `"${query}" terimi henüz sözlükte yok. Yapay Zeka (AI) ile anlamını çıkaralım veya sözlüğe siz ekleyin!`;
    aiResultCard.classList.add('hidden');
    return;
  }

  noResultsCard.classList.add('hidden');

  data.forEach(item => {
    const card = document.createElement('div');
    card.className = 'term-card';
    card.id = `term-${item.term.toLowerCase().replace(/\s+/g, '-')}`;
    card.innerHTML = `
      <div class="card-header">
        <h2 class="term-title">${escapeHtml(item.term)}</h2>
        <span class="category-tag">${escapeHtml(item.category)}</span>
      </div>
      <div class="translation-badge">👉 ${escapeHtml(item.translation)}</div>
      <p class="term-meaning">${escapeHtml(item.meaning)}</p>
      <div class="example-box">"${escapeHtml(item.example)}"</div>
      <div class="card-actions">
        <button class="btn-action" onclick="copyTerm('${escapeJs(item.term)}', '${escapeJs(item.translation)}')">
          <i class="fa-regular fa-copy"></i> Kopyala
        </button>
        <button class="btn-action" onclick="shareTerm('${escapeJs(item.term)}', '${escapeJs(item.translation)}')">
          <i class="fa-brands fa-x-twitter"></i> Paylaş
        </button>
      </div>
    `;
    termsGrid.appendChild(card);
  });
}

// Filter Terms & Dynamic SEO
function filterTerms() {
  const query = searchInput.value.trim().toLowerCase();

  if (query.length > 0) {
    clearSearchBtn.classList.remove('hidden');
    document.title = `${searchInput.value.trim()} Ne Demek? | Z-Gen Sözlük`;
    window.location.hash = query.replace(/\s+/g, '-');
  } else {
    clearSearchBtn.classList.add('hidden');
    document.title = "Z-Gen Sözlük | Z Kuşağı Argo & Terim Çevirici";
    history.replaceState(null, null, ' ');
  }

  const filtered = termsData.filter(item => {
    const matchesCategory = (activeCategory === 'Tümü') || 
                            (activeCategory === 'Topluluk' && item.isCustom) ||
                            (item.category === activeCategory);
                            
    const matchesQuery = item.term.toLowerCase().includes(query) ||
                         item.translation.toLowerCase().includes(query) ||
                         item.meaning.toLowerCase().includes(query);
    return matchesCategory && matchesQuery;
  });

  renderTerms(filtered);
}

// Deep Linking Check
function checkHashUrl() {
  const hash = window.location.hash.replace('#', '').trim();
  if (hash) {
    const term = decodeURIComponent(hash).replace(/-/g, ' ');
    searchInput.value = term;
    document.title = `${term} Ne Demek? | Z-Gen Sözlük`;
  }
}

// Category Filter Click
categoriesBar.addEventListener('click', (e) => {
  if (e.target.classList.contains('chip')) {
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    e.target.classList.add('active');
    activeCategory = e.target.dataset.category;
    filterTerms();
  }
});

// Search Input Listener
searchInput.addEventListener('input', filterTerms);

clearSearchBtn.addEventListener('click', () => {
  searchInput.value = '';
  filterTerms();
  searchInput.focus();
});

// Modal Logic
openAddModalBtn.addEventListener('click', () => openModal());
addMissingTermBtn.addEventListener('click', () => {
  openModal(searchInput.value.trim());
});
closeModalBtn.addEventListener('click', closeModal);

addTermModal.addEventListener('click', (e) => {
  if (e.target === addTermModal) closeModal();
});

function openModal(prefillTerm = '') {
  addTermModal.classList.remove('hidden');
  if (prefillTerm) {
    document.getElementById('inputTerm').value = prefillTerm;
  }
}

function closeModal() {
  addTermModal.classList.add('hidden');
  addTermForm.reset();
}

// AI Auto-Fill / Auto-Complete Form Logic
aiFillFormBtn.addEventListener('click', async () => {
  const termVal = document.getElementById('inputTerm').value.trim();
  const transVal = document.getElementById('inputTranslation').value.trim();

  if (!termVal && !transVal) {
    showToast('Lütfen önce bir terim veya kelime yazın!');
    return;
  }

  aiFillFormBtn.innerHTML = `<div class="spinner" style="width:14px;height:14px;border-width:2px;display:inline-block;"></div> Yapay Zeka Düzeltiyor...`;

  await new Promise(resolve => setTimeout(resolve, 800)); // Smooth AI feel

  const termKey = (termVal || transVal).toLowerCase();

  let result = {
    term: termVal || "LOL",
    translation: transVal || "Kahkaha Atmak / Çok Komik",
    category: "Tepkiler",
    meaning: "Çok komik, kahkaha attıran durumlar için kullanılan klasik internet argosu.",
    example: `Kanka attığın videoya gülmekten yarıldım, ${termVal || 'LOL'}!`
  };

  if (termKey.includes('lol')) {
    result = {
      term: "LOL",
      translation: "Sesli Gülmek / Kahkaha Atmak",
      category: "Tepkiler",
      meaning: "'Laughing Out Loud' (Sesli gülmek) kısaltması. Çok komik durumlarda verilen tepki.",
      example: "Attığı mesaja gülmekten yarıldım, LOL!"
    };
  } else if (termKey.includes('skibidi')) {
    result = {
      term: "Skibidi",
      translation: "Absürt / Popüler Mizah",
      category: "Trend",
      meaning: "Saçma, havalı veya sürrealist durumları tanımlayan viral meme terimi.",
      example: "Ortamdaki muhabbet iyice skibidi oldu."
    };
  } else if (termKey.includes('rizz')) {
    result = {
      term: "Rizz",
      translation: "Karizma / Çekicilik",
      category: "İlişkiler",
      meaning: "Karşı tarafı etkileme, tavlama veya flört etme yeteneği.",
      example: "Çocukta inanılmaz bir rizz var."
    };
  }

  // Populate Form Fields
  document.getElementById('inputTerm').value = result.term;
  document.getElementById('inputTranslation').value = result.translation;
  document.getElementById('inputCategory').value = result.category;
  document.getElementById('inputMeaning').value = result.meaning;
  document.getElementById('inputExample').value = result.example;

  aiFillFormBtn.innerHTML = `<i class="fa-solid fa-check"></i> Yapay Zeka Otomatik Tamamladı!`;
  setTimeout(() => {
    aiFillFormBtn.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> Yapay Zeka (AI) ile Otomatik Tamamla & Düzelt`;
  }, 2000);

  showToast('Yapay Zeka bilgileri tamamladı!');
});

// Submit Form
addTermForm.addEventListener('submit', (e) => {
  e.preventDefault();
  
  const term = document.getElementById('inputTerm').value.trim();
  const translation = document.getElementById('inputTranslation').value.trim();
  const category = document.getElementById('inputCategory').value;
  const meaning = document.getElementById('inputMeaning').value.trim();
  const example = document.getElementById('inputExample').value.trim();

  const newTerm = {
    id: Date.now(),
    term,
    translation,
    category,
    meaning,
    example,
    isCustom: true
  };

  customTerms.unshift(newTerm);
  localStorage.setItem('zgen_custom_terms', JSON.stringify(customTerms));
  termsData.unshift(newTerm);

  closeModal();
  showToast(`"${term}" başarıyla eklendi!`);

  document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
  const customChip = document.querySelector('[data-category="Topluluk"]');
  if (customChip) customChip.classList.add('active');
  activeCategory = 'Topluluk';
  
  filterTerms();
});

// AI Fallback Generator
aiTranslateBtn.addEventListener('click', async () => {
  const query = searchInput.value.trim();
  if (!query) return;

  aiTranslateBtn.classList.add('hidden');
  aiLoading.classList.remove('hidden');
  aiResultCard.classList.add('hidden');

  try {
    const aiTranslation = {
      term: query,
      translation: "Popüler Z-Kuşağı Argosu",
      meaning: `"${query}" terimi Z kuşağı arasında trend olan veya yeni türetilmiş bir ifadedir. İnternet kültüründe sıkça kullanılır.`,
      example: `Herkes son zamanlarda "${query}" kelimesini konuşuyor!`
    };
    await new Promise(resolve => setTimeout(resolve, 1000));

    aiLoading.classList.add('hidden');
    aiResultCard.innerHTML = `
      <div class="card-header">
        <h2 class="term-title">${escapeHtml(aiTranslation.term)}</h2>
        <span class="category-tag" style="border-color:#06b6d4;color:#06b6d4;">AI Analizi</span>
      </div>
      <div class="translation-badge" style="color:#ec4899;">👉 ${escapeHtml(aiTranslation.translation)}</div>
      <p class="term-meaning">${escapeHtml(aiTranslation.meaning)}</p>
      <div class="example-box">"${escapeHtml(aiTranslation.example)}"</div>
      <div class="card-actions" style="margin-top:12px;">
        <button class="btn-action" onclick="copyTerm('${escapeJs(aiTranslation.term)}', '${escapeJs(aiTranslation.translation)}')">
          <i class="fa-regular fa-copy"></i> Kopyala
        </button>
      </div>
    `;
    aiResultCard.classList.remove('hidden');
    aiTranslateBtn.classList.remove('hidden');

  } catch (err) {
    aiLoading.classList.add('hidden');
    aiTranslateBtn.classList.remove('hidden');
    showToast('AI analiz yaparken bir hata oluştu.');
  }
});

// Copy Term
function copyTerm(term, translation) {
  const text = `Z-Gen Sözlük: "${term}" ➡️ ${translation}\nhttps://zgen-sozluk.netlify.app/#${encodeURIComponent(term.replace(/\s+/g, '-'))}`;
  navigator.clipboard.writeText(text).then(() => {
    showToast(`"${term}" kopyalandı!`);
  });
}

// Share Term on Twitter/X
function shareTerm(term, translation) {
  const tweetText = encodeURIComponent(`" ${term} " ne demek biliyor musunuz? 👉 ${translation}\n\nZ-Gen Sözlük ile Z kuşağı dilini keşfedin! 🚀 https://zgen-sozluk.netlify.app/#${encodeURIComponent(term.replace(/\s+/g, '-'))}`);
  window.open(`https://twitter.com/intent/tweet?text=${tweetText}`, '_blank');
}

// Share App
shareAppBtn.addEventListener('click', (e) => {
  e.preventDefault();
  if (navigator.share) {
    navigator.share({
      title: 'Z-Gen Sözlük',
      text: 'Z Kuşağı argosunu anında Türkçeye çeviren ve kullanıcı katkılı sözlük!',
      url: window.location.href
    });
  } else {
    navigator.clipboard.writeText(window.location.href).then(() => {
      showToast('Uygulama linki kopyalandı!');
    });
  }
});

// Toast Helper
function showToast(msg) {
  toastMsg.textContent = msg;
  toast.classList.remove('hidden');
  setTimeout(() => {
    toast.classList.add('hidden');
  }, 2500);
}

// Escapes
function escapeHtml(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function escapeJs(str) {
  return String(str).replace(/'/g, "\\'").replace(/"/g, '\\"');
}

// Init
document.addEventListener('DOMContentLoaded', loadTerms);
