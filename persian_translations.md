# Persian to English Translation Dictionary
# Generated from project files

## File: models/gamification.py

| Line | Persian Text | English Translation |
|------|-------------|---------------------|
| 3 | بخش ۳: سیستم اعتبار و گیمیفیکیشن حرفه‌ای (Trust & Gamification) | Section 3: Trust & Professional Gamification System (Trust & Gamification) |
| 4 | - موتور امتیازدهی پویا | - Dynamic Scoring Engine |
| 5 | - نشان‌های افتخار (Badges) | - Badges (Badges) |
| 6 | - چالش‌های فصلی | - Seasonal Challenges |
| 7 | - پیشرفت شخصی | - Personal Progress |
| 17 | """نشان‌های افتخار کاربران""" | """User Badges""" |
| 23 | 'متخصص صادرات به عمان' | 'Export Expert to Oman' |
| 28 | # رابطه | # Relationship |
| 33 | """داشبورد پیشرفت شخصی کاربران""" | """User Personal Progress Dashboard""" |
| 39 | # امتیاز کل گیمیفیکیشن | # Total Gamification Score |
| 42 | # سطح کاربر (Level) | # User Level (Level) |
| 45 | # پیشرفت به سطح بعدی (۰-۱۰۰ درصد) | # Progress to Next Level (0-100 percent) |
| 48 | # آمار فعالیت‌ها | # Activity Statistics |
| 51 | # تعداد محتوای مفید | # Number of Useful Content |
| 52 | # تعداد معرفی‌های موفق | # Number of Successful Referrals |
| 54 | # آخرین فعالیت | # Last Activity |
| 57 | # رابطه | # Relationship |
| 61 | """محاسبه سطح بر اساس امتیاز کل""" | """Calculate Level Based on Total Score""" |
| 62 | # فرمول ساده: هر ۱۰۰۰ امتیاز = ۱ سطح | # Simple Formula: Every 1000 points = 1 level |
| 67 | """پیشنهاد ۳ اقدام بعدی برای ارتقا""" | """Suggest 3 Next Actions for Upgrade""" |
| 70 | "تکمیل پروفایل شرکتی (+۲۰۰ امتیاز)" | "Complete Company Profile (+200 points)" |
| 72 | "انجام اولین معامله موفق (+۵۰۰ امتیاز)" | "Complete First Successful Trade (+500 points)" |
| 74 | "اشتراک‌گذاری محتوای تخصصی (+۱۰۰ امتیاز)" | "Share Specialized Content (+100 points)" |
| 76 | "معرفی همکار تجاری (+۱۵۰ امتیاز)" | "Refer Business Partner (+150 points)" |
| 81 | """چالش‌های فصلی با پاداش‌های ملموس""" | """Seasonal Challenges with Tangible Rewards""" |
| 93 | # شرکت‌کنندگان | # Participants |
| 98 | """شرکت‌کنندگان در چالش‌های فصلی""" | """Participants in Seasonal Challenges""" |
| 104 | # درصد پیشرفت | # Progress Percentage |
| 109 | # روابط | # Relationships |

## File: models/trading/__init__.py

