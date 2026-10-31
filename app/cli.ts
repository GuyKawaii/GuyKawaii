import {readFile,writeFile,mkdir,rename} from 'node:fs/promises';
import {collect} from './collect.js';
import {render} from './render.js';
import {validateProfile} from './model.js';
const command=process.argv[2];
try{
 if(!['collect','render','preview','update'].includes(command))throw new Error('Use collect, render, preview, or update');
 let profile;
 if(command==='collect'||command==='update'){
  profile=await collect(process.env.GH_TOKEN??'');
  await mkdir('.cache',{recursive:true});await writeFile('.cache/profile.json.tmp',JSON.stringify(profile,null,2));await rename('.cache/profile.json.tmp','.cache/profile.json');
  console.log('Aggregate snapshot collected successfully');
 }
 if(command==='collect')process.exit(0);
 const preview=command==='preview';
 profile??=validateProfile(JSON.parse(await readFile(preview?'fixtures/profile.json':'.cache/profile.json','utf8')));
 await render(profile,preview?'out/typescript-preview':'out',preview);
 console.log(preview?'Preview ready: out/typescript-preview/fetch.gif':'Profile exported: out/fetch.gif');
}catch(error){console.error(error instanceof Error?error.message:'Profile update failed');process.exitCode=1;}
