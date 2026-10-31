import {readFile,writeFile,mkdir,rename} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
import {chromium} from 'playwright';
import sharp from 'sharp';
import {transform} from 'esbuild';
import {createRequire} from 'node:module';
const {GIFEncoder,quantize}=createRequire(import.meta.url)('gifenc') as typeof import('gifenc').default;
import type {Profile} from './model.js';
export async function render(profile:Profile,output:string,preview=false){
 const config=JSON.parse(await readFile('config.json','utf8'));
 const {code}=await transform(await readFile('app/browser.ts','utf8'),{loader:'ts',target:'es2022',format:'iife'});
 const browser=await chromium.launch();
 await mkdir(output,{recursive:true});
 try{
  const page=await browser.newPage({viewport:{width:1920,height:1200}});
  await page.goto(pathToFileURL(path.resolve('assets/ascii-portrait.html')).href);
  await page.addStyleTag({content:'main{display:none}body{display:block;margin:0}#card{width:1920px;height:1200px;max-width:none}'});
  const portraitCode=await transform(await readFile('app/portrait.ts','utf8'),{loader:'ts',target:'es2022',format:'iife'});
  await page.addScriptTag({content:portraitCode.code});
  await page.addScriptTag({content:code});
  await page.evaluate(async({profile,config,preview})=>window.prepareCard(profile,config,preview),{profile,config,preview});
  const rgba:Buffer[]=[];
  let first:Buffer|undefined;
  for(let i=0;i<32;i++){
   const encoded=await page.evaluate(time=>{window.drawCard(time);return document.querySelector<HTMLCanvasElement>('#card')!.toDataURL('image/png').split(',')[1];},i/4);
   const png=Buffer.from(encoded,'base64');if(i===0)first=png;
   rgba.push(await sharp(png).ensureAlpha().raw().toBuffer());
  }
  const samples=await Promise.all(rgba.map(data=>sharp(data,{raw:{width:1920,height:1200,channels:4}}).resize(480,300).raw().toBuffer()));
  const palette=quantize(Buffer.concat(samples),256),gif=GIFEncoder();
  // One persistent RGB565 mapping prevents static text colors changing as
  // animated portrait colors enter the encoder in a different order.
  const lookup=new Int16Array(65536).fill(-1);
  function indexed(data:Buffer){
   const result=new Uint8Array(data.length/4);
   for(let pixel=0;pixel<result.length;pixel++){
    const offset=pixel*4,key=((data[offset]>>3)<<11)|((data[offset+1]>>2)<<5)|(data[offset+2]>>3);
    if(lookup[key]<0){
     const r=((key>>11)&31)*255/31,g=((key>>5)&63)*255/63,b=(key&31)*255/31;
     let distance=Infinity,best=0;
     palette.forEach((color,index)=>{const score=(r-color[0])**2+(g-color[1])**2+(b-color[2])**2;if(score<distance){distance=score;best=index;}});
     lookup[key]=best;
    }
    result[pixel]=lookup[key];
   }
   return result;
  }
  rgba.forEach((data,i)=>gif.writeFrame(indexed(data),1920,1200,{...(i===0?{palette}:{}),delay:250,repeat:0}));gif.finish();
  // Complete both exports before replacing any previously generated images.
  await writeFile(path.join(output,'fetch.png.tmp'),first!);await writeFile(path.join(output,'fetch.gif.tmp'),gif.bytes());
  await rename(path.join(output,'fetch.png.tmp'),path.join(output,'fetch.png'));await rename(path.join(output,'fetch.gif.tmp'),path.join(output,'fetch.gif'));
 }finally{await browser.close();}
}
