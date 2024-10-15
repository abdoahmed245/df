import requests
from bs4 import BeautifulSoup
import hashlib
import time
from difflib import unified_diff

# إعدادات بوت تليجرام
TELEGRAM_BOT_TOKEN = '7484302780:AAFoE53mu0b4XjbT-fFy-tj9_68gRDd-b_M'  # ضع توكن البوت هنا
CHAT_ID = '6662346056'  # ضع معرف المحادثة هنا

# URL الصفحة المراد تتبعها
url = 'https://sarhne.sarahah.pro/38633557759051'

# دالة لجلب محتوى الصفحة
def get_page_content(url):
    try:
        # جلب محتوى الصفحة
        response = requests.get(url)
        response.raise_for_status()
        
        # استخدام BeautifulSoup لتحليل HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # تحويل المحتوى إلى نص
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

# حفظ المحتوى الأول للصفحة
initial_content = get_page_content(url)
if initial_content is None:
    print("لم يتمكن من جلب الصفحة في البداية.")
    exit()

# حفظ التجزئة الأولى
initial_hash = calculate_hash(initial_content)

print(f"تم بدأ تتبع الصفحة {url} ...")

# التحقق الدوري من الصفحة
while True:
    time.sleep(10)  # التحقق كل 60 ثانية

    # جلب المحتوى الجديد للصفحة
    current_content = get_page_content(url)

    if current_content is None:
        continue

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
    else:
        print("لا يوجد تغيير في الصفحة.")
