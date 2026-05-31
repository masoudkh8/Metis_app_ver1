# راهنمای استفاده از Tailwind CSS بدون CDN

## مشکل قبلی
استفاده از `cdn.tailwindcss.com` باعث کندی لود سایت و وابستگی به اینترنت می‌شد.

## راه‌حل
اکنون از فایل CSS محلی (`output.css`) استفاده می‌شود که با Tailwind CSS v4 ساخته شده است.

## فایل‌های مهم

### 1. `static/css/input.css`
فایل ورودی Tailwind که تم سفارشی شما را تعریف می‌کند:
```css
@import "tailwindcss";

@theme {
  --font-sans: Tahoma, sans-serif;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  --color-dark-900: #0f172a;
  --color-dark-800: #1e293b;
  --color-dark-700: #334155;
}
```

### 2. `static/css/output.css`
فایل CSS نهایی که باید در HTML لینک شود (تولید خودکار).

### 3. `build_tailwind.py`
اسکریپت پایتون برای ساخت فایل output.css:
```bash
python build_tailwind.py
```

### 4. `templates/base_pwa.html`
الگوی پایه که فقط از فایل محلی استفاده می‌کند:
```html
<link href="{{ url_for('static', filename='css/output.css') }}" rel="stylesheet">
```

## نحوه استفاده

### هر بار که کلاس‌های Tailwind را تغییر می‌دهید:
```bash
# روش 1: با پایتون
python build_tailwind.py

# روش 2: مستقیم با npx
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify
```

### افزودن کلاس‌های جدید به input.css
اگر به رنگ‌ها یا فونت‌های جدید نیاز دارید، آن‌ها را به بخش `@theme` در `input.css` اضافه کنید:
```css
@theme {
  --color-custom-500: #your-color;
  --font-custom: YourFont, sans-serif;
}
```

سپس دوباره build کنید.

## مزایا
- ✅ سرعت لود بالاتر (بدون وابستگی به CDN)
- ✅ کار آفلاین
- ✅ حجم کمتر (فقط کلاس‌های استفاده شده)
- ✅ کنترل کامل روی تم

## نکات مهم
1. فایل `output.css` باید بعد از هر تغییر در کلاس‌های Tailwind دوباره ساخته شود
2. فایل `tailwind.config.js` حذف شده چون در v4 از `@theme` در CSS استفاده می‌شود
3. تمام تنظیمات custom (فونت Tahoma، رنگ‌های primary و dark) در `input.css` تعریف شده‌اند
