from pathlib import Path
import shutil,json,time,shlex
source=Path(__file__).parent
home=Path.home()
plugin=home/'.config/omarchy/plugins/krysto.surface-pen'
config=home/'.config/omarchy/shell.json'
bindings=home/'.config/hypr/bindings.lua'
if not config.is_file() or not bindings.is_file():
    raise SystemExit('Richiede Omarchy Shell e Hyprland con bindings.lua; nessun file modificato.')
data=json.loads(config.read_text())
if not isinstance(data.get('bar',{}).get('layout',{}).get('right'),list):
    raise SystemExit('Layout barra non riconosciuto; nessun file modificato.')
plugin.mkdir(parents=True,exist_ok=True)
for name in ('Panel.qml','control.py','manifest.json','i18n'):
    src=source/name
    if src.is_dir():shutil.copytree(src,plugin/name,dirs_exist_ok=True)
    else:shutil.copy2(src,plugin/name)
config=home/'.config/omarchy/shell.json'
data=json.loads(config.read_text())
if not any(x['id']=='krysto.surface-pen' for values in data['bar']['layout'].values() for x in values):
    shutil.copy2(config,str(config)+'.bak.surface-pen-'+str(int(time.time())))
    data['bar']['layout']['right'].insert(0,{'id':'krysto.surface-pen'})
    config.write_text(json.dumps(data,indent=2)+'\n')
bindings=home/'.config/hypr/bindings.lua'
text=bindings.read_text()
if '-- Surface Pen Bluetooth button' not in text:
    shutil.copy2(bindings,str(bindings)+'.bak.surface-pen-'+str(int(time.time())))
    text+='\n-- Surface Pen Bluetooth button (single / double / hold).\n'
    for modifier in ('SUPER + ', ''):
        for key,action in [('F20','single'),('F19','double'),('F18','hold')]:
            if modifier:
                key = {'F20':'XF86AudioMicMute', 'F19':'F19', 'F18':'XF86Launch9'}[key]
            command=json.dumps('python3 '+shlex.quote(str(plugin/'control.py'))+' '+action)
            text+=f'o.bind("{modifier}{key}", "Surface Pen: {action}", {command})\n'
    bindings.write_text(text)
settings=home/'.config/surface-pen/settings.json'
if not settings.exists():
    settings.parent.mkdir(parents=True,exist_ok=True)
    settings.write_text(json.dumps({'single':'com.github.xournalpp.xournalpp.desktop','double':'libreoffice-impress.desktop','hold':'omawrite.desktop','presentation':'auto'},indent=2)+'\n')
print('Installed',plugin)
