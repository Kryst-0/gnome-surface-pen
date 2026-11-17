#!/usr/bin/env python3
import configparser
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile

CONFIG = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'surface-pen/settings.json'
DEFAULT = {'single': '', 'double': '', 'hold': '', 'presentation': 'auto'}

def load():
    try:
        return DEFAULT | json.loads(CONFIG.read_text())
    except (OSError, ValueError):
        return DEFAULT.copy()

def apps():
    found = {}
    roots = [Path(os.environ.get('XDG_DATA_HOME', Path.home()/'.local/share'))]
    roots += [Path(p) for p in os.environ.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share').split(':')]
    seen = set()
    for root in roots:
        directory = root/'applications'
        for path in sorted(directory.rglob('*.desktop')):
            appid = str(path.relative_to(directory)).replace('/', '-')
            if appid in seen:
                continue
            seen.add(appid)
            p = configparser.ConfigParser(interpolation=None, strict=False)
            try:
                p.read(path)
                d = p['Desktop Entry']
                if d.get('Type') != 'Application' or any(d.get(k,'false').lower() == 'true' for k in ('Hidden','NoDisplay')):
                    continue
                if not d.get('Exec') and d.get('DBusActivatable','false').lower() != 'true':
                    continue
                found[appid] = {'id': appid, 'name': d.get('Name[it]', d.get('Name', appid))[:200], 'path': str(path)}
            except (OSError, configparser.Error, KeyError):
                continue
    return sorted(found.values(), key=lambda a:a['name'].casefold())

def save(value):
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=CONFIG.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(value, f)
        os.replace(name, CONFIG)
    finally:
        if os.path.exists(name): os.unlink(name)

def presentation(window, mode):
    if mode == 'off': return False
    if mode == 'on': return True
    if not (window.get('fullscreen') or window.get('fullscreenClient')): return False
    cls = window.get('class','').lower()
    title = window.get('title','').lower()
    firefox_pdf = ('firefox' in cls and bool(re.search(r'\.pdf(?=$|[\s?#—–|)])', title)))
    return (firefox_pdf or 'impress' in cls or 'impress' in title or cls in ('soffice','libreoffice')
            or any(x in cls for x in ('okular','evince','papers','atril','pdfpc'))
            or any(x in title for x in ('google slides','presentazioni google','powerpoint','slide show','presentazione','slideshow')))

def run(cmd):
    result = subprocess.run(cmd, check=True, text=True, capture_output=True, timeout=8).stdout
    # hyprctl can return status 0 even when Lua execution fails.
    if result.lstrip().startswith(('error:', 'Error', 'Invalid')):
        raise ValueError(result.strip())
    return result

def main():
    op = sys.argv[1]
    cfg = load()
    if op == 'state':
        devices = Path('/proc/bus/input/devices').read_text()
        return {'settings':cfg,'apps':apps(),'connected':'surface pen' in devices.lower() or 'surface slim pen' in devices.lower()}
    if op == 'set':
        key, value = sys.argv[2:4]
        if key not in DEFAULT: raise ValueError('Unknown setting')
        if key == 'presentation':
            if value not in ('auto','on','off'): raise ValueError('Invalid mode')
        elif value and value not in {a['id'] for a in apps()}:
            raise ValueError('Application not available')
        cfg[key] = value
        save(cfg)
        return {'ok':True}
    if op in ('single','double','hold'):
        window = json.loads(run(['hyprctl','activewindow','-j']))
        if op != 'hold' and presentation(window, cfg['presentation']):
            address = window.get('address','')
            if not re.fullmatch(r"0x[0-9a-fA-F]+", address): raise ValueError("Invalid active window")
            key = 'Right' if op == 'single' else 'Left'
            expression = ('hl.dispatch(hl.dsp.send_shortcut({'
                          f'mods = "", key = "{key}", window = "address:{address}"'
                          '}))')
            run(['hyprctl', 'eval', expression])
            return {'ok':True,'action':'slide'}
        app = next((a for a in apps() if a['id'] == cfg[op]), None)
        if app:
            subprocess.Popen(['gio','launch',app['path']], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        return {'ok':True,'action':'app' if app else 'none'}
    raise ValueError('Unknown operation')

if __name__ == '__main__':
    try:
        print(json.dumps(main(), ensure_ascii=False))
    except (ValueError, OSError, subprocess.SubprocessError) as e:
        print(json.dumps({'error':str(e)}))
        sys.exit(1)