| Line | Persian Text | English Translation |
|------|-------------|---------------------|
| 84 | base_asset = db.Column(db.String(50), nullable=False)  # ارز پایه | base_asset = db.Column(db.String(50), nullable=False)  # Base Currency |
| 85 | quote_asset = db.Column(db.String(50), nullable=False)  # ارز قیمت | quote_asset = db.Column(db.String(50), nullable=False)  # Quote Currency |
| 86 | symbol = db.Column(db.String(20), unique=True, nullable=False)  # نماد نمایشی | symbol = db.Column(db.String(20), unique=True, nullable=False)  # Display Symbol |
| 88 | # مشخصات معامله | # Trade Specifications |
| 91 | price_precision = db.Column(db.Integer, default=2)  # دقت قیمت | price_precision = db.Column(db.Integer, default=2)  # Price Precision |
| 92 | quantity_precision = db.Column(db.Integer, default=8)  # دقت مقدار | quantity_precision = db.Column(db.Integer, default=8)  # Quantity Precision |
| 94 | # وضعیت | # Status |
| 98 | # محدودیت‌ها | # Limits/Restrictions |
| 99 | trading_hours = db.Column(db.JSON, default={})  # ساعات مجاز معامله | trading_hours = db.Column(db.JSON, default={})  # Allowed Trading Hours |
| 100 | allowed_user_levels = db.Column(db.JSON, default=[])  # سطوح کاربری مجاز | allowed_user_levels = db.Column(db.JSON, default=[])  # Allowed User Levels |
| 102 | # آمار بازار (۲۴ ساعته) | # Market Statistics (24 hours) |
| 104 | price_change_24h = db.Column(db.Numeric(10, 4))  # درصد تغییر | price_change_24h = db.Column(db.Numeric(10, 4))  # Percentage Change |
| 132 | # موجودی‌ها به صورت JSONB: {"USDT": 1000.50, "BTC": 0.05} | # Balances as JSONB: {"USDT": 1000.50, "BTC": 0.05} |
| 134 | locked_balances = db.Column(db.JSON, default={})  # موجودی قفل‌شده در سفارش‌ها | locked_balances = db.Column(db.JSON, default={})  # Locked Balances in Orders |
| 136 | # اعتبار | # Credit |
| 140 | # آمار معاملاتی | # Trading Statistics |
| 144 | # وضعیت | # Status |
| 148 | # مدیریت ریسک | # Risk Management |
| 150 | daily_loss_limit = db.Column(db.Numeric(20, 8))  # حد ضرر روزانه | daily_loss_limit = db.Column(db.Numeric(20, 8))  # Daily Loss Limit |
| 151 | daily_loss_current = db.Column(db.Numeric(20, 8), default=0)  # ضرر فعلی امروز | daily_loss_current = db.Column(db.Numeric(20, 8), default=0)  # Current Loss Today |
| 183 | # ارجاع به سفارش یا معامله مرتبط | # Reference to Related Order or Trade |
| 188 | reference_id = db.Column(db.String(100))  # شناسه مرجع خارجی | reference_id = db.Column(db.String(100))  # External Reference ID |
| 195 | # رابطه | # Relationship |
| 221 | # نوع سفارش | # Order Type |
| 225 | # سمت سفارش | # Order Side |
| 229 | # قیمت و مقدار | # Price and Quantity |
| 235 | # قیمت‌های شرطی | # Conditional Prices |
| 239 | # وضعیت | # Status |
| 243 | # زمان‌بندی | # Timing/Scheduling |
| 247 | # مالی | # Financial |
| 248 | fee_rate = db.Column(db.Numeric(10, 6), default=0.001)  # کارمزد | fee_rate = db.Column(db.Numeric(10, 6), default=0.001)  # Fee |
| 253 | client_order_id = db.Column(db.String(100), unique=True)  # شناسه سفارش از سمت کلاینت | client_order_id = db.Column(db.String(100), unique=True)  # Client Order ID |
| 262 | # روابط | # Relationships |
| 289 | # سفارش‌های طرفین | # Orders of Both Parties |
| 293 | # اطلاعات معامله | # Trade Information |
| 298 | # کارمزدها | # Fees |
| 302 | # نقش‌ها | # Roles |
| 308 | # روابط | # Relationships |
| 328 | """داده‌های تاریخی بازار برای نمودارها""" | """Historical Market Data for Charts""" |
| 329 | کندل‌های قیمتی (OHLCV) | Price Candles (OHLCV) |
| 336 | # تایم‌فریم | # Timeframe |
| 339 | # زمان شروع کندل | # Candle Start Time |
| 342 | # داده‌های OHLCV | # OHLCV Data |
| 350 | # تعداد معاملات | # Number of Trades |
| 353 | # داده‌های اضافی | # Additional Data |
| 359 | # رابطه | # Relationship |
| 383 | description_fa = db.Column(db.Text) | description_fa = db.Column(db.Text) |
| 386 | is_public = db.Column(db.Boolean, default=False)  # آیا کاربران می‌توانند ببینند | is_public = db.Column(db.Boolean, default=False)  # Can Users View |
| 413 | # ایجاد انواع سفارش | # Create Order Types |
| 420 | # ایجاد سمت‌های سفارش | # Create Order Sides |
| 427 | # ایجاد وضعیت‌های سفارش | # Create Order Statuses |
| 434 | # ایجاد تنظیمات پیش‌فرض | # Create Default Settings |
| 439 | 'desc_fa': 'فعال بودن تالار معاملاتی', | 'desc_fa': 'Trading Hall Enabled', |
| 446 | 'desc_fa': 'کارمزد پیش‌فرض معاملات', | 'desc_fa': 'Default Trading Fee', |
| 453 | 'desc_fa': 'حداکثر سفارش‌های باز برای هر کاربر', | 'desc_fa': 'Maximum Open Orders Per User', |

## File: models/user.py

