import gettext
import os
import json

class Translator:
    def __init__(self, lang='fa'):
        self.lang = lang
        self.translations = {}
        self.translator = None
        self.load_translations()
    
    def load_translations(self):
        """Load translation file"""
        # بارگذاری ترجمه‌های JSON (برای سازگاری با عقب)
        translations_path = os.path.join(os.path.dirname(__file__), '..', 'translations', f'{self.lang}.json')
        try:
            with open(translations_path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            self.translations = {}
        
        # بارگذاری ترجمه‌های gettext (.mo فایل)
        translations_dir = os.path.join(os.path.dirname(__file__), '..', 'translations')
        try:
            self.translator = gettext.translation('messages', localedir=translations_dir, languages=[self.lang])
        except FileNotFoundError:
            print(f"⚠️ Translation file for language {self.lang} not found. Using default translation.")
            self.translator = None
    
    def get(self, key, default=None):
        """Get translation with nested key (e.g. 'common.login')"""
        keys = key.split('.')
        value = self.translations
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default if default else key
        return value
    
    def gettext(self, message):
        """Translate text using gettext"""
        if self.translator:
            return self.translator.gettext(message)
        return message
    
    def t(self, key, **kwargs):
        """Translate key and replace variables"""
        # اول سعی کن از gettext استفاده کنی (برای متن‌های مستقیم)
        text = self.gettext(key)
        
        # اگر ترجمه‌ای پیدا نشد، از JSON استفاده کن
        if text == key:
            text = self.get(key)
        
        if kwargs:
            for k, v in kwargs.items():
                text = text.replace(f'{{{k}}}', str(v))
        return text

# نمونه جهانی
translator = Translator('fa')

def t(key, **kwargs):
    """Helper function for use in templates"""
    return translator.t(key, **kwargs)
