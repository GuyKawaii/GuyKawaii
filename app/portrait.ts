
export {};
const canvas=document.querySelector<HTMLCanvasElement>('#portrait')!;
const ctx=canvas.getContext('2d',{willReadFrequently:true})!;
const columns=60,rows=40,pitchX=12,pitchY=18;
const ramp=' .,:;irsXA253hMHGS#9B&@';
let samples:Uint8ClampedArray|undefined;
let animation=0;
function hash(a:number,b:number,c:number){let n=(Math.imul(a+1,374761393)^Math.imul(b+1,668265263)^Math.imul(c+1,1274126177))>>>0;n=Math.imul(n^(n>>>13),1274126177)>>>0;return ((n^(n>>>16))>>>0)/4294967296;}
window.loadPortrait=async source=>{
 const image=new Image();image.src=source;await image.decode();
 const buffer=document.createElement('canvas');buffer.width=columns;buffer.height=rows;
 const sc=buffer.getContext('2d',{willReadFrequently:true})!;
 sc.fillStyle='#080d18';sc.fillRect(0,0,columns,rows);
 const side=Math.min(image.naturalWidth,image.naturalHeight);
 sc.drawImage(image,(image.naturalWidth-side)/2,(image.naturalHeight-side)/2,side,side,0,0,columns,rows);
 samples=sc.getImageData(0,0,columns,rows).data;
 window.drawPortrait(0);
};
window.drawPortrait=seconds=>{
 ctx.globalAlpha=1;ctx.shadowBlur=0;ctx.fillStyle='#080d18';ctx.fillRect(0,0,720,720);
 if(!samples)return;
 const frame=((Math.floor(seconds*4)%32)+32)%32;
 const noise=Number(document.querySelector<HTMLInputElement>('#noise')!.value)/100;
 const twinkle=Number(document.querySelector<HTMLInputElement>('#twinkle')!.value)/100;
 ctx.font='bold 17px monospace';ctx.textBaseline='middle';
 for(let row=0;row<rows;row++)for(let col=0;col<columns;col++){
  const offset=(row*columns+col)*4;
  const red=samples[offset],green=samples[offset+1],blue=samples[offset+2];
  const lum=(red*.2126+green*.7152+blue*.0722)/255;
  const grain=(hash(col,row,frame)-.5)*noise;
  const flash=hash(col+337,row+179,frame)<twinkle*.28;
  const density=Math.max(0,Math.min(1,Math.pow(lum,.85)+grain*.35));
  const glyph=ramp[Math.min(ramp.length-1,Math.floor(density*ramp.length))];
  if(glyph===' ')continue;
  const gain=1.10+grain;
  const ink=[red,green,blue].map(v=>Math.min(255,Math.round(v*gain+(flash?70:0))));
  ctx.fillStyle=`rgb(${ink.join(',')})`;
  // A faint colored halo sits behind the sharp glyph core; twinkles glow slightly more.
  ctx.shadowBlur=flash?4:2;ctx.shadowColor=`rgba(${ink.join(',')},0.4)`;
  ctx.fillText(glyph,col*pitchX+1,row*pitchY+pitchY/2);
 }
 ctx.shadowBlur=0;
};
document.querySelector<HTMLInputElement>('#image')!.addEventListener('change',async event=>{
 const file=(event.target as HTMLInputElement).files?.[0];if(!file)return;cancelAnimationFrame(animation);
 const url=URL.createObjectURL(file);try{await window.loadPortrait(url);}finally{URL.revokeObjectURL(url);}
 function tick(time:number){window.drawPortrait(time/1000);animation=requestAnimationFrame(tick);}animation=requestAnimationFrame(tick);
});
