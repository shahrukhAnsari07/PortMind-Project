export const VESSEL_NAMES=['Ocean Star','Blue Horizon','Pacific Dawn','Evergreen','Maersk Nova','Atlas Express','Eastern Pearl','Blue Meridian','Indian Voyager','Sea Falcon','Aurora Line','Pacific Trader'];
export const WEATHER=['Normal','Heavy Rain','Storm','Low Visibility'];
export const DEFAULT_RESOURCES={vessels:4,berths:2,cranes:'',trucks:12,yards:4};
const arrivals=[0,35,70,100,140,185,225,270,315,355,400,445];
const services=[150,120,110,90,130,105,95,80,115,100,125,100];
const containers=[300,240,220,180,260,210,190,160,230,200,250,190];
const priorities=[2,1,2,1,2,3,2,1,2,3,2,1];
export function makeVessel(i,name=VESSEL_NAMES[i]||`Vessel ${i+1}`){return {id:`v-${i+1}-${name.toLowerCase().replace(/[^a-z0-9]+/g,'-')}`,name,arrival_time:arrivals[i]??i*35,service_time:services[i]??110,containers:containers[i]??200,priority:priorities[i]??2};}
export function defaultVessels(count=4){return Array.from({length:count},(_,i)=>makeVessel(i));}
export const DEFAULT_SCENARIO={delayedVessel:'',delayMinutes:0,failedCrane:'',closedBerth:'',weather:'Normal',truckShortage:0,blockedYard:'',yardReduction:0,scenarioName:'normal'};
export const PRESETS={
 normal:{label:'Normal operations',icon:'🟢',...DEFAULT_SCENARIO,scenarioName:'normal'},
 delay:{label:'+45 min vessel delay',icon:'🚢',...DEFAULT_SCENARIO,scenarioName:'vessel_delay',delayedVessel:'Ocean Star',delayMinutes:45},
 crane:{label:'Crane failure',icon:'🏗️',...DEFAULT_SCENARIO,scenarioName:'crane_failure',failedCrane:'2'},
 rain:{label:'Heavy rain',icon:'🌧️',...DEFAULT_SCENARIO,scenarioName:'heavy_rain',weather:'Heavy Rain'},
 trucks:{label:'Truck shortage',icon:'🚚',...DEFAULT_SCENARIO,scenarioName:'truck_shortage',truckShortage:5},
 yard:{label:'Yard congestion',icon:'📦',...DEFAULT_SCENARIO,scenarioName:'yard_congestion',blockedYard:'2',yardReduction:25},
 major:{label:'Major disruption',icon:'🚨',...DEFAULT_SCENARIO,scenarioName:'major_disruption',weather:'Storm',delayedVessel:'Pacific Dawn',delayMinutes:50,failedCrane:'2',truckShortage:4,blockedYard:'2',yardReduction:25}
};
