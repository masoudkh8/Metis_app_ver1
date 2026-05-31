# models/course.py
# بخش ۱۴: Learning Hub - آموزش و آکادمی

from . import db
from datetime import datetime, timedelta
from enum import Enum

class CourseLevel(Enum):
    BEGINNER = 'beginner'  # مقدماتی
    INTERMEDIATE = 'intermediate'  # متوسط
    ADVANCED = 'advanced'  # پیشرفته
    EXPERT = 'expert'  # تخصصی

class CourseCategory(Enum):
    EXPORT_BASICS = 'export_basics'  # اصول صادرات
    IMPORT_BASICS = 'import_basics'  # اصول واردات
    CUSTOMS_REGULATIONS = 'customs_regulations'  # مقررات گمرکی
    INTERNATIONAL_LAW = 'international_law'  # حقوق بین‌الملل
    LOGISTICS = 'logistics'  # لجستیک و حمل‌ونقل
    MARKETING = 'marketing'  # بازاریابی بین‌الملل
    FINANCE = 'finance'  # مالی و پرداخت
    COUNTRY_SPECIFIC = 'country_specific'  # ویژه کشور خاص
    INDUSTRY_SPECIFIC = 'industry_specific'  # ویژه صنعت خاص

class ContentType(Enum):
    VIDEO = 'video'
    ARTICLE = 'article'
    QUIZ = 'quiz'
    ASSIGNMENT = 'assignment'
    LIVE_WEBINAR = 'live_webinar'
    PDF = 'pdf'
    EXTERNAL_LINK = 'external_link'

class CertificateType(Enum):
    COMPLETION = 'completion'  # گواهی تکمیل دوره
    ACHIEVEMENT = 'achievement'  # گواهی موفقیت (نمره بالا)
    PARTICIPATION = 'participation'  # گواهی مشارکت در وبینار

class Course(db.Model):
    """
    دوره آموزشی - بخش ۱۴
    """
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # اطلاعات پایه
    title_fa = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200))
    title_ar = db.Column(db.String(200))
    
    description_fa = db.Column(db.Text)
    description_en = db.Column(db.Text)
    description_ar = db.Column(db.Text)
    
    # دسته‌بندی
    category = db.Column(db.Enum(CourseCategory), nullable=False)
    level = db.Column(db.Enum(CourseLevel), default=CourseLevel.BEGINNER)
    
    # مدرس
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    instructor_name_fa = db.Column(db.String(100))
    instructor_name_en = db.Column(db.String(100))
    instructor_bio = db.Column(db.Text)
    
    # محتوا
    thumbnail = db.Column(db.String(500))  # تصویر شاخص
    trailer_url = db.Column(db.String(500))  # لینک تریلر
    
    # زمان‌بندی
    duration_minutes = db.Column(db.Integer, default=0)  # مدت کل (دقیقه)
    estimated_days = db.Column(db.Integer)  # روزهای تخمینی برای تکمیل
    
    # قیمت‌گذاری
    price = db.Column(db.Numeric(10, 2), default=0)  # قیمت به دلار
    currency = db.Column(db.String(3), default='USD')
    is_free = db.Column(db.Boolean, default=False)
    
    # وضعیت
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    is_featured = db.Column(db.Boolean, default=False)
    
    # آمار
    enrolled_count = db.Column(db.Integer, default=0)
    completed_count = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Numeric(3, 2), default=0)
    rating_count = db.Column(db.Integer, default=0)
    
    # پیش‌نیازها
    prerequisites = db.Column(db.JSON)  # لیست دوره‌های پیش‌نیاز
    target_audience = db.Column(db.Text)  # مخاطبان هدف
    
    # سرفصل‌ها
    syllabus = db.Column(db.JSON)  # ساختار دوره
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    instructor = db.relationship('User', backref=db.backref('taught_courses', lazy='dynamic'))
    modules = db.relationship('CourseModule', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    enrollments = db.relationship('CourseEnrollment', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    certificates = db.relationship('Certificate', backref='course', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title_fa': self.title_fa,
            'title_en': self.title_en,
            'category': self.category.value,
            'level': self.level.value,
            'duration_minutes': self.duration_minutes,
            'is_free': self.is_free,
            'price': float(self.price) if self.price else 0,
            'enrolled_count': self.enrolled_count,
            'average_rating': float(self.average_rating) if self.average_rating else 0,
            'thumbnail': self.thumbnail,
            'instructor_name': self.instructor_name_fa,
        }


class CourseModule(db.Model):
    """
    ماژول/فصل دوره - بخش ۱۴
    """
    __tablename__ = 'course_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    
    title_fa = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200))
    
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0)  # ترتیب نمایش
    
    duration_minutes = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # روابط
    lessons = db.relationship('CourseLesson', backref='module', lazy='dynamic', cascade='all, delete-orphan', order_by='CourseLesson.order_index')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title_fa': self.title_fa,
            'order_index': self.order_index,
            'duration_minutes': self.duration_minutes,
            'lessons_count': self.lessons.count(),
        }


