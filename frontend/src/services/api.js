const API=(import.meta.env.VITE_API_URL||'http://127.0.0.1:8000').replace(/\/$/,'');
async function request(path,options={}){let response;try{response=await fetch(`${API}${path}`,{headers:{'Content-Type':'application/json',...(options.headers||{})},...options});}catch(e){throw new Error(`Cannot reach PortMind backend at ${API}. Start FastAPI first.`)}if(!response.ok){let msg=await response.text();try{const j=JSON.parse(msg);msg=j.detail||msg}catch{}throw new Error(msg||`Request failed (${response.status})`)}return response.json();}
export const simulate=payload=>request('/api/simulate',{method:'POST',body:JSON.stringify(payload)});
export const monteCarlo=payload=>request('/api/monte-carlo',{method:'POST',body:JSON.stringify(payload)});
export const askAI=(message,simulation)=>request('/api/ai',{method:'POST',body:JSON.stringify({message,simulation})});
export const health=()=>request('/api/health');
export const reset=()=>request('/api/reset',{method:'POST'});
export const presets=()=>request('/api/presets');
