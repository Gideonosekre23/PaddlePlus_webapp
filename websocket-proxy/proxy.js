const http = require('http');
const WebSocket = require('ws');
const urlModule = require('url');  // rename import to 'urlModule' to avoid confusion

const server = http.createServer();
const wss = new WebSocket.Server({ server });

wss.on('connection', (clientSocket, req) => {
  // Parse the query params from the request URL
  const params = urlModule.parse(req.url, true).query;
  const token = params.token;
  const realServerUrl = params.wsUrl;  // rename this variable
  console.log(token);
  console.log(realServerUrl);

  const realServerSocket = new WebSocket(realServerUrl, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  realServerSocket.on('open', () => {
    console.log('[Proxy] Connected to real server with Bearer token');
  });

  // Pipe messages from browser -> real server
  clientSocket.on('message', (msg) => {
    if (realServerSocket.readyState === WebSocket.OPEN) {
      realServerSocket.send(msg);
    }
  });

  // Pipe messages from real server -> browser
  realServerSocket.on('message', (msg) => {
    if (clientSocket.readyState === WebSocket.OPEN) {
      clientSocket.send(msg);
    }
  });

  // Handle closures
  clientSocket.on('close', () => realServerSocket.close());
  realServerSocket.on('close', () => clientSocket.close());

  // Handle errors
  realServerSocket.on('error', (err) => {
    console.error('[Proxy] Error with real server socket:', err);
    clientSocket.close();
  });
  clientSocket.on('error', (err) => {
    console.error('[Proxy] Error with client socket:', err);
    realServerSocket.close();
  });
});

const PORT = process.env.PORT || 8080;
server.listen(PORT, () => {
  console.log(`[Proxy] WebSocket proxy listening on port ${PORT}`);
});