class CourseLesson(db.Model):
    """
    درس/محتوای داخل ماژول - بخش ۱۴
    """
    __tablename__ = 'course_lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('course_modules.id'), nullable=False, index=True)
    
    title_fa = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200))
    
    content_type = db.Column(db.Enum(ContentType), nullable=False)
    
    # محتوا
    video_url = db.Column(db.String(500))  # برای ویدیو
    video_duration = db.Column(db.Integer)  # مدت ویدیو (ثانیه)
    
    article_content = db.Column(db.Text)  # برای مقاله
    
    quiz_data = db.Column(db.JSON)  # سوالات آزمون
    passing_score = db.Column(db.Integer, default=70)  # نمره قبولی (درصد)
    
    file_url = db.Column(db.String(500))  # برای PDF و فایل‌ها
    external_url = db.Column(db.String(500))  # لینک خارجی
    
    order_index = db.Column(db.Integer, default=0)
    
    is_preview = db.Column(db.Boolean, default=False)  # قابل مشاهده رایگان
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # آمار
    view_count = db.Column(db.Integer, default=0)
    completion_count = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title_fa': self.title_fa,
            'content_type': self.content_type.value,
            'video_duration': self.video_duration,
            'is_preview': self.is_preview,
            'order_index': self.order_index,
        }


class CourseEnrollment(db.Model):
    """
    ثبت‌نام کاربر در دوره - بخش ۱۴
    """
    __tablename__ = 'course_enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    
    # وضعیت
    status = db.Column(db.String(20), default='active')  # active, completed, dropped
    
    # پیشرفت
    progress_percentage = db.Column(db.Numeric(5, 2), default=0)
    completed_lessons = db.Column(db.JSON, default=[])  # لیست ID درس‌های تکمیل‌شده
    
    # زمان‌بندی
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # یادداشت‌ها
    notes = db.Column(db.Text)  # یادداشت‌های کاربر
    
    # روابط
    user = db.relationship('User', backref=db.backref('course_enrollments', lazy='dynamic'))
    lesson_progress = db.relationship('LessonProgress', backref='enrollment', lazy='dynamic', cascade='all, delete-orphan')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='unique_enrollment'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'course_title': self.course.title_fa if self.course else None,
            'progress_percentage': float(self.progress_percentage) if self.progress_percentage else 0,
            'status': self.status,
            'enrolled_at': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }


class LessonProgress(db.Model):
    """
    پیشرفت کاربر در هر درس - بخش ۱۴
    """
    __tablename__ = 'lesson_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('course_enrollments.id'), nullable=False, index=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('course_lessons.id'), nullable=False)
    
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    
    # برای آزمون‌ها
    quiz_score = db.Column(db.Integer)  # نمره کسب‌شده
    quiz_passed = db.Column(db.Boolean)
    quiz_attempts = db.Column(db.Integer, default=0)
    
    time_spent_seconds = db.Column(db.Integer, default=0)  # زمان صرف‌شده
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    lesson = db.relationship('CourseLesson', backref='progress_records')
    
    __table_args__ = (db.UniqueConstraint('enrollment_id', 'lesson_id', name='unique_lesson_progress'),)


