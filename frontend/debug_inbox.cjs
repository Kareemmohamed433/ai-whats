const WebSocket = require('ws');
const http = require('http');
const { spawn } = require('child_process');

const edgePath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const proc = spawn(edgePath, [
  '--headless',
  '--remote-debugging-port=9224',
  '--disable-gpu',
  '--no-sandbox',
  'http://localhost:5173/login'
]);

setTimeout(() => {
  http.get('http://127.0.0.1:9224/json', (res) => {
    let raw = '';
    res.on('data', c => raw += c);
    res.on('end', () => {
      const tabs = JSON.parse(raw);
      const pageTab = tabs.find(t => t.type === 'page');
      if (!pageTab) {
        console.log('No page tab');
        proc.kill();
        return;
      }
      const ws = new WebSocket(pageTab.webSocketDebuggerUrl);
      let id = 1;

      ws.on('open', () => {
        ws.send(JSON.stringify({ id: id++, method: 'Runtime.enable' }));
        ws.send(JSON.stringify({ id: id++, method: 'Page.enable' }));

        // Get login token
        const loginPayload = JSON.stringify({ email: 'admin@nexorasolutions.com', password: 'Nexora#Secure2026' });
        const postReq = http.request({
          hostname: '127.0.0.1',
          port: 5000,
          path: '/api/auth/login',
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(loginPayload) }
        }, (authRes) => {
          let authRaw = '';
          authRes.on('data', d => authRaw += d);
          authRes.on('end', () => {
            const authJson = JSON.parse(authRaw);
            const token = authJson.token || authJson.access_token;
            console.log('Login token received. Navigating to /inbox...');

            const codeToInject = `
              localStorage.setItem('token', '${token}');
              localStorage.setItem('nexora_token', '${token}');
              localStorage.setItem('nexora_user', JSON.stringify(${JSON.stringify(authJson.user)}));
              window.location.href = 'http://localhost:5173/inbox';
            `;

            ws.send(JSON.stringify({
              id: id++,
              method: 'Runtime.evaluate',
              params: { expression: codeToInject }
            }));
          });
        });
        postReq.write(loginPayload);
        postReq.end();
      });

      ws.on('message', (msg) => {
        const data = JSON.parse(msg);
        if (data.result && data.result.result) {
          console.log('[EVAL RESULT]', data.result.result.value);
        }
        if (data.method === 'Runtime.consoleAPICalled') {
          console.log('[CONSOLE]', data.params.type, data.params.args.map(a => a.value || a.description).join(' '));
        }
        if (data.method === 'Runtime.exceptionThrown') {
          console.log('>>> [EXCEPTION THROWN] <<<');
          console.log(JSON.stringify(data.params.exceptionDetails, null, 2));
        }
      });

      setTimeout(() => {
        ws.send(JSON.stringify({
          id: id++,
          method: 'Runtime.evaluate',
          params: { expression: 'document.body.innerHTML.slice(0, 500)' }
        }));
      }, 5000);

      setTimeout(() => {
        ws.close();
        proc.kill();
        process.exit(0);
      }, 7000);
    });
  });
}, 2000);
