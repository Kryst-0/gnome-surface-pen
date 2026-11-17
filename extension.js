import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import Meta from 'gi://Meta';
import Shell from 'gi://Shell';
import St from 'gi://St';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';
import {presentation, slideReady} from './logic.js';

const GESTURES = ['single', 'double', 'hold'];
const LABELS = {single: 'Clic', double: 'Doppio clic', hold: 'Pressione lunga'};

export default class SurfacePen extends Extension {
    enable() {
        this._settings = this.getSettings();
        this._sources = new Set();
        this._bindings = [];
        this._keyboard = null;
        this._indicator = new PanelMenu.Button(0.0, 'Surface Pen');
        this._indicator.add_child(new St.Icon({
            icon_name: 'document-edit-symbolic', style_class: 'system-status-icon',
        }));
        this._status = new PopupMenu.PopupMenuItem('Premi il pulsante della penna', {reactive: false});
        this._indicator.menu.addMenuItem(this._status);
        this._indicator.menu.addAction('Configura Surface Pen…', () => this.openPreferences());
        this._indicator.menu.addAction('Impostazioni Bluetooth…', () => {
            try {
                Gio.DesktopAppInfo.new('gnome-bluetooth-panel.desktop')?.launch([], global.create_app_launch_context(0, -1));
            } catch (e) { this._error(e); }
        });
        Main.panel.addToStatusArea(this.uuid, this._indicator);
        for (const gesture of GESTURES) {
            const name = `${gesture}-shortcut`;
            const action = Main.wm.addKeybinding(name, this._settings,
                Meta.KeyBindingFlags.IGNORE_AUTOREPEAT, Shell.ActionMode.NORMAL,
                () => this._activate(gesture));
            this._bindings.push(name);
            if (action === Meta.KeyBindingAction.NONE)
                Main.notify('Surface Pen', `Scorciatoia ${LABELS[gesture]} non disponibile. Controlla le preferenze.`);
        }
    }

    _error(error) {
        console.error(`[Surface Pen] ${error}`);
        Main.notify('Surface Pen', `${error.message ?? error}`);
    }

    _activate(gesture) {
        try {
            this._status.label.text = `Ultimo gesto: ${LABELS[gesture]}`;
            const window = global.display.focus_window;
            const info = window ? {class: window.get_wm_class(), title: window.get_title(),
                fullscreen: window.is_fullscreen()} : null;
            if (gesture !== 'hold' && presentation(info, this._settings.get_string('presentation'))) {
                this._sendSlide(window, gesture === 'single' ? Clutter.KEY_Right : Clutter.KEY_Left);
                return;
            }
            const id = this._settings.get_string(`${gesture}-app`);
            if (!id) return;
            const app = Gio.DesktopAppInfo.new(id);
            if (!app) throw new Error(`App non disponibile: ${id}. Sceglila nelle preferenze.`);
            app.launch([], global.create_app_launch_context(0, -1));
        } catch (e) { this._error(e); }
    }

    _sendSlide(window, key) {
        // The pen emits Super with its function key. Wait for physical release
        // rather than sending Super+Right/Left (a window-management shortcut).
        const deadline = GLib.get_monotonic_time() + 1500000;
        const source = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 20, () => {
            const expired = GLib.get_monotonic_time() >= deadline;
            const current = global.display.focus_window;
            const normal = Main.actionMode === Shell.ActionMode.NORMAL;
            const mask = Clutter.ModifierType.SHIFT_MASK | Clutter.ModifierType.CONTROL_MASK |
                Clutter.ModifierType.MOD1_MASK | Clutter.ModifierType.SUPER_MASK;
            const modifiers = global.get_pointer()[2] & mask;
            if (expired || current !== window || !normal) {
                this._sources.delete(source);
                return GLib.SOURCE_REMOVE;
            }
            if (!slideReady(window, current, modifiers, normal, expired))
                return GLib.SOURCE_CONTINUE;
            this._sources.delete(source);
            try {
                this._keyboard ??= global.stage.context.get_backend().get_default_seat()
                    .create_virtual_device(Clutter.InputDeviceType.KEYBOARD_DEVICE);
                this._keyboard.notify_keyval(GLib.get_monotonic_time(),
                    key, Clutter.KeyState.PRESSED);
                this._keyboard.notify_keyval(GLib.get_monotonic_time(),
                    key, Clutter.KeyState.RELEASED);
            } catch (e) { this._error(e); }
            return GLib.SOURCE_REMOVE;
        });
        this._sources.add(source);
    }

    disable() {
        for (const name of this._bindings ?? []) Main.wm.removeKeybinding(name);
        this._bindings = [];
        for (const source of this._sources ?? []) GLib.Source.remove(source);
        this._sources?.clear();
        this._sources = null;
        this._keyboard = null;
        this._indicator?.destroy();
        this._indicator = null;
        this._status = null;
        this._settings = null;
    }
}
