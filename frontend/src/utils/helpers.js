export const num=v=>Number.isFinite(Number(v))?Number(v):0;
export function duration(v){const n=Math.max(0,Math.round(num(v)));if(n<60)return `${n} min`;const h=Math.floor(n/60),m=n%60;return m?`${h} hr ${m} min`:`${h} hr`;}
export function money(v){return `₹${Math.round(num(v)).toLocaleString('en-IN')}`;}
export function pct(v){return `${num(v).toFixed(1)}%`;}
export function downloadCSV(rows,filename='portmind-report.csv'){if(!rows?.length)return;const keys=[...new Set(rows.flatMap(r=>Object.keys(r)))];const esc=v=>`"${String(v??'').replaceAll('"','""')}"`;const csv=[keys.map(esc).join(','),...rows.map(r=>keys.map(k=>esc(r[k])).join(','))].join('\n');const blob=new Blob([csv],{type:'text/csv;charset=utf-8'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=filename;a.click();URL.revokeObjectURL(a.href);}
export function clone(v){return JSON.parse(JSON.stringify(v));}
