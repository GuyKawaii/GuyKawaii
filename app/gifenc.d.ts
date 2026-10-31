declare module 'gifenc' {
 export function quantize(data:Uint8Array, colors:number):number[][];
 export function applyPalette(data:Uint8Array,palette:number[][]):Uint8Array;
 export function GIFEncoder():{writeFrame(data:Uint8Array,width:number,height:number,options:{palette?:number[][];delay:number;repeat:number}):void;finish():void;bytes():Uint8Array};
 const api:{GIFEncoder:typeof GIFEncoder;quantize:typeof quantize;applyPalette:typeof applyPalette};
 export default api;
}
