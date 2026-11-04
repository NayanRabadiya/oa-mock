// mimics the page's JS worker (async-aware version)
const fs=require('fs');
module.exports = async function(src, inp){
  let out="", err="";
  const show=x=>typeof x==="string"?x:(x&&typeof x==="object"?JSON.stringify(x):String(x));
  const fmt=a=>a.map(show).join(" ");
  const con={log:(...a)=>{out+=fmt(a)+"\n"},info:(...a)=>{out+=fmt(a)+"\n"},error:(...a)=>{err+=fmt(a)+"\n"},warn:()=>{}};
  const EXIT={exit:true};
  const proc={stdin:{on(){return this},resume(){},setEncoding(){}},stdout:{write(s){out+=String(s);return true}},env:{},argv:[],exit(){throw EXIT}};
  const req=n=>{if(n==="fs")return{readFileSync:()=>inp};throw new Error("Module '"+n+"' is not available here")};
  try { const r=new Function("require","process","console",src)(req,proc,con); if(r&&typeof r.then==="function") await r; }
  catch(x){ if(x!==EXIT) err+=String(x&&x.stack?String(x.stack).split("\n").slice(0,3).join("\n"):x); }
  return {out,err};
};
