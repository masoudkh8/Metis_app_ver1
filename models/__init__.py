# models/__init__.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models

from .user import User, UserProfile
from .order import Order
from .notification import Notification
from .message import Message
from .provider import DataProvider
from .port import Port
from .premium_request import PremiumRequest
from .magazine import Magazine, MagazineIssue, SponsorshipRequest, AdvertisementRequest, Subscription

# New models for 16-section platform
from .trust_score import TrustScore
from .gamification import UserBadge, UserProgress, SeasonalChallenge, ChallengeParticipant
from .trade_credit import TradeCreditAccount, CreditTransaction, CreditRule
from .consortium import ConsortiumProject, ConsortiumMember, ConsortiumContract, PartnerMatch

# Marketplace & Products (بخش ۹)
from .product import Product, RFQ, RFQProposal, ProductComparison, FavoriteProduct

# Financial Layer (بخش ۱۰)
from .wallet import Wallet, WalletTransaction, EscrowTransaction, ExchangeRate, FinancialReport

# Learning Hub (بخش ۱۴)
from .course import Course, CourseModule, CourseLesson, CourseEnrollment, LessonProgress, Certificate, Webinar, WebinarRegistration, LearningPath

# CRM & Leads (بخش ۱۲)
from .lead import Lead, LeadInteraction, LeadTask, Campaign, CampaignLead, CampaignAnalytics, EmailTemplate, AutomationRule

# Integrations (بخش ۱۱)
from .integration import ExternalIntegration, IntegrationLog, WebhookSubscription, WebhookDelivery, LinkedInProfile, LinkedInPost, WhatsAppContact, LogisticsProvider, LogisticsQuote, APICache

# AI Core (بخش ۱)
from .ai_chat import Conversation, ChatMessage, AIRecommendation, CustomizationProfile, ContentGenerationRequest

# Smart Map & Logistics (بخش ۲)
from .smart_map import Country, CustomsData, RiskEvent, TradeRoute, ShipmentTracking

# i18n & Localization (بخش ۱۳)
from .i18n import Language, TranslationKey, Translation, LocalizationSettings

# Data Intelligence (بخش ۸)
from .data_intelligence import MarketTrend, CompetitorAnalysis, DemandForecast, TradeStatistic, CustomReport, DataAlert

# Social Network (بخش سوشال - مرحله ۱)
from .social import Follow, Post, Comment, Like, update_user_relationships

# Exhibition Hall (نمایشگاه آنلاین - مرحله ۲)
from .exhibition import (
    Exhibition, Booth, BoothVisit, BoothInteraction, BoothAppointment, ExhibitionVisit,
    ExhibitionStatus, BoothType,
    init_exhibition_db
)

# Trading Hall (تالار معاملاتی - مرحله ۲)
from .trading import (
    TradingPair, TradingWallet, TradingWalletTransaction, TradeOrder, Trade, MarketData, TradingSetting,
    OrderType, OrderSide, OrderStatus,
    init_trading_db
)

# Authentication & Security Models (امنیت و احراز هویت)
from .auth import PasswordResetToken, LoginSession, ActivityLog, EmailVerificationToken, TwoFactorBackupCode

# Initialize social relationships after all models are imported
update_user_relationships()