class Certificate(db.Model):
    """
    گواهینامه دوره - بخش ۱۴
    """
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    certificate_number = db.Column(db.String(50), unique=True, nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    
    # نوع گواهی
    certificate_type = db.Column(db.Enum(CertificateType), nullable=False)
    
    # نمره نهایی
    final_score = db.Column(db.Numeric(5, 2))
    
    # تاریخ
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # تاریخ انقضا (برای گواهی‌های موقت)
    
    # فایل
    pdf_url = db.Column(db.String(500))  # لینک دانلود PDF
    verification_code = db.Column(db.String(20), unique=True)  # کد استعلام
    
    # امضاها
    instructor_signature = db.Column(db.String(500))  # تصویر امضای مدرس
    platform_signature = db.Column(db.String(500))  # تصویر امضای پلتفرم
    
    is_verified = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=True)  # نمایش در پروفایل عمومی
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # روابط
    user = db.relationship('User', backref=db.backref('certificates', lazy='dynamic'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'certificate_number': self.certificate_number,
            'course_title': self.course.title_fa if self.course else None,
            'certificate_type': self.certificate_type.value,
            'final_score': float(self.final_score) if self.final_score else None,
            'issued_at': self.issued_at.isoformat() if self.issued_at else None,
            'verification_code': self.verification_code,
            'pdf_url': self.pdf_url,
            'is_public': self.is_public,
        }


class Webinar(db.Model):
    """
    وبینار زنده - بخش ۱۴
    """
    __tablename__ = 'webinars'
    
    id = db.Column(db.Integer, primary_key=True)
    
    title_fa = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200))
    
    description_fa = db.Column(db.Text)
    description_en = db.Column(db.Text)
    
    # مدرس
    speaker_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    speaker_name = db.Column(db.String(100))
    
    # زمان‌بندی
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    
    # لینک‌ها
    meeting_url = db.Column(db.String(500))  # لینک جلسه
    recording_url = db.Column(db.String(500))  # لینک ضبط شده
    
    # ظرفیت
    max_participants = db.Column(db.Integer, default=100)
    
    # قیمت
    price = db.Column(db.Numeric(10, 2), default=0)
    is_free = db.Column(db.Boolean, default=False)
    
    # وضعیت
    status = db.Column(db.String(20), default='scheduled')  # scheduled, live, completed, cancelled
    
    # آمار
    registered_count = db.Column(db.Integer, default=0)
    attended_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    speaker = db.relationship('User', backref=db.backref('webinars', lazy='dynamic'))
    registrations = db.relationship('WebinarRegistration', backref='webinar', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title_fa': self.title_fa,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'status': self.status,
            'is_free': self.is_free,
            'registered_count': self.registered_count,
            'max_participants': self.max_participants,
        }


class WebinarRegistration(db.Model):
    """
    ثبت‌نام در وبینار - بخش ۱۴
    """
    __tablename__ = 'webinar_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    webinar_id = db.Column(db.Integer, db.ForeignKey('webinars.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    attended = db.Column(db.Boolean, default=False)
    attendance_duration = db.Column(db.Integer)  # مدت حضور (دقیقه)
    
    certificate_issued = db.Column(db.Boolean, default=False)
    
    __table_args__ = (db.UniqueConstraint('webinar_id', 'user_id', name='unique_webinar_registration'),)
    
    user = db.relationship('User', backref=db.backref('webinar_registrations', lazy='dynamic'))


class LearningPath(db.Model):
    """
    مسیر یادگیری شخصی‌سازی‌شده - بخش ۱۴
    """
    __tablename__ = 'learning_paths'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # دوره‌های پیشنهادی
    recommended_courses = db.Column(db.JSON)  # لیست ID دوره‌ها
    
    # پیشرفت کلی
    total_courses = db.Column(db.Integer, default=0)
    completed_courses = db.Column(db.Integer, default=0)
    progress_percentage = db.Column(db.Numeric(5, 2), default=0)
    
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('learning_paths', lazy='dynamic'))
