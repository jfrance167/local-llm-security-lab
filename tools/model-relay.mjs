/** Disposable VM inference relay. No payload logging, keys, remote routes or model pulls.
 * Run with installed Node; binds Windows loopback port 11435.
 * POST /v1/chat/completions or /api/chat, exact installed model, <=32KiB.
 * Operator stops with Ctrl+C; health and discovery endpoints intentionally absent.
 */
import http from 'node:http';
import {pathToFileURL} from 'node:url';
const MODEL = 'qwen3.5:2b';
export function createHandler({fetchImpl = fetch, log = line => process.stdout.write(line)} = {}) {
let busy = false;
return async (req, res) => {
  const reply = (status, value) => {
    if (!res.destroyed) { res.writeHead(status, {'content-type':'application/json'}); res.end(JSON.stringify(value)); }
  };
  if (req.method !== 'POST' || !['/v1/chat/completions', '/api/chat'].includes(req.url)) {
    reply(404, {error:'route denied'}); req.resume(); return;
  }
  if (busy) { reply(429, {error:'one request at a time'}); req.resume(); return; }
  let bytes = 0;
  let acquired = false;
  try {
    const chunks = [];
    for await (const chunk of req) {
      bytes += chunk.length;
      if (bytes > 32768) { reply(413, {error:'request too large'}); req.destroy(); return; }
      chunks.push(chunk);
    }
    const body = JSON.parse(Buffer.concat(chunks).toString('utf8'));
    if (!body || typeof body !== 'object' || Array.isArray(body) || body.model !== MODEL || !Array.isArray(body.messages) || body.messages.length < 1 || body.messages.length > 12 ||
        body.messages.some(m => !m || !['system','user','assistant'].includes(m.role) || typeof m.content !== 'string') ||
        body.stream === true) { reply(400, {error:'model or message denied'}); return; }
    const cap = body.max_tokens ?? body.options?.num_predict ?? 800;
    if (!Number.isInteger(cap) || cap < 1 || cap > 1600) { reply(400, {error:'token cap denied'}); return; }
    if (busy) { reply(429, {error:'one request at a time'}); return; }
    busy = true;
    acquired = true;
    const started = Date.now();
    const upstream = await fetchImpl('http://127.0.0.1:11434/api/chat', {
      method:'POST', redirect:'error', signal:AbortSignal.timeout(120000),
      headers:{'content-type':'application/json'},
      body:JSON.stringify({model:MODEL, messages:body.messages, stream:false, think:false,
        options:{temperature:0, seed:42, num_ctx:8192, num_predict:cap}}),
    });
    if (!upstream.ok) throw new Error('local model unavailable');
    const data = await upstream.json();
    if (data.model !== MODEL || typeof data.message?.content !== 'string') throw new Error('invalid local model response');
    const usage = {prompt_tokens:data.prompt_eval_count ?? 0, completion_tokens:data.eval_count ?? 0};
    usage.total_tokens = usage.prompt_tokens + usage.completion_tokens;
    log(JSON.stringify({event:'inference', model:MODEL, durationMs:Date.now()-started, ...usage})+'\n');
    reply(200, req.url === '/api/chat' ? data : {id:'local-pilot', object:'chat.completion', model:MODEL,
      choices:[{index:0,message:{role:'assistant',content:data.message.content},finish_reason:data.done_reason ?? 'stop'}], usage});
  } catch (error) {
    reply(error instanceof SyntaxError ? 400 : 502, {error:error instanceof SyntaxError ? 'invalid JSON' : 'local inference failed'});
  } finally { if (acquired) busy = false; }
};
}
export function createRelayServer(options) {
const server = http.createServer(createHandler(options));
server.requestTimeout = 150000;
server.headersTimeout = 10000;
server.maxConnections = 4;
return server;
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  createRelayServer().listen(11435, '127.0.0.1', () => process.stdout.write('local-only relay ready\n'));
}
