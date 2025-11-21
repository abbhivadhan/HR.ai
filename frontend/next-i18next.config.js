module.exports = {
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'es', 'fr', 'de', 'zh', 'ja'],
    localeDetection: true,
  },
  fallbackLng: 'en',
  debug: process.env.NODE_ENV === 'development',
  reloadOnPrerender: process.env.NODE_ENV === 'development',
  
  ns: ['common', 'auth', 'dashboard', 'assessment', 'jobs', 'interviews'],
  defaultNS: 'common',
  
  interpolation: {
    escapeValue: false,
  },
};