import requests
from bs4 import BeautifulSoup
import hashlib
import time
from difflib import unified_diff
from flask import Flask, jsonify

app = Flask(name)

# إعدادات بوت تليجرام
TELEGRAM_BOT_TOKEN = '7484302780:AAFoE53mu0b4XjbT-fFy-tj9_68gRDd-b_M'  # ضع توكن البوت هنا
CHAT_ID = '6662346056'  # ضع معرف المحادثة هنا

# URL الصفحة المراد تتبعها
url = 'https://sarhne.sarahah.pro/38633557759051'

# دالة لجلب محتوى الصفحة
def get_page_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        page_content = soup.get_text()
        return page_content
    except requests.exceptions.RequestException as e:
        print(f"حدث خطأ: {e}")
        return None

# دالة لحساب تجزئة النص
def calculate_hash(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

# دالة لإرسال رسالة عبر بوت تليجرام
def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'  # يمكنك استخدام Markdown لتنسيق الرسالة
    }
    requests.post(url, json=payload)

@app.route('/track', methods=['GET'])
def track_page():
    # حفظ المحتوى الأول للصفحة
    initial_content = get_page_content(url)
    if initial_content is None:
        return jsonify({"error": "لم يتمكن من جلب الصفحة في البداية."}), 500

    # حفظ التجزئة الأولى
    initial_hash = calculate_hash(initial_content)
    
    print(f"تم بدأ تتبع الصفحة {url} ...")

    # التحقق الدوري من الصفحة (لن يتم استخدام loop في Vercel، لذا سنقوم بتنفيذ التحقق لمرة واحدة هنا)
    time.sleep(7)  # الانتظار 4 ثواني (يمكنك تعديل الزمن)

    # جلب المحتوى الجديد للصفحة
    current_content = get_page_content(url)
    if current_content is None:
        return jsonify({"error": "حدث خطأ أثناء جلب المحتوى الجديد."}), 500

    # حساب التجزئة الجديدة
    current_hash = calculate_hash(current_content)

    # مقارنة التجزئة الجديدة مع التجزئة السابقة
    if current_hash != initial_hash:
        print("تم اكتشاف تغيير في الصفحة!")

        # عرض الفرق بين المحتويين
        diff = unified_diff(initial_content.splitlines(), current_content.splitlines(), lineterm='', fromfile='Old Content', tofile='New Content')
        diff_text = "\n".join(diff)
        print(diff_text)

        # إرسال رسالة إلى تليجرام
        send_telegram_message(f"تم اكتشاف تغيير في الصفحة: {url}\n\n{diff_text}")

        # تحديث المحتوى والتجزئة السابقين
        initial_content = current_content
        initial_hash = current_hash
        return jsonify({"message": "تم اكتشاف تغيير في الصفحة!"}), 200
    else:
        print("لا يوجد تغيير في الصفحة.")
        return jsonify({"message": "لا يوجد تغيير في الصفحة."}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
