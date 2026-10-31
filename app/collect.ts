import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {mkdtemp, readFile, writeFile, rm, mkdir} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import AdmZip from 'adm-zip';
import sharp from 'sharp';
import {validateProfile, type Profile} from './model.js';
const execute=promisify(execFile);
const excluded='node_modules,vendor,dist,build,.venv,venv,__pycache__,coverage,.next,.nuxt';
interface Repo {id:number; full_name:string; private:boolean;fork:boolean;size:number;default_branch:string;owner:{login:string};stargazers_count:number}
export function archiveTarget(root:string, name:string):string {
  if(name.includes(':') || name.includes('\\') || path.posix.isAbsolute(name) || name.split('/').includes('..')) throw new Error('Unsafe archive entry');
  const target=path.resolve(root,name);
  if(!target.startsWith(path.resolve(root)+path.sep)) throw new Error('Unsafe archive entry');
  return target;
}
export async function collect(token:string):Promise<Profile>{
  if(!token) throw new Error('GH_TOKEN is required only for collection');
  async function request(route:string) {
    const response=await fetch('https://api.github.com'+route,{headers:{Authorization:`Bearer ${token}`,Accept:'application/vnd.github+json'},signal:AbortSignal.timeout(300000)});
    if(!response.ok) throw new Error(`GitHub request failed (${response.status})`);
    return response;
  }
  const user=await (await request('/user')).json() as {login:string;avatar_url:string};
  const repos:Repo[]=[];
  for(let page=1;;page++){
    const batch=await (await request(`/user/repos?affiliation=owner&per_page=100&page=${page}`)).json() as Repo[];
    repos.push(...batch.filter(repo=>repo.owner.login.toLowerCase()===user.login.toLowerCase()));
    if(batch.length<100)break;
  }
  let totalLines=0, commits=0;
  // Cache only on this runner; never publish or upload it as an artifact.
  await mkdir('.cache/counts',{recursive:true});
  for(const repo of repos){
    try {
      if(repo.size===0)continue;
      const head=await (await request(`/repos/${repo.full_name}/commits/${encodeURIComponent(repo.default_branch)}`)).json() as {sha:string};
      const cachePath=`.cache/counts/${repo.id}.json`;
      let cached:{sha:string;lines:number}|undefined;
      try{cached=JSON.parse(await readFile(cachePath,'utf8'));}catch{}
      let lines:number;
      if(cached?.sha===head.sha){lines=cached.lines;}else{
        const directory=await mkdtemp(path.join(tmpdir(),'profile-loc-'));
        try{
          const archive=await request(`/repos/${repo.full_name}/zipball/${head.sha}`);
          const zip=new AdmZip(Buffer.from(await archive.arrayBuffer()));
          for(const entry of zip.getEntries()){
            if(entry.isDirectory || ((entry.attr>>>16)&0o170000)===0o120000)continue;
            const target=archiveTarget(directory,entry.entryName);
            await mkdir(path.dirname(target),{recursive:true});await writeFile(target,entry.getData());
          }
          const {stdout}=await execute('cloc',['--json','--quiet','--skip-uniqueness',`--exclude-dir=${excluded}`,directory],{timeout:600000,maxBuffer:2e6});
          lines=JSON.parse(stdout).SUM?.code??0;
        }finally{await rm(directory,{recursive:true,force:true});}
        await writeFile(cachePath,JSON.stringify({sha:head.sha,lines}));
      }
      if(!Number.isSafeInteger(lines)||lines<0)throw new Error('Invalid line count');
      totalLines+=lines;
      if(!repo.fork){
        const response=await request(`/repos/${repo.full_name}/commits?per_page=1&sha=${encodeURIComponent(head.sha)}`);
        const last=response.headers.get('link')?.match(/[?&]page=(\d+)>; rel="last"/);
        commits+=last?Number(last[1]):((await response.json()) as unknown[]).length;
      }
    }catch{throw new Error('Repository collection failed; keeping the previous profile rather than publishing partial totals');}
  }
  const avatarResponse=await fetch(user.avatar_url,{signal:AbortSignal.timeout(30000)});
  if(!avatarResponse.ok)throw new Error('Avatar download failed');
  const avatar=await sharp(Buffer.from(await avatarResponse.arrayBuffer())).resize(512,512,{fit:'inside'}).png().toBuffer();
  const publicRepos=repos.filter(repo=>!repo.private);
  return validateProfile({username:user.login,avatar:'data:image/png;base64,'+avatar.toString('base64'),collectedAt:new Date().toISOString(),totalLines,publicRepos:publicRepos.length,stars:publicRepos.reduce((sum,repo)=>sum+repo.stargazers_count,0),commits});
}
