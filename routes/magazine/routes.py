# routes/magazine/routes.py
from flask import render_template, request, redirect, url_for, flash, send_from_directory, current_app
from . import magazine_bp
from models import db, MagazineIssue, SponsorshipRequest, AdvertisementRequest, Subscription
from werkzeug.utils import secure_filename
import os
import pytz
from datetime import datetime
tehran_tz = pytz.timezone('Asia/Tehran')


# مسیرهای عمومی برای نمایش مجله
@magazine_bp.route('/')
def index():
    """صفحه اصلی مجله - نمایش شماره‌های موجود"""
    issues = MagazineIssue.query.filter_by(is_published=True).order_by(MagazineIssue.issue_number.desc()).all()
    return render_template('magazine/index.html', issues=issues)

@magazine_bp.route('/download/<int:issue_id>')
def download_issue(issue_id):
    """دانلود فایل دیجیتال مجله"""
    issue = MagazineIssue.query.get_or_404(issue_id)
    
    if not issue.is_published:
        flash('This issue has not been published yet.', 'error')
        return redirect(url_for('magazine.index'))
    
    # مسیر فایل را برگردانید
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'magazines', issue.file_path)
    
    if os.path.exists(file_path):
        return send_from_directory(
            os.path.join(current_app.config['UPLOAD_FOLDER'], 'magazines'),
            issue.file_path,
            as_attachment=True,
            download_name=f"imazheh-issue-{issue.issue_number}.pdf"
        )
    else:
        flash('Magazine file not found.', 'error')
        return redirect(url_for('magazine.index'))

# فرم درخواست اسپانسری
@magazine_bp.route('/sponsorship', methods=['GET', 'POST'])
def sponsorship_request():
    """ثبت درخواست اسپانسری"""
    if request.method == 'POST':
        name = request.form.get('name')
        company = request.form.get('company')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        if not all([name, email, phone]):
            flash('Please fill in the required fields.', 'error')
            return redirect(url_for('magazine.sponsorship_request'))
        
        new_request = SponsorshipRequest(
            name=name,
            company=company,
            email=email,
            phone=phone,
            message=message
        )
        
        db.session.add(new_request)
        db.session.commit()
        
        flash('Your sponsorship request has been successfully submitted. We will contact you soon.', 'success')
        return redirect(url_for('magazine.index'))
    
    return render_template('magazine/sponsorship.html')

# فرم درخواست تبلیغات
@magazine_bp.route('/advertisement', methods=['GET', 'POST'])
def advertisement_request():
    """ثبت درخواست تبلیغات در مجله"""
    if request.method == 'POST':
        name = request.form.get('name')
        company = request.form.get('company')
        email = request.form.get('email')
        phone = request.form.get('phone')
        ad_type = request.form.get('ad_type')
        size = request.form.get('size')
        duration = request.form.get('duration')
        message = request.form.get('message')
        
        if not all([name, email, phone, ad_type]):
            flash('Please fill in the required fields.', 'error')
            return redirect(url_for('magazine.advertisement_request'))
        
        new_request = AdvertisementRequest(
            name=name,
            company=company,
            email=email,
            phone=phone,
            ad_type=ad_type,
            size=size,
            duration=duration,
            message=message
        )
        
        db.session.add(new_request)
        db.session.commit()
        
        flash('Your advertising request has been successfully submitted. We will contact you soon.', 'success')
        return redirect(url_for('magazine.index'))
    
    return render_template('magazine/advertisement.html')

# فرم اشتراک سالیانه
@magazine_bp.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    """ثبت نام اشتراک سالیانه"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        subscription_type = request.form.get('subscription_type')
        
        if not all([name, email, phone, address]):
            flash('Please fill in the required fields.', 'error')
            return redirect(url_for('magazine.subscribe'))
        
        new_subscription = Subscription(
            name=name,
            email=email,
            phone=phone,
            address=address,
            subscription_type=subscription_type,
            is_active=True
        )
        
        db.session.add(new_subscription)
        db.session.commit()
        
        flash('Your annual subscription has been successfully registered. Information will be sent soon.', 'success')
        return redirect(url_for('magazine.index'))
    
    return render_template('magazine/subscribe.html')