| Line | Persian Text | English Translation |
|------|-------------|---------------------|
| 14 | """8 تخصصی نقش‌های کاربری بر اساس CONTEXT_MASTER_BRIEF""" | """8 Specialized User Roles Based on CONTEXT_MASTER_BRIEF""" |
| 15 | PRODUCER = 'producer'              # تولیدکننده/صادرکننده | PRODUCER = 'producer'              # Producer/Exporter |
| 16 | BUYER = 'buyer'                    # واردکننده/خریدار | BUYER = 'buyer'                    # Importer/Buyer |
| 17 | BROKER = 'broker'                  # کارگزار تجاری | BROKER = 'broker'                  # Commercial Broker |
| 18 | CORPORATE_AGENT = 'corporate_agent' # نماینده شرکتی | CORPORATE_AGENT = 'corporate_agent' # Corporate Agent |
| 19 | LOGISTICS = 'logistics'            # خدمات لجستیک و بیمه | LOGISTICS = 'logistics'            # Logistics and Insurance Services |
| 20 | LEGAL = 'legal'                    # خدمات حقوقی و انطباق | LEGAL = 'legal'                    # Legal and Compliance Services |
| 21 | TECH_PARTNER = 'tech_partner'      # شریک فناوری | TECH_PARTNER = 'tech_partner'      # Technology Partner |
| 22 | INVESTOR = 'investor'              # سرمایه‌گذار مالی | INVESTOR = 'investor'              # Financial Investor |
| 23 | ADMIN = 'admin'                    # مدیریت سیستم | ADMIN = 'admin'                    # System Management |
| 24 | MODERATOR = 'moderator'            # ناظر محتوا | MODERATOR = 'moderator'            # Content Moderator |
| 32 | """دریافت نام نمایشی فارسی نقش""" | """Get Persian Display Name of Role""" |
| 34 | 'producer': 'تولیدکننده/صادرکننده', | 'producer': 'Producer/Exporter', |
| 35 | 'buyer': 'واردکننده/خریدار', | 'buyer': 'Importer/Buyer', |
| 36 | 'broker': 'کارگزار تجاری', | 'broker': 'Commercial Broker', |
| 37 | 'corporate_agent': 'نماینده شرکتی', | 'corporate_agent': 'Corporate Agent', |
| 38 | 'logistics': 'خدمات لجستیک و بیمه', | 'logistics': 'Logistics and Insurance Services', |
| 39 | 'legal': 'خدمات حقوقی و انطباق', | 'legal': 'Legal and Compliance Services', |
| 40 | 'tech_partner': 'شریک فناوری', | 'tech_partner': 'Technology Partner', |
| 41 | 'investor': 'سرمایه‌گذار مالی', | 'investor': 'Financial Investor', |
| 42 | 'admin': 'مدیر سیستم', | 'admin': 'System Manager', |
| 43 | 'moderator': 'ناظر محتوا' | 'moderator': 'Content Moderator' |
| 49 | """دریافت نقش‌های اصلی تجاری (بدون Admin و Moderator)""" | """Get Core Business Roles (Without Admin and Moderator)""" |
| 54 | """پروفایل تخصصی کاربران با فیلدهای مخصوص هر نقش""" | """Specialized User Profile with Fields Specific to Each Role""" |
| 61 | bio = db.Column(db.Text)  # بیوگرافی حرفه‌ای | bio = db.Column(db.Text)  # Professional Biography |
| 68 | # برای Producer/Exporter | # For Producer/Exporter |
| 69 | production_capacity = db.Column(db.String(100))  # ظرفیت تولید | production_capacity = db.Column(db.String(100))  # Production Capacity |
| 70 | export_experience_years = db.Column(db.Integer)  # سال‌های سابقه صادرات | export_experience_years = db.Column(db.Integer)  # Years of Export Experience |
| 71 | main_products = db.Column(db.Text)  # محصولات اصلی | main_products = db.Column(db.Text)  # Main Products |
| 72 | certifications = db.Column(db.Text)  # گواهینامه‌ها (ISO, HACCP, etc.) | certifications = db.Column(db.Text)  # Certifications (ISO, HACCP, etc.) |
| 73 | target_markets = db.Column(db.Text)  # بازارهای هدف | target_markets = db.Column(db.Text)  # Target Markets |
| 75 | # برای Buyer/Importer | # For Buyer/Importer |
| 76 | annual_import_volume = db.Column(db.String(100))  # حجم واردات سالانه | annual_import_volume = db.Column(db.String(100))  # Annual Import Volume |
| 77 | main_categories = db.Column(db.Text)  # دسته‌بندی‌های اصلی مورد نیاز | main_categories = db.Column(db.Text)  # Main Required Categories |
| 78 | preferred_payment_terms = db.Column(db.String(200))  # شرایط پرداخت مورد علاقه | preferred_payment_terms = db.Column(db.String(200))  # Preferred Payment Terms |
| 80 | # برای Broker | # For Broker |
| 81 | specialization_sectors = db.Column(db.Text)  # بخش‌های تخصصی | specialization_sectors = db.Column(db.Text)  # Specialization Sectors |
| 82 | broker_license_number = db.Column(db.String(50))  # شماره پروانه کارگزاری | broker_license_number = db.Column(db.String(50))  # Broker License Number |
| 83 | commission_rate = db.Column(db.String(20))  # نرخ کمیسیون | commission_rate = db.Column(db.String(20))  # Commission Rate |
| 85 | # برای Corporate Agent | # For Corporate Agent |
| 86 | company_position = db.Column(db.String(100))  # سمت در شرکت | company_position = db.Column(db.String(100))  # Position in Company |
| 87 | authorization_level = db.Column(db.String(100))  # سطح اختیارات | authorization_level = db.Column(db.String(100))  # Authorization Level |
| 91 | # برای Logistics & Insurance | # For Logistics & Insurance |
| 92 | service_types = db.Column(db.Text)  # انواع خدمات (حمل دریایی، هوایی، زمینی، بیمه) | service_types = db.Column(db.Text)  # Service Types (Sea, Air, Land Transport, Insurance) |
| 93 | coverage_regions = db.Column(db.Text)  # مناطق تحت پوشش | coverage_regions = db.Column(db.Text)  # Coverage Regions |
| 94 | insurance_license = db.Column(db.String(50))  # مجوز بیمه | insurance_license = db.Column(db.String(50))  # Insurance License |
| 95 | fleet_size = db.Column(db.String(50))  # اندازه ناوگان | fleet_size = db.Column(db.String(50))  # Fleet Size |
| 97 | # برای Legal & Compliance | # For Legal & Compliance |
| 98 | practice_areas = db.Column(db.Text)  # حوزه‌های فعالیت (گمرک، قراردادها، داوری) | practice_areas = db.Column(db.Text)  # Practice Areas (Customs, Contracts, Arbitration) |
| 99 | bar_association_number = db.Column(db.String(50))  # شماره کانون وکلا | bar_association_number = db.Column(db.String(50))  # Bar Association Number |
| 100 | years_of_practice = db.Column(db.Integer)  # سال‌های فعالیت | years_of_practice = db.Column(db.Integer)  # Years of Practice |
| 102 | # برای Tech Partner | # For Tech Partner |
| 103 | tech_specialties = db.Column(db.Text)  # تخصص‌های فنی (ERP, CRM, AI, Blockchain) | tech_specialties = db.Column(db.Text)  # Technical Specialties (ERP, CRM, AI, Blockchain) |
| 104 | portfolio_url = db.Column(db.String(200))  # لینک نمونه کارها | portfolio_url = db.Column(db.String(200))  # Portfolio URL |
| 105 | service_packages = db.Column(db.Text)  # بسته‌های خدماتی | service_packages = db.Column(db.Text)  # Service Packages |
| 107 | # برای Investor | # For Investor |
| 108 | investment_capacity = db.Column(db.String(100))  # ظرفیت سرمایه‌گذاری | investment_capacity = db.Column(db.String(100))  # Investment Capacity |
| 109 | preferred_sectors = db.Column(db.Text)  # بخش‌های مورد علاقه برای سرمایه‌گذاری | preferred_sectors = db.Column(db.Text)  # Preferred Sectors for Investment |
| 110 | investment_type = db.Column(db.String(100))  # نوع سرمایه‌گذاری (VC, Angel, Project-based) | investment_type = db.Column(db.String(100))  # Investment Type (VC, Angel, Project-based) |
| 111 | risk_tolerance = db.Column(db.String(50))  # سطح ریسک‌پذیری | risk_tolerance = db.Column(db.String(50))  # Risk Tolerance Level |
| 113 | # وضعیت‌ها | # Statuses |
| 114 | is_verified = db.Column(db.Boolean, default=False)  # تأیید هویت انجام شده | is_verified = db.Column(db.Boolean, default=False)  # Identity Verification Completed |
| 118 | trust_score_override = db.Column(db.Integer)  # امتیاز اعتماد دستی (برای Admin) | trust_score_override = db.Column(db.Integer)  # Manual Trust Score (For Admin) |
| 120 | # === سیستم مجوزهای سفارشی (Custom Permissions) === | # === Custom Permissions System === |
| 121 | # این فیلد اجازه می‌دهد دسترسی‌های کاربر را به صورت ریزدانه تنظیم کنید | # This field allows you to set user permissions in a granular way |
| 122 | # اگر NULL یا خالی باشد، از مجوزهای پیش‌فرض نقش استفاده می‌شود | # If NULL or empty, default role permissions will be used |
| 123 | # فرمت: JSON Array از رشته‌های Permission (مثلاً ["order.view", "logistics.update_status"]) | # Format: JSON Array of Permission strings (e.g., ["order.view", "logistics.update_status"]) |
| 136 | """دریافت لیست مجوزهای سفارشی به صورت لیستی از رشته‌ها""" | """Get List of Custom Permissions as List of Strings""" |
| 137 | اگر پروفایل وجود نداشته باشد یا custom_permissions خالی باشد، لیست خالی برمی‌گرداند | If profile doesn't exist or custom_permissions is empty, returns empty list |
| 154 | """تنظیم مجوزهای سفارشی به صورت لیستی از رشته‌های permission value""" | """Set Custom Permissions as List of Permission Value Strings""" |
| 156 | permissions_list: لیستی از رشته‌ها مانند ['order.view', 'logistics.update_status'] | permissions_list: List of strings like ['order.view', 'logistics.update_status'] |
| 167 | """اضافه کردن یک مجوز به مجوزهای سفارشی""" | """Add a Permission to Custom Permissions""" |
| 185 | """حذف یک مجوز از مجوزهای سفارشی""" | """Remove a Permission from Custom Permissions""" |
| 203 | """بررسی وجود یک مجوز در مجوزهای سفارشی""" | """Check Existence of a Permission in Custom Permissions""" |
| 212 | # جدول واسط برای اتصالات (Follow System) - باید قبل از کلاس User تعریف شود | # Intermediate Table for Connections (Follow System) - Must be defined before User class |
| 222 | """لایه‌های دسترسی باشگاه نخبگان (Concentric Circles Model)""" | """Elite Club Access Layers (Concentric Circles Model)""" |
| 223 | OBSERVER = 'observer'          # لایه ۱: بازدیدکننده (تازه وارد،未احراز) | OBSERVER = 'observer'          # Layer 1: Visitor (Newcomer, Unverified) |
| 224 | VERIFIED = 'verified'          # لایه ۲: عضو تأیید شده (KYC تکمیل، حق عضویت پایه) | VERIFIED = 'verified'          # Layer 2: Verified Member (KYC Completed, Basic Membership) |
| 225 | PARTNER = 'partner'            # لایه ۳: شریک استراتژیک (TrustScore > 70، دعوت یا عملکرد بالا) | PARTNER = 'partner'            # Layer 3: Strategic Partner (TrustScore > 70, Invitation or High Performance) |
| 226 | ELITE = 'elite'                # لایه ۴: نخبگان (دعوت اختصاصی، TrustScore > 90، تایید هیئت مدیره) | ELITE = 'elite'                # Layer 4: Elite (Exclusive Invitation, TrustScore > 90, Board Approval) |
| 230 | """دریافت نام نمایشی فارسی لایه""" | """Get Persian Display Name of Layer""" |
| 232 | 'observer': 'بازدیدکننده', | 'observer': 'Visitor', |
| 233 | 'verified': 'عضو تأیید شده', | 'verified': 'Verified Member', |
| 234 | 'partner': 'شریک استراتژیک', | 'partner': 'Strategic Partner', |
| 235 | 'elite': 'نخبه' | 'elite': 'Elite' |
| 241 | """دریافت سطح سلسله مراتبی برای مقایسه""" | """Get Hierarchical Level for Comparison""" |
| 265 | invited_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # چه کسی دعوت کرده؟ | invited_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Who invited? |
| 268 | # امتیاز اعتماد (کلید ارتقای لایه) | # Trust Score (Key to Layer Upgrade) |
| 269 | trust_score_value = db.Column(db.Integer, default=50, nullable=False, index=True)  # ✅ امتیاز اولیه 50 | trust_score_value = db.Column(db.Integer, default=50, nullable=False, index=True)  # ✅ Initial Score 50 |
| 271 | # وضعیت احراز هویت (شرط ورود به لایه ۲) | # Authentication Status (Condition for Entry to Layer 2) |
| 275 | # === فیلدهای تخصصی پروفایل (درخواست ۱) === | # === Specialized Profile Fields (Request 1) === |
| 276 | expertise_area = db.Column(db.String(200))  # حوزه تخصصی برای متخصصین | expertise_area = db.Column(db.String(200))  # Area of Expertise for Professionals |
| 277 | job_title = db.Column(db.String(100))  # عنوان شغلی | job_title = db.Column(db.String(100))  # Job Title |
| 278 | bio = db.Column(db.Text)  # درباره من / بیوگرافی حرفه‌ای | bio = db.Column(db.Text)  # About Me / Professional Biography |
| 279 | website = db.Column(db.String(200))  # وبسایت شخصی/شرکتی | website = db.Column(db.String(200))  # Personal/Company Website |
| 280 | social_links = db.Column(db.Text)  # لینک‌های اجتماعی (JSON format) | social_links = db.Column(db.Text)  # Social Links (JSON format) |
| 282 | # وضعیت تأیید هویت (درخواست ۱) | # Identity Verification Status (Request 1) |
| 283 | is_verified = db.Column(db.Boolean, default=False)  # ✅ تأیید هویت انجام شده | is_verified = db.Column(db.Boolean, default=False)  # ✅ Identity Verification Completed |
| 284 | verification_documents = db.Column(db.Text)  # مدارک تأیید هویت (JSON format) | verification_documents = db.Column(db.Text)  # Identity Verification Documents (JSON format) |
| 286 | # === فیلدهای امنیتی و احراز هویت === | # === Security and Authentication Fields === |
| 287 | # Avatar/Profile Picture | # Avatar/Profile Picture |
| 288 | avatar_filename = db.Column(db.String(255), nullable=True)  # نام فایل عکس پروفایل | avatar_filename = db.Column(db.String(255), nullable=True)  # Profile Picture Filename |
| 290 | # Two-Factor Authentication (2FA) | # Two-Factor Authentication (2FA) |
| 291 | two_factor_enabled = db.Column(db.Boolean, default=False, nullable=False) | two_factor_enabled = db.Column(db.Boolean, default=False, nullable=False) |
| 292 | two_factor_secret = db.Column(db.String(32), nullable=True)  # رمز的秘密 برای TOTP | two_factor_secret = db.Column(db.String(32), nullable=True)  # Secret for TOTP |
| 293 | backup_codes = db.Column(db.Text, nullable=True)  # کدهای پشتیبان (JSON format) | backup_codes = db.Column(db.Text, nullable=True)  # Backup Codes (JSON format) |
| 295 | # Account Lockout | # Account Lockout |
| 296 | failed_login_attempts = db.Column(db.Integer, default=0, nullable=False) | failed_login_attempts = db.Column(db.Integer, default=0, nullable=False) |
| 297 | locked_until = db.Column(db.DateTime, nullable=True)  # زمان قفل بودن حساب | locked_until = db.Column(db.DateTime, nullable=True)  # Account Lock Time |
| 299 | # Password History (برای جلوگیری از استفاده مجدد) | # Password History (To Prevent Reuse) |
| 300 | password_history = db.Column(db.Text, nullable=True)  # JSON array of previous password hashes | password_history = db.Column(db.Text, nullable=True)  # JSON array of previous password hashes |
| 302 | # Email Verification | # Email Verification |
| 313 | dark_mode_preference = db.Column(db.String(20), default='system', nullable=False)  # 'light', 'dark', 'system' | dark_mode_preference = db.Column(db.String(20), default='system', nullable=False)  # 'light', 'dark', 'system' |
| 315 | # Notification Preferences (JSON) | # Notification Preferences (JSON) |
| 318 | # Privacy Settings (JSON) | # Privacy Settings (JSON) |
| 321 | # تاریخچه | # History |
| 333 | is_active = db.Column(db.Boolean, default=True)  # ✅ فعال/غیرفعال | is_active = db.Column(db.Boolean, default=True)  # ✅ Active/Inactive |
| 346 | # روابط اجتماعی (Follow System) - استفاده از مدل Follow از social.py | # Social Relationships (Follow System) - Using Follow Model from social.py |
| 347 | # relationshipهای follow/followers در models/social.py به User اضافه می‌شوند | # follow/followers relationships are added to User in models/social.py |
| 348 | # اینجا فقط برای سازگاری با کدهای قدیمی تعریف شده | # Defined here only for compatibility with old code |
| 350 | # پست‌ها - relationship در models/social.py تعریف شده است | # Posts - relationship is defined in models/social.py |
| 351 | # برای جلوگیری از تداخل، اینجا تعریف نمی‌کنیم | # To avoid conflict, not defined here |
| 360 | """دریافت نام نمایشی فارسی نقش کاربر""" | """Get Persian Display Name of User Role""" |
| 365 | """دریافت نام نمایشی فارسی لایه عضویت""" | """Get Persian Display Name of Membership Layer""" |
| 366 | return MembershipTier.get_display_name(self.membership_tier.value) if self.membership_tier else 'بازدیدکننده' | return MembershipTier.get_display_name(self.membership_tier.value) if self.membership_tier else 'Visitor' |
| 370 | """آیا کاربر جزو اعضای اصلی باشگاه نخبگان است؟""" | """Is User Among Core Members of Elite Club?""" |
| 411 | """تبدیل به دیکشنری برای API""" | """Convert to Dictionary for API""" |

