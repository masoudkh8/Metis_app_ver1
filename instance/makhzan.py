    def get_locale():
        # اولویت ۱: session
        lang = session.get('lang')
        if lang:
            return 'fa_IR' if lang.startswith('fa') else lang

        # اولویت ۲: آرگومان URL
        lang = request.args.get('lang')
        if lang:
            session['lang'] = 'fa_IR' if lang.startswith('fa') else lang
            return session['lang']

        # اولویت ۳: مرورگر کاربر
        return request.accept_languages.best_match(['fa_IR', 'en'], 'fa_IR')
