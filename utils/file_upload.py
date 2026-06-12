import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

# تعریف پسوندهای مجاز برای امنیت
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'doc', 'docx'}
IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    """بررسی می‌کند که آیا پسوند فایل مجاز است یا خیر"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_social_media(files):
    """
    آپلود فایل‌های رسانه‌ای و دسته‌بندی آن‌ها به تصاویر و اسناد.
    :param files: لیست فایل‌های دریافتی از request.files.getlist('media_files')
    :return: دیکشنری با ساختار {'images': [], 'files': []} مطابق با مدل Post
    """
    # ساختار خروجی دقیقاً منطبق با فیلد media در مدل Post
    media_data = {'images': [], 'files': []}

    # دریافت مسیر از کانفیگ یا استفاده از مسیر پیش‌فرض
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads/social')
    absolute_upload_path = os.path.join(current_app.root_path, upload_folder)

    # اطمینان از وجود پوشه مقصد
    os.makedirs(absolute_upload_path, exist_ok=True)

    for file in files:
        # بررسی اینکه فایل واقعاً وجود دارد و نام دارد
        if file and file.filename != '':
            if not allowed_file(file.filename):
                # اگر فایل مجاز نبود، آن را نادیده می‌گیریم (یا می‌توانید Error برگردانید)
                continue

            # استخراج پسوند اصلی و ساخت نام یکتا با UUID برای جلوگیری از تداخل
            original_ext = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{original_ext}"

            # مسیر کامل ذخیره‌سازی در سرور
            file_path = os.path.join(absolute_upload_path, unique_filename)

            # ذخیره فایل
            file.save(file_path)

            # ساخت URL نسبی برای ذخیره در دیتابیس و نمایش در فرانت‌اند
            # مثال خروجی: /static/uploads/social/a1b2c3d4.jpg
            file_url = f"/{upload_folder}/{unique_filename}"

            # دسته‌بندی فایل بر اساس پسوند
            if original_ext in IMAGE_EXTENSIONS:
                media_data['images'].append(file_url)
            else:
                media_data['files'].append(file_url)

    return media_data