## File: routes/admin/routes.py

| Line | Persian Text | English Translation |
|------|-------------|---------------------|
| 29 | # --------------------------------------- | # --------------------------------------- |
| 30 | # Decorator: فقط ادمین دسترسی داشته باشه | # Decorator: Only Admin Has Access |
| 54 | # --------------------------------------- | # --------------------------------------- |
| 55 | # داشبورد ادمین | # Admin Dashboard |
| 60 | """داشبورد ادمین با نمایش آمار و نوتیفیکیشن‌های جدید""" | """Admin Dashboard with Statistics and New Notifications""" |
| 67 | # شمارش مدارک آپلود شده برای بررسی (کاربرانی که مدارک دارند اما هنوز تأیید نشده‌اند) | # Count Uploaded Documents for Review (Users who have documents but not yet verified) |
| 74 | # دریافت نوتیفیکیشن‌های خوانده‌نشده ادمین | # Get Admin Unread Notifications |
| 85 | # ✅ Fetch recent activity logs for admin dashboard | # ✅ Fetch recent activity logs for admin dashboard |
| 99 | # --------------------------------------- | # --------------------------------------- |
| 100 | # مدیریت کاربران | # User Management |
| 122 | # ✅ محاسبه تعداد در بک‌اند | # ✅ Calculate Count in Backend |
| 134 | # --------------------------------------- | # --------------------------------------- |
| 135 | # تغییر نقش کاربر | # Change User Role |
| 159 | # --------------------------------------- | # --------------------------------------- |
| 160 | # درخواست‌های ارتقاء به کاربر ویژه | # Upgrade Requests to Premium User |
| 179 | # --------------------------------------- | # --------------------------------------- |
| 180 | # تأیید یا رد درخواست ارتقاء (یکپارچه‌سازی approve و reject) | # Approve or Reject Upgrade Request (Integration of approve and reject) |
| 190 | # ارتقای لایه عضویت به VERIFIED (لایه ۲) | # Upgrade Membership Layer to VERIFIED (Layer 2) |
| 193 | # تأیید KYC | # KYC Verification |
| 195 | # افزایش امتیاز اعتماد (Trust Score) | # Increase Trust Score |
| 197 | # ثبت زمان پریمیوم شدن | # Record Premium Time |
| 200 | # ذخیره مدارک در فیلد verification_documents | # Save Documents in verification_documents Field |
| 225 | # --------------------------------------- | # --------------------------------------- |
| 226 | # تأیید درخواست ارتقاء (قدیمی - برای سازگاری) | # Approve Upgrade Request (Old - For Compatibility) |
| 233 | # ارتقای لایه عضویت به VERIFIED (لایه ۲) | # Upgrade Membership Layer to VERIFIED (Layer 2) |
| 236 | # تأیید KYC | # KYC Verification |
| 238 | # ثبت زمان پریمیوم شدن | # Record Premium Time |
| 247 | # --------------------------------------- | # --------------------------------------- |
| 248 | # رد درخواست ارتقاء (قدیمی - برای سازگاری) | # Reject Upgrade Request (Old - For Compatibility) |
| 261 | # --------------------------------------- | # --------------------------------------- |
| 262 | # مشاهده جزئیات درخواست | # View Request Details |
| 271 | # --------------------------------------- | # --------------------------------------- |
| 272 | # مشاهده مدارک کاربر | # View User Documents |
| 278 | # دریافت مدارک از فیلد verification_documents (JSON format) | # Get Documents from verification_documents Field (JSON format) |
| 286 | # --------------------------------------- | # --------------------------------------- |
| 287 | # مشاهده همه مدارک کاربران برای بررسی | # View All User Documents for Review |
| 291 | """نمایش لیست تمام کاربرانی که مدارک آپلود کرده‌اند""" | """Display List of All Users Who Have Uploaded Documents""" |
| 312 | # آمار | # Statistics |
| 333 | # --------------------------------------- | # --------------------------------------- |
| 334 | # تأیید مدارک کاربر | # Verify User Documents |
| 342 | # اگر کاربر مدارک کامل دارد، لایه عضویت را ارتقا بده | # If User Has Complete Documents, Upgrade Membership Layer |
| 347 | # ایجاد نوتیفیکیشن برای کاربر | # Create Notification for User |
| 355 | related_type='document_verified', | related_type='document_verified', |
| 356 | title='✅ مدارک شما تأیید شد', | title='✅ Your Documents Were Verified', |
| 357 | message=f'مدارک تأیید هویت شما با موفقیت تأیید شد. امتیاز اعتماد شما افزایش یافت.' | message=f'Your identity verification documents were successfully verified. Your trust score has increased.' |
| 360 | # افزایش TrustScore | # Increase TrustScore |
| 370 | # --------------------------------------- | # --------------------------------------- |
| 371 | # رد مدارک کاربر | # Reject User Documents |
| 376 | # می‌توانیم مدارک را پاک کنیم یا فقط وضعیت را تغییر دهیم | # We can delete documents or just change the status |
| 377 | # در اینجا فقط وضعیت را به False تغییر می‌دهیم | # Here we just change the status to False |
| 380 | # ایجاد نوتیفیکیشن برای کاربر | # Create Notification for User |
| 388 | title='⚠️ مدارک شما رد شد', | title='⚠️ Your Documents Were Rejected', |
| 389 | message=f'مدارک تأیید هویت شما مورد تأیید قرار نگرفت. لطفاً مدارک صحیح را آپلود کنید.' | message=f'Your identity verification documents were not approved. Please upload correct documents.' |
| 399 | # --------------------------------------- | # --------------------------------------- |
| 400 | # حذف کاربر (با احتیاط) | # Delete User (With Caution) |
| 412 | # حذف درخواست ارتقاء اگر وجود داشت | # Delete Upgrade Request if Existed |
| 427 | # --------------------------------------- | # --------------------------------------- |
| 428 | # غیرفعال‌سازی کاربر | # Deactivate User |
| 448 | # --------------------------------------- | # --------------------------------------- |
| 449 | # فعال‌سازی کاربر | # Activate User |
| 461 | # --------------------------------------- | # --------------------------------------- |
| 462 | # تغییر وضعیت ویژه (Premium) کاربر | # Change User Premium Status |

