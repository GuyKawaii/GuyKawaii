import {test} from 'bun:test';
import assert from 'node:assert/strict';
import {readFile,mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import sharp from 'sharp';
import {validateProfile} from './model.js';
import {archiveTarget} from './collect.js';
import {render} from './render.js';

test('snapshot publishes only allowed aggregate fields',async()=>{
 const sample=JSON.parse(await readFile('fixtures/profile.json','utf8'));
 const profile=validateProfile({...sample,privateRepositories:['secret'],privateLines:123,token:'never-publish'});
 assert.equal(JSON.stringify(profile).includes('secret'),false);
 assert.equal('token' in profile,false);
 assert.throws(()=>validateProfile({...sample,totalLines:-1}));
 assert.throws(()=>validateProfile({...sample,totalLines:'123'}));
});
test('archive paths cannot escape the temporary workspace',()=>{
 const root=path.resolve('temporary-source');
 for(const entry of ['../escape','/absolute','folder/../../escape','folder\\escape'])assert.throws(()=>archiveTarget(root,entry));
 assert.equal(archiveTarget(root,'snapshot/src/index.ts'),path.join(root,'snapshot','src','index.ts'));
});
test('real browser export loops with visible portrait changes and steady text',async()=>{
 const directory=await mkdtemp(path.join(tmpdir(),'profile-test-'));
 try{
  const sample=validateProfile(JSON.parse(await readFile('fixtures/profile.json','utf8')));
  await render(sample,directory,true);
  const file=path.join(directory,'fetch.gif');
  const bytes=await readFile(file);
  const metadata=await sharp(bytes,{animated:true}).metadata();
  assert.equal(metadata.pages,32);assert.equal(metadata.loop,0);
  assert.equal(metadata.width,1920);assert.equal(metadata.pageHeight,1200);
  assert.equal(metadata.delay?.reduce((sum,delay)=>sum+delay,0),8000);
  const first=await sharp(bytes,{page:0}).ensureAlpha().raw().toBuffer();
  const second=await sharp(bytes,{page:1}).ensureAlpha().raw().toBuffer();
  const crop=async(data:Buffer,region:{left:number;top:number;width:number;height:number})=>sharp(data,{raw:{width:1920,height:1200,channels:4}}).extract(region).toBuffer();
  const text={left:900,top:200,width:935,height:840};
  assert.deepEqual(await crop(first,text),await crop(second,text));
  const portrait={left:88,top:224,width:720,height:720};
  assert.notDeepEqual(await crop(first,portrait),await crop(second,portrait));
 }finally{await rm(directory,{recursive:true,force:true});}
}, 60_000);
