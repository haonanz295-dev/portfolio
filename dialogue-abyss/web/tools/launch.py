"""Start the local service, wait until ready, then open its actual page."""
from pathlib import Path
import subprocess,sys,time,urllib.request,webbrowser,json,socket
root=Path(__file__).resolve().parents[1]
port=4196
url=f'http://127.0.0.1:{port}'
open_url=url+('/admin' if '--admin' in sys.argv else '/')
def ready():
    try:
        with urllib.request.urlopen(url+'/api/health',timeout=1) as r:return json.load(r).get('version')=='0.6'
    except Exception:return False
if ready():
    webbrowser.open(open_url)
    print('Game already running: '+url+' / Publisher: '+url+'/admin')
    sys.exit(0)
for candidate in range(4196,4210):
    with socket.socket() as probe:
        try:probe.bind(('127.0.0.1',candidate))
        except OSError:continue
        port=candidate;break
else:
    print('No free local port in 4196-4209. Close an old game service and retry.');sys.exit(1)
url=f'http://127.0.0.1:{port}'
open_url=url+('/admin' if '--admin' in sys.argv else '/')
proc=subprocess.Popen([sys.executable,str(root/'backend/server.py'),'--port',str(port)],cwd=root)
try:
    for _ in range(80):
        if ready():break
        if proc.poll() is not None:raise RuntimeError('Server stopped. Read the error above.')
        time.sleep(.15)
    else:raise RuntimeError('Server did not become ready.')
    webbrowser.open(open_url)
    print('Game: '+url+'\nPublisher: '+url+'/admin\nKeep this window open. Ctrl+C stops the service.',flush=True)
    proc.wait()
except KeyboardInterrupt:proc.terminate()
except Exception as error:
    print(error);proc.terminate();sys.exit(1)
