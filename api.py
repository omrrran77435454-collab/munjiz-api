# api.py

# استيراد Flask ومكتبات التلخيص
from flask import Flask, request, jsonify
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import heapq

# إنشاء تطبيق Flask
app = Flask(__name__)

# --- دالة التلخيص (نفس منطق الكود السابق) ---
def summarize_text(text, num_sentences=3):
    # 1. تقسيم النص إلى جمل
    sentences = sent_tokenize(text)

    # 2. حساب تكرار الكلمات المهمة
    stop_words = set(stopwords.words("english"))
    word_frequencies = {}
    for word in word_tokenize(text):
        if word.lower() not in stop_words and word.isalpha():
            if word not in word_frequencies:
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1
    
    if not word_frequencies:
        return "Could not summarize the text. Not enough significant words."

    # 3. توحيد أوزان الكلمات
    maximum_frequency = max(word_frequencies.values())
    for word in word_frequencies:
        word_frequencies[word] = (word_frequencies[word] / maximum_frequency)

    # 4. تقييم الجمل
    sentence_scores = {}
    for sent in sentences:
        for word in word_tokenize(sent.lower()):
            if word in word_frequencies:
                if len(sent.split(' ')) < 30:
                    if sent not in sentence_scores:
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]
    
    if not sentence_scores:
        return "Could not score any sentences. Text might be too short or simple."

    # 5. الحصول على أفضل الجمل
    summary_sentences = heapq.nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
    summary = ' '.join(summary_sentences)
    return summary

# --- إنشاء نقطة الوصول (Endpoint) للـ API ---
# هذا هو الرابط الذي سيتصل به تطبيق الأندرويد
@app.route('/summarize', methods=['POST'])
def handle_summarize():
    # الحصول على البيانات التي أرسلها التطبيق (النص)
    data = request.get_json()
    
    # التحقق من وجود النص
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing text in request'}), 400
    
    text_to_summarize = data['text']
    
    # استدعاء دالة التلخيص
    summary_result = summarize_text(text_to_summarize)
    
    # إرجاع الملخص إلى التطبيق
    return jsonify({'summary': summary_result})

# --- تشغيل السيرفر ---
if __name__ == '__main__':
    app.run(debug=True)
