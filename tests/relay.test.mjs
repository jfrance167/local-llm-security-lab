import test from 'node:test';
import assert from 'node:assert/strict';
import {createHandler, createRelayServer} from '../tools/model-relay.mjs';

const good = {model:'qwen3.5:2b',messages:[{role:'user',content:'synthetic text'}],max_tokens:128};
function request(body = good, url = '/v1/chat/completions', method = 'POST') {
  return {url,method,resume(){},destroy(){this.destroyed=true;},
    async *[Symbol.asyncIterator](){yield Buffer.from(typeof body === 'string' ? body : JSON.stringify(body));}};
}
async function invoke(handler, req) {
  const res = {destroyed:false,writeHead(status){this.status=status;},end(data){this.body=JSON.parse(data);}};
  await handler(req,res);
  return res;
}
function fixture() {
  const calls = [], logs = [];
  const handler = createHandler({log:line=>logs.push(line),fetchImpl:async(url,options)=>{
    calls.push({url,options});
    return {ok:true,json:async()=>({model:'qwen3.5:2b',message:{content:'synthetic answer'},
      prompt_eval_count:4,eval_count:2,done_reason:'stop'})};
  }});
  return {handler,calls,logs};
}
test('fixed upstream, forced offline controls and no payload logging',async()=>{
  const {handler,calls,logs}=fixture();
  const res=await invoke(handler,request({...good,options:{num_ctx:999999},temperature:100,think:true}));
  assert.equal(res.status,200);
  assert.equal(calls[0].url,'http://127.0.0.1:11434/api/chat');
  assert.equal(calls[0].options.redirect,'error');
  const sent=JSON.parse(calls[0].options.body);
  assert.equal(sent.think,false);
  assert.equal(sent.stream,false);
  assert.deepEqual(sent.options,{temperature:0,seed:42,num_ctx:8192,num_predict:128});
  assert.equal(res.body.usage.total_tokens,6);
  assert(!logs[0].includes('synthetic text'));
  assert(!logs[0].includes('synthetic answer'));
});
test('native chat route preserves native response',async()=>{
  const {handler}=fixture();
  const res=await invoke(handler,request({...good,max_tokens:undefined,options:{num_predict:64}},'/api/chat'));
  assert.equal(res.status,200);
  assert.equal(res.body.message.content,'synthetic answer');
});
test('denied methods and paths never call model',async()=>{
  const {handler,calls}=fixture();
  for(const req of [request(good,'/api/pull'),request(good,'/api/tags'),request(good,'/v1/models'),
    request(good,'/v1/chat/completions','GET'),request(good,'/v1/chat/completions?x=1')]) {
    assert.equal((await invoke(handler,req)).status,404);
  }
  assert.equal(calls.length,0);
});
test('malformed or unauthorized bodies never call model',async()=>{
  const {handler,calls}=fixture();
  for(const body of [null,[],1,'{bad}',{...good,model:'cloud-model'},
    {...good,messages:[]},{...good,messages:Array(13).fill(good.messages[0])},
    {...good,messages:[{role:'tool',content:'x'}]},{...good,messages:[{role:'user',content:3}]},
    {...good,stream:true}]) {
    assert.equal((await invoke(handler,request(body))).status,400);
  }
  assert.equal(calls.length,0);
});
test('token cap and byte cap denied before inference',async()=>{
  const {handler,calls}=fixture();
  for(const cap of [0,1601,1.5,'128',-1,true]) {
    assert.equal((await invoke(handler,request({...good,max_tokens:cap}))).status,400);
  }
  assert.equal((await invoke(handler,request({...good,messages:[{role:'user',content:'x'.repeat(32769)}]}))).status,413);
  assert.equal(calls.length,0);
});
test('errors are redacted and busy state releases',async()=>{
  let calls=0;
  const handler=createHandler({log(){},fetchImpl:async()=>{calls++;throw new Error('PRIVATE_DETAIL');}});
  for(let i=0;i<2;i++) {
    const res=await invoke(handler,request());
    assert.equal(res.status,502);
    assert(!JSON.stringify(res.body).includes('PRIVATE_DETAIL'));
  }
  assert.equal(calls,2);
});
test('concurrent rejected request cannot clear active busy state',async()=>{
  let release, calls=0;
  const held=new Promise(resolve=>{release=resolve;});
  const handler=createHandler({log(){},fetchImpl:async()=>{calls++;await held;
    return {ok:true,json:async()=>({model:'qwen3.5:2b',message:{content:'ok'}})};}});
  const first=invoke(handler,request());
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal((await invoke(handler,request())).status,429);
  assert.equal((await invoke(handler,request())).status,429);
  assert.equal(calls,1);
  release();
  assert.equal((await first).status,200);
});
test('upstream model mismatch is rejected',async()=>{
  const handler=createHandler({log(){},fetchImpl:async()=>({ok:true,json:async()=>({model:'other',message:{content:'text'}})})});
  assert.equal((await invoke(handler,request())).status,502);
});
test('server resource limits set without starting listener',()=>{
  const server=createRelayServer();
  assert.equal(server.requestTimeout,150000);
  assert.equal(server.headersTimeout,10000);
  assert.equal(server.maxConnections,4);
  assert.equal(server.listening,false);
  server.close();
});
