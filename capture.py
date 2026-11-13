"""Capture Apple Settings in an official Duo simulator; no third-party apps."""
import json
import pathlib
import struct
import subprocess
import tempfile
import time

out = pathlib.Path('captures')
out.mkdir(exist_ok=True)

def run(*args, required=True):
    print('RUN ' + ' '.join(args), flush=True)
    with tempfile.TemporaryFile(mode='w+') as log:
        try:
            limit = 360 if 'bootstatus' in args else 120
            result = subprocess.run(args, text=True, stdout=log, stderr=log, timeout=limit)
        except subprocess.TimeoutExpired:
            log.seek(0)
            details = log.read()
            (out / 'timeout.txt').write_text(' '.join(args) + '\n' + details)
            print(details[-4000:], flush=True)
            raise
        log.seek(0)
        result.stdout = log.read()
        result.stderr = result.stdout
    print(result.stdout[-3000:], flush=True)
    if required and result.returncode:
        raise RuntimeError(f'{args[0:3]}: {result.stderr[-2000:]}')
    return result

devices = json.loads(run('xcrun', 'simctl', 'list', 'devices', 'available', '--json').stdout)
matches = [(runtime, d) for runtime, group in devices['devices'].items()
           for d in group if 'Duo' in d['name'] and d.get('isAvailable', True)]
if not matches:
    raise RuntimeError('No available official iPhone Duo simulator in this runner image')
runtime, device = sorted(matches, key=lambda item: item[0], reverse=True)[0]
udid = device['udid']
metadata = {'device': device['name'], 'runtime': runtime,
            'environment': 'GitHub-hosted official Apple simulator, not physical hardware',
            'application': 'com.apple.Preferences', 'captures': []}
(out / 'environment.json').write_text(json.dumps(metadata, indent=2))
print(f"Selected {device['name']} / {runtime}", flush=True)
run('open', '-a', '/Applications/Xcode.app/Contents/Applications/DeviceHub.app', required=False)
if device['state'] != 'Booted':
    run('xcrun', 'simctl', 'boot', udid)
run('xcrun', 'simctl', 'bootstatus', udid, '-b')
run('xcrun', 'simctl', 'status_bar', udid, 'override', '--time', '9:41',
    '--batteryState', 'charged', '--batteryLevel', '100', required=False)
run('xcrun', 'simctl', 'launch', udid, 'com.apple.Preferences')
time.sleep(5)
inventory = run('xcrun', 'simctl', 'io', udid, 'enumerate', required=False)
(out / 'displays.txt').write_text(inventory.stdout + inventory.stderr)
for label, display in [('default', None), ('outer', 'primary'), ('inner', 'primary-1')]:
    path = out / f'settings-{label}.png'
    args = ['xcrun', 'simctl', 'io', udid, 'screenshot']
    if display:
        args.append(f'--display={display}')
    result = run(*args, str(path), required=False)
    if result.returncode == 0 and path.exists():
        data = path.read_bytes()
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            width, height = struct.unpack('>II', data[16:24])
            metadata['captures'].append({'file': path.name, 'width': width,
                                         'height': height, 'bytes': len(data)})
    else:
        (out / f'{label}-error.txt').write_text(result.stdout + result.stderr)
(out / 'environment.json').write_text(json.dumps(metadata, indent=2))
print(json.dumps(metadata, indent=2), flush=True)
if not metadata['captures']:
    raise RuntimeError('No PNG screenshot produced')
