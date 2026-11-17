#!/usr/bin/env python3
"""Build a GNOME extension zip; optionally install it for the current user."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent
FILES = ('extension.js', 'logic.js', 'prefs.js', 'metadata.json', 'LICENSE')

def build(output=None):
    metadata = json.loads((ROOT / 'metadata.json').read_text())
    output = Path(output) if output else ROOT / 'dist' / (metadata['uuid'] + '.shell-extension.zip')
    if not shutil.which('glib-compile-schemas'):
        raise SystemExit('Manca glib-compile-schemas: su Fedora installare glib2.')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='surface-pen-build-') as temp:
        stage = Path(temp)
        for name in FILES:
            shutil.copy2(ROOT / name, stage / name)
        shutil.copytree(ROOT / 'schemas', stage / 'schemas', ignore=shutil.ignore_patterns('gschemas.compiled'))
        subprocess.run(['glib-compile-schemas', '--strict', str(stage / 'schemas')], check=True)
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(stage.rglob('*')):
                if path.is_file(): archive.write(path, path.relative_to(stage))
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true', help='Installazione per utente tramite gnome-extensions')
    args = parser.parse_args()
    if args.install:
        if not shutil.which('gnome-extensions') or not shutil.which('gnome-shell'):
            parser.error('Richiede GNOME Shell e gnome-extensions; usare senza --install per generare lo ZIP.')
        import re
        version = subprocess.check_output(['gnome-shell', '--version'], text=True)
        major = re.search(r'\b(\d+)\.', version)
        supported = json.loads((ROOT / 'metadata.json').read_text())['shell-version']
        if not major or major[1] not in supported:
            parser.error('Versione GNOME non dichiarata compatibile: ' + version.strip())
    package = build()
    print(package)
    if args.install:
        subprocess.run(['gnome-extensions', 'install', '--force', str(package)], check=True)
        print('Disconnettersi dalla sessione e rientrare, poi eseguire:')
        print('gnome-extensions enable surface-pen@kryst-0.github.io')
