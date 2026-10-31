interface CardData {username:string;avatar:string;collectedAt:string;totalLines:number;publicRepos:number;stars:number;commits:number}
interface CardConfig {profile_info:[string,string][]}
declare global { interface Window {loadPortrait:(source:string)=>Promise<void>;drawPortrait:(time:number)=>void;drawCard:(time:number)=>void;prepareCard:(data:CardData,config:CardConfig,preview:boolean)=>Promise<void>} }
export {};
const cardCanvas=document.createElement('canvas');cardCanvas.width=1920;cardCanvas.height=1200;
cardCanvas.id='card';document.body.append(cardCanvas);
const cardContext=cardCanvas.getContext('2d')!;
let cardData:CardData,cardConfig:CardConfig,isPreview=false;
const cardFont=(size:number)=>`${size}px Consolas, 'DejaVu Sans Mono', monospace`;
function cardText(text:string,x:number,y:number,size:number,color:string,maxWidth?:number){
 cardContext.font=cardFont(size);cardContext.fillStyle=color;
 if(maxWidth)while(cardContext.measureText(text).width>maxWidth&&size>14){size--;cardContext.font=cardFont(size);}
 cardContext.fillText(text,x,y);
}
window.prepareCard=async(data,config,preview)=>{cardData=data;cardConfig=config;isPreview=preview;await window.loadPortrait(data.avatar);window.drawCard(0);};
window.drawCard=time=>{
 const c=cardContext, cyan='#43eddf',pink='#f16ab7',white='#e1edf4',muted='#8da5b7';
 window.drawPortrait(time);c.fillStyle='#050910';c.fillRect(0,0,1920,1200);
 c.beginPath();[[30,62],[62,30],[1858,30],[1890,62],[1890,1138],[1858,1170],[62,1170],[30,1138]].forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.closePath();c.fillStyle='#080d18';c.fill();c.strokeStyle='#25354b';c.lineWidth=2;c.stroke();
 const line=(points:number[][],color:string,width=2)=>{c.beginPath();points.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.strokeStyle=color;c.lineWidth=width;c.stroke();};
 line([[30,156],[30,62],[62,30],[208,30]],cyan,4);line([[1712,1170],[1858,1170],[1890,1138],[1890,1044]],pink,4);
 cardText(`[ ${cardData.username.toUpperCase()} / PROFILE ]`,90,84,24,cyan);
 cardText(isPreview?'NEOFETCH / PREVIEW':'NEOFETCH / GITHUB',1455,84,23,muted);
 c.drawImage(document.querySelector<HTMLCanvasElement>('#portrait')!,88,224);
 line([[850,205],[850,1030]],'#233449');
 cardText(cardData.username,910,208,46,white);c.font=cardFont(46);const userWidth=c.measureText(cardData.username).width;
 cardText('@github',910+userWidth,208,46,pink);cardText('------------------------------',910,275,28,'#345268');
 const info=cardConfig.profile_info??[];
 const rows=[...info,['',''],['Repositories LOC',cardData.totalLines.toLocaleString('en-US')],['Public repos',cardData.publicRepos.toLocaleString('en-US')],['Stars',cardData.stars.toLocaleString('en-US')],['Commits',cardData.commits.toLocaleString('en-US')]];
 rows.forEach(([label,value],i)=>{const y=352+i*Math.min(55,570/Math.max(1,rows.length-1));cardText(label,910,y,27,i<=info.length?cyan:pink);cardText(value,1225,y,28,white,600);});
 ['#26364b','#2c81af',cyan,'#71b6e9','#b9aaa0','#704a29',pink,white].forEach((color,i)=>{c.fillStyle=color;c.fillRect(910+i*48,963,40,31);});
 cardText(`${cardData.username.toLowerCase()}@dev:~$`,90,1000,29,cyan);
 if(Math.floor(time*4)%16<8){c.fillStyle=cyan;c.fillRect(366,1009,14,28);}
 line([[90,1080],[1830,1080]],'#233449');
 cardText(isPreview?'LOCAL DESIGN PREVIEW':'AGGREGATE STATS / UPDATED DAILY',90,1107,22,muted);
 cardText(isPreview?'Proposed info / illustrative counts':'LOC INCLUDES PUBLIC + PRIVATE REPOS',1140,1107,22,muted);
};
