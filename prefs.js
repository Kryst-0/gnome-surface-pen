import Adw from 'gi://Adw';
import Gio from 'gi://Gio';
import Gtk from 'gi://Gtk';
import {ExtensionPreferences} from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

export default class SurfacePenPreferences extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const settings = this.getSettings();
        const page = new Adw.PreferencesPage({title: 'Surface Pen', icon_name: 'document-edit-symbolic'});
        window.add(page);
        const group = new Adw.PreferencesGroup({title: 'Pulsante superiore Bluetooth',
            description: 'Associa prima la penna dalle impostazioni Bluetooth. Il pulsante laterale dello stilo resta invariato.'});
        page.add(group);
        const apps = Gio.AppInfo.get_all().filter(app => app.should_show() && app.get_id())
            .sort((a, b) => a.get_display_name().localeCompare(b.get_display_name()));
        for (const [gesture, title] of [['single', 'Clic'], ['double', 'Doppio clic'], ['hold', 'Pressione lunga']]) {
            const key = `${gesture}-app`;
            const current = settings.get_string(key);
            const choices = [{id: '', name: 'Nessuna azione'}, ...apps.map(app => ({
                id: app.get_id(), name: app.get_display_name(),
            }))];
            if (current && !choices.some(app => app.id === current))
                choices.push({id: current, name: `Non installata: ${current}`});
            const row = new Adw.ComboRow({title, enable_search: true,
                model: Gtk.StringList.new(choices.map(app => app.name)),
                selected: Math.max(0, choices.findIndex(app => app.id === current))});
            row.connect('notify::selected', () => settings.set_string(key, choices[row.selected].id));
            group.add(row);
        }
        const modes = ['auto', 'on', 'off'];
        const slides = new Adw.ComboRow({title: 'Modalità slide',
            subtitle: 'Clic: avanti. Doppio clic: indietro. La pressione lunga apre sempre l’app scelta.',
            model: Gtk.StringList.new(['Automatica (presentazione a schermo intero)', 'Sempre', 'Disattivata']),
            selected: modes.indexOf(settings.get_string('presentation'))});
        slides.connect('notify::selected', () => settings.set_string('presentation', modes[slides.selected]));
        group.add(slides);
        const shortcuts = new Adw.PreferencesGroup({title: 'Scorciatoie della penna',
            description: 'Acceleratori GTK separati da virgole. Le impostazioni valgono anche per gli stessi tasti su una tastiera. Nessuna modifica alle scorciatoie di sistema.'});
        page.add(shortcuts);
        for (const [gesture, title] of [['single', 'Clic'], ['double', 'Doppio clic'], ['hold', 'Pressione lunga']]) {
            const key = `${gesture}-shortcut`;
            const row = new Adw.EntryRow({title, text: settings.get_strv(key).join(', '), show_apply_button: true});
            row.connect('apply', () => {
                const values = row.text.split(',').map(s => s.trim()).filter(Boolean);
                if (values.every(value => Gtk.accelerator_parse(value)[0])) {
                    settings.set_strv(key, values);
                    row.remove_css_class('error');
                } else row.add_css_class('error');
            });
            shortcuts.add(row);
        }
        const reset = new Gtk.Button({label: 'Ripristina scorciatoie predefinite', halign: Gtk.Align.START});
        reset.connect('clicked', () => {
            for (const gesture of ['single', 'double', 'hold']) settings.reset(`${gesture}-shortcut`);
            window.close();
        });
        shortcuts.add(reset);
    }
}
