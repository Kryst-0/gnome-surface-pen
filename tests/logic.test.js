import {test} from 'node:test';
import assert from 'node:assert/strict';
import {presentation, slideReady} from '../logic.js';

test('automatic slides require a recognised fullscreen window', () => {
    for (const cls of ['libreoffice-impress', 'okular', 'org.gnome.Papers', 'org.gnome.Evince', 'pdfpc']) {
        assert.equal(presentation({class: cls, fullscreen: true}, 'auto'), true);
        assert.equal(presentation({class: cls, fullscreen: false}, 'auto'), false);
    }
    assert.equal(presentation({class: 'terminal', fullscreen: true}, 'auto'), false);
    assert.equal(presentation({class: 'firefox', title: 'Talk - Google Slides', fullscreen: true}, 'auto'), true);
});
test('Firefox PDF recognition excludes misleading suffixes and normal windows', () => {
    for (const title of ['Talk.pdf — Mozilla Firefox', 'Talk.pdf', 'Talk.pdf?download'])
        assert.equal(presentation({class: 'firefox', title, fullscreen: true}, 'auto'), true);
    for (const title of ['News', 'Talk.pdf.exe'])
        assert.equal(presentation({class: 'firefox', title, fullscreen: true}, 'auto'), false);
    assert.equal(presentation({class: 'firefox', title: 'Talk.pdf', fullscreen: false}, 'auto'), false);
});
test('manual modes and missing focused window', () => {
    assert.equal(presentation(null, 'on'), false);
    assert.equal(presentation({}, 'on'), true);
    assert.equal(presentation({class: 'impress', fullscreen: true}, 'off'), false);
});
test('never inject slide into a changed window, with held modifiers, lock screen or after timeout', () => {
    const target = {};
    assert.equal(slideReady(target, target, 0, true, false), true);
    assert.equal(slideReady(target, {}, 0, true, false), false);
    assert.equal(slideReady(target, target, 64, true, false), false);
    assert.equal(slideReady(target, target, 0, false, false), false);
    assert.equal(slideReady(target, target, 0, true, true), false);
    assert.equal(slideReady(null, null, 0, true, false), false);
});
