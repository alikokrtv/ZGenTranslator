import os
import json
from flask import Flask, render_template, request, jsonify

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "z-kusagi-translator-secret")

# Initial Z Generation words dictionary
z_words = {
    "güno": "Günaydın",
    "ajg": "Aynen ya, çok iyi",
    "vibe": "Ortam, hava, enerji",
    "sus": "Şüpheli, güvenilmez",
    "fr": "Cidden, gerçekten (for real)",
    "no cap": "Yalan değil, cidden",
    "cringe": "Utanç verici, rahatsız edici",
    "yeet": "Bir şeyi güçlü atmak veya reddetmek",
    "flex": "Hava atmak, gösteriş yapmak",
    "slay": "Çok iyi yapmak, başarılı olmak",
    "ok boomer": "Eski kafalı düşüncelere karşı bir ifade",
    "lit": "Harika, mükemmel",
    "savage": "Acımasız, sert ama havalı",
    "stan": "Fanatik hayran olmak",
    "rizz": "Karşı cinsi etkileme yeteneği",
    "npc": "Sıradan, düşünemeyen insan (non-player character)",
    "gg": "İyi oyun, tebrikler (good game)",
    "bruh": "Abi, dostum (şaşkınlık ifadesi)",
    "ship": "İki kişinin ilişkide olmasını istemek",
    "based": "Kendinden emin, korkmadan fikrini söyleyen"
}

# Route for home page
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to get translation
@app.route('/translate', methods=['POST'])
def translate():
    word = request.form.get('word', '').lower().strip()
    
    if not word:
        return jsonify({
            'success': False,
            'message': 'Lütfen bir kelime girin! 🙏'
        })
    
    if word in z_words:
        return jsonify({
            'success': True,
            'word': word,
            'translation': z_words[word]
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Bu kelimeyi bilmiyorum 😢 Ama sen öğretebilirsin!'
        })

# API endpoint to suggest new word
@app.route('/suggest', methods=['POST'])
def suggest():
    word = request.form.get('word', '').lower().strip()
    meaning = request.form.get('meaning', '').strip()
    name = request.form.get('name', '').strip()
    
    if not word or not meaning:
        return jsonify({
            'success': False,
            'message': 'Kelime ve anlamı zorunludur! 📝'
        })
    
    # Log the suggestion (development stage)
    print(f"Yeni kelime önerisi: '{word}' = '{meaning}' (Öneren: {name if name else 'İsimsiz'})")
    
    # In a real app, you would save this to a database
    # For now, just add it to our in-memory dictionary
    z_words[word] = meaning
    
    return jsonify({
        'success': True,
        'message': 'Teşekkürler! Kelime öneriniz alındı. 🎉'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
