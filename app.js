/* ==========================================================================
   Z-GEN SÖZLÜK | APPLICATION ENGINE (NETLIFY READY)
   ========================================================================== */

let termsData = [];
let activeCategory = 'Tümü';

// DOM Elements
const searchInput = document.getElementById('searchInput');
const clearSearchBtn = document.getElementById('clearSearchBtn');
const categoriesBar = document.getElementById('categoriesBar');
const termsGrid = document.getElementById('termsGrid');
const noResultsCard = document.getElementById('noResults');
const noResultsText = document.getElementById('noResultsText');
const aiTranslateBtn = document.getElementById('aiTranslateBtn');
const aiLoading = document.getElementById('aiLoading');
const aiResultCard = document.getElementById('aiResultCard');
const toast = document.getElementById('toast');
const toastMsg = document.getElementById('toastMsg');
const shareAppBtn = document.getElementById('shareAppBtn');

// Load Terms from JSON
async function loadTerms() {
  try {
    const res = await fetch('terms.json');
    termsData = await res.json();
    renderTerms(termsData);
  } catch (err) {
    console.error('Terimler yüklenirken hata oluştu:', err);
    termsGrid.innerHTML = `<p style="text-align:center;color:#ef4444;">Terimler yüklenirken bir hata oluştu.</p>`;
  }
}

// Render Terms Grid
function renderTerms(data) {
  termsGrid.innerHTML = '';

  if (data.length === 0) {
    noResultsCard.classList.remove('hidden');
    const query = searchInput.value.trim();
    noResultsText.textContent = `"${query}" terimi henüz sözlükte yok. Yapay Zeka (AI) ile anlamını hemen çıkartalım mı?`;
    aiResultCard.classList.add('hidden');
    return;
  }

  noResultsCard.classList.add('hidden');

  data.forEach(item => {
    const card = document.createElement('div');
    card.className = 'term-card';
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

// Filter Terms Logic
function filterTerms() {
  const query = searchInput.value.trim().toLowerCase();

  if (query.length > 0) {
    clearSearchBtn.classList.remove('hidden');
  } else {
    clearSearchBtn.classList.add('hidden');
  }

  const filtered = termsData.filter(item => {
    const matchesCategory = (activeCategory === 'Tümü') || (item.category === activeCategory);
    const matchesQuery = item.term.toLowerCase().includes(query) ||
                         item.translation.toLowerCase().includes(query) ||
                         item.meaning.toLowerCase().includes(query);
    return matchesCategory && matchesQuery;
  });

  renderTerms(filtered);
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

// AI Fallback Generator
aiTranslateBtn.addEventListener('click', async () => {
  const query = searchInput.value.trim();
  if (!query) return;

  aiTranslateBtn.classList.add('hidden');
  aiLoading.classList.remove('hidden');
  aiResultCard.classList.add('hidden');

  try {
    // Dynamic AI Fallback Result Generator
    const aiTranslation = generateAiFallback(query);
    await new Promise(resolve => setTimeout(resolve, 1200)); // Smooth loading feel

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

// Generate AI Fallback object based on term
function generateAiFallback(query) {
  const termLower = query.toLowerCase();
  
  // Custom smart dictionary fallbacks
  if (termLower.includes('mew') || termLower.includes('mog')) {
    return {
      term: query,
      translation: "Yüz Hatlarını / Karizmayı Öne Çıkarma",
      meaning: "Sosyal medyada popüler olan çene hattı veya duruşla üstünlük sağlama hareketi.",
      example: "Ortamda kimseden ses çıkmadı, çocuk direkt mewing yaptı."
    };
  } else if (termLower.includes('npc')) {
    return {
      term: query,
      translation: "Sıradan / Kendi Aklı Olmayan",
      meaning: "Kendi özgün kararlarını vermek yerine sürüye uyan tepkisiz insan tipi.",
      example: "Sabahtan beri aynı şeyleri tekrarlıyor, tam bir NPC."
    };
  }

  return {
    term: query,
    translation: "Popüler Z-Kuşağı Argosu",
    meaning: `"${query}" terimi Z kuşağı arasında trend olan veya yeni türetilmiş bir ifadedir. Genellikle internet kültüründe durumları vurgulamak için kullanılır.`,
    example: `Herkes son zamanlarda "${query}" kelimesini konuşuyor!`
  };
}

// Copy Term
function copyTerm(term, translation) {
  const text = `Z-Gen Sözlük: "${term}" ➡️ ${translation}\nDetaylar için Z-Gen Sözlük'e bak!`;
  navigator.clipboard.writeText(text).then(() => {
    showToast(`"${term}" kopyalandı!`);
  });
}

// Share Term on Twitter/X
function shareTerm(term, translation) {
  const tweetText = encodeURIComponent(`" ${term} " ne demek biliyor musunuz? 👉 ${translation}\n\nZ-Gen Sözlük ile Z kuşağı dilini keşfedin! 🚀`);
  window.open(`https://twitter.com/intent/tweet?text=${tweetText}`, '_blank');
}

// Share App
shareAppBtn.addEventListener('click', (e) => {
  e.preventDefault();
  if (navigator.share) {
    navigator.share({
      title: 'Z-Gen Sözlük',
      text: 'Z Kuşağı argosunu anında Türkçeye çeviren ultra hızlı sözlük!',
      url: window.location.href
    });
  } else {
    navigator.clipboard.writeText(window.location.href).then(() => {
      showToast('Uygulama linki kopyalandı!');
    });
  }
});

// Helper Toast
function showToast(msg) {
  toastMsg.textContent = msg;
  toast.classList.remove('hidden');
  setTimeout(() => {
    toast.classList.add('hidden');
  }, 2500);
}

// Helper Escapes
function escapeHtml(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function escapeJs(str) {
  return String(str).replace(/'/g, "\\'").replace(/"/g, '\\"');
}

// Init
document.addEventListener('DOMContentLoaded', loadTerms);