## File: routes/users/auth.py

| Line | Persian Text | English Translation |
|------|-------------|---------------------|
| 87 | # اگر درخواستی وجود ندارد، یک درخواست جدید با وضعیت draft ایجاد کن | # If no request exists, create a new request with draft status |
| 97 | # اگر شماره قبلاً تأیید شده، به مرحله بعد برو | # If number already verified, go to next step |
| 100 | return redirect(url_for('users.verify_email'))  # ✅ به ایمیل برو، نه payment_confirmation | return redirect(url_for('users.verify_email'))  # ✅ Go to email, not payment_confirmation |
| 123 | return redirect(url_for('users.verify_email'))  # ✅ بعد از تأیید شماره، به ایمیل برو | return redirect(url_for('users.verify_email'))  # ✅ After number verification, go to email |
| 127 | # ارسال اولیه کد | # Initial Code Sending |
| 148 | # ------------------------------- | # ------------------------------- |
| 149 | # تأیید ایمیل (صفحه نمایش) | # Email Verification (Display Page) |
| 151 | # ------------------------------- | # ------------------------------- |
| 152 | # تأیید ایمیل (صفحه نمایش - برای کاربرانی که ثبت‌نام کرده‌اند) | # Email Verification (Display Page - For Users Who Registered) |
| 153 | @users_bp.route('/verify_email', endpoint='show_verify_email_page')  # ← تغییر: اضافه کردن endpoint منحصر به فرد | @users_bp.route('/verify_email', endpoint='show_verify_email_page')  # ← Change: Add unique endpoint |
| 159 | # اگر درخواستی وجود ندارد، کاربر باید ابتدا فرآیند را شروع کند | # If no request exists, user must start the process first |
| 164 | # حذف شرط phone_verified - مستقیماً به تأیید ایمیل می‌رویم | # Remove phone_verified condition - Go directly to email verification |
| 182 | # ارسال ایمیل تأیید | # Send Confirmation Email |
| 252 | # ✅ همچنین is_email_verified را در جدول User نیز true کن | # ✅ Also set is_email_verified to true in User table |
| 261 | # ==================== فراموشی رمز عبور ==================== | # ==================== Password Recovery ==================== |
| 265 | """درخواست بازیابی رمز عبور""" | """Password Recovery Request""" |
| 275 | # حتی اگر کاربر وجود نداشت، برای امنیت پیام یکسان نشان بده | # Even if user doesn't exist, show same message for security |
| 277 | # ایجاد توکن بازیابی | # Create Recovery Token |
| 284 | # ارسال ایمیل | # Send Email |
| 300 | description='Request Password Recovery', | description='Request Password Recovery', |
| 309 | description='of Error sending email: {str(e)}', | description='of Error sending email: {str(e)}', |
| 322 | """بازیابی رمز عبور با توکن""" | """Password Recovery with Token""" |
| 323 | # هش کردن توکن برای مقایسه | # Hash Token for Comparison |
| 352 | # بررسی تاریخچه رمز عبور | # Check Password History |
| 357 | # بررسی نکنیم که رمز فعلی در تاریخچه نباشد (اختیاری) | # Don't check that current password is not in history (optional) |
| 361 | # تنظیم رمز عبور جدید | # Set New Password |
| 364 | # ذخیره رمز قبلی در تاریخچه | # Save Previous Password in History |
| 374 | # فقط ۵ رمز آخر را نگه دار | # Keep Only Last 5 Passwords |
| 377 | # ریست کردن تلاش‌های ناموفق | # Reset Failed Attempts |
| 381 | # استفاده از توکن | # Use Token |
| 384 | # لاگ فعالیت | # Activity Log |
| 388 | description='بازیابی موفق رمز عبور', | description='Successful Password Recovery', |
| 393 | # خروج از تمام نشست‌ها به جز نشست فعلی | # Logout from All Sessions Except Current |
| 402 | # ==================== تأیید دو مرحله‌ای (2FA) ==================== | # ==================== Two-Factor Authentication (2FA) ==================== |
| 409 | """فعال‌سازی احراز هویت دو مرحله‌ای""" | """Enable Two-Factor Authentication""" |
| 425 | # ذخیره秘密 و فعال‌سازی | # Save Secret and Enable |
| 429 | # تولید کدهای پشتیبان | # Generate Backup Codes |
| 435 | # پاک کردن session | # Clear Session |
| 529 | """صفحه تأیید کد 2FA هنگام ورود""" | """2FA Code Verification Page During Login""" |
| 531 | user_id = session.get('2fa_pending_user_id') | user_id = session.get('2fa_pending_user_id') |
| 533 | flash("❌ No pending login found. Please log in first.", "warning") | flash("❌ No pending login found. Please log in first.", "warning") |
| 648 | """لغو همه نشست‌های فعال""" | """Cancel All Active Sessions""" |
| 657 | # ==================== گزارش فعالیت کاربران ==================== | # ==================== User Activity Log ==================== |
| 661 | """نمایش گزارش فعالیت‌های کاربر""" | """Display User Activity Log""" |
