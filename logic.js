// Window classification shared with the original Omarchy plugin.
export function presentation(window, mode) {
    if (mode === 'off') return false;
    if (!window) return false;
    if (mode === 'on') return true;
    if (!window.fullscreen) return false;
    const cls = (window.class ?? '').toLowerCase();
    const title = (window.title ?? '').toLowerCase();
    const firefoxPdf = cls.includes('firefox') && /\.pdf(?=$|[\s?#—–|)])/.test(title);
    return firefoxPdf || cls.includes('impress') || title.includes('impress') ||
        ['soffice', 'libreoffice'].includes(cls) ||
        ['okular', 'evince', 'papers', 'atril', 'pdfpc'].some(x => cls.includes(x)) ||
        ['google slides', 'presentazioni google', 'powerpoint', 'slide show',
            'presentazione', 'slideshow'].some(x => title.includes(x));
}

export function slideReady(target, current, modifiers, normalMode, expired) {
    return Boolean(target && target === current && !modifiers && normalMode && !expired);
}
