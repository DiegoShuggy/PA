// src/translations/i18n.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Importa tus archivos de traducción
import en from './en/en.json';
import es from './es/es.json';
import fr from './fr/fr.json';

i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
        debug: true,
        lng: 'es', // Idioma por defecto
        resources: {
            en: { translation: en },
            es: { translation: es },
            fr: { translation: fr }
        },
        fallbackLng: 'es',
        interpolation: {
            escapeValue: false,
        }
    });

export default i18n;