'use strict';

(function(){
  const API_URL = '/api/centres';
  const LIST_EL_ID = 'centres-list';
  const STATUS_EL_ID = 'centres-status';
  const SCROLL_CONTAINER_ID = 'centres-scroll-container';

  const CACHE_KEY = 'nabh_geocode_cache_v1';
  const GEO_CACHE_TTL_DAYS = 30;

  const cache = loadCache();

  function loadCache(){
    try{
      const raw = localStorage.getItem(CACHE_KEY);
      if(!raw) return { createdAt: Date.now(), data: {} };
      const parsed = JSON.parse(raw);
      // reset if too old
      const ageDays = (Date.now() - (parsed.createdAt||0)) / (1000*60*60*24);
      if(ageDays > GEO_CACHE_TTL_DAYS){
        return { createdAt: Date.now(), data: {} };
      }
      return parsed;
    }catch(e){
      return { createdAt: Date.now(), data: {} };
    }
  }
  function saveCache(){
    try{
      localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
    }catch(e){/* ignore */}
  }

  function haversineDistance(lat1, lon1, lat2, lon2){
    function toRad(v){ return v * Math.PI/180; }
    const R = 6371; // km
    const dLat = toRad(lat2-lat1);
    const dLon = toRad(lon2-lon1);
    const a = Math.sin(dLat/2)**2 + Math.cos(toRad(lat1))*Math.cos(toRad(lat2))*Math.sin(dLon/2)**2;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  }

  function $(id){ return document.getElementById(id); }

  function cityGuessFromName(name){
    // Take the last two comma-separated tokens before 'India'
    const parts = name.split(',').map(s=>s.trim());
    const indiaIdx = parts.findIndex(p => /india$/i.test(p));
    let guess = name;
    if(indiaIdx > 0){
      const slice = parts.slice(Math.max(0, indiaIdx-2), indiaIdx);
      guess = slice.join(', ');
    } else {
      // fallback: last two tokens
      guess = parts.slice(-2).join(', ');
    }
    return guess;
  }

  async function geocodeAddress(q){
    const key = q.toLowerCase();
    if(cache.data[key]) return cache.data[key];
    try{
      // Respect Nominatim usage policy: include format and limit, avoid rapid calls
      const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}&limit=1&addressdetails=0`;
      const res = await fetch(url, { headers: { 'Accept-Language': 'en' } });
      if(!res.ok) throw new Error('geocode failed');
      const data = await res.json();
      if(Array.isArray(data) && data.length){
        const { lat, lon } = data[0];
        cache.data[key] = { lat: parseFloat(lat), lon: parseFloat(lon) };
        saveCache();
        return cache.data[key];
      }
    }catch(e){
      // ignore; leave undefined
    }
    cache.data[key] = null;
    saveCache();
    return null;
  }

  function renderList(items){
    const list = $(LIST_EL_ID);
    if(!list) return;
    list.innerHTML = '';
    for(const item of items){
      const li = document.createElement('li');
      li.className = 'list-group-item';
      const badge = item.distance_km != null ? `<span class="badge bg-primary rounded-pill">${item.distance_km.toFixed(1)} km</span>` : '';
      const remarks = item.remarks ? `<div class="small text-muted">${item.remarks}</div>` : '';
      li.innerHTML = `
        <div class="d-flex w-100 justify-content-between align-items-start">
          <div>
            <div class="fw-semibold">${item.name}</div>
            <div class="small text-muted">Ref: ${item.reference_no} • Acc: ${item.acc_no}</div>
            <div class="small">Valid: ${item.valid_from || '-'} → ${item.valid_upto || '-'}</div>
            ${remarks}
          </div>
          ${badge}
        </div>`;
      list.appendChild(li);
    }
  }

  function status(text, type){
    const el = $(STATUS_EL_ID);
    if(!el) return;
    el.className = `alert alert-${type||'info'} mb-3`;
    el.textContent = text;
  }

  async function getUserLocation(){
    return new Promise((resolve)=>{
      if(!navigator.geolocation){
        resolve(null);
        return;
      }
      navigator.geolocation.getCurrentPosition(
        pos => resolve({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
        _err => resolve(null),
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 600000 }
      );
    });
  }

  async function init(){
    const list = $(LIST_EL_ID);
    if(!list) return; // section not on this page

    status('Loading centres…', 'info');

    const res = await fetch(API_URL);
    const payload = await res.json();
    if(!payload.success){
      status('Failed to load centres.', 'danger');
      return;
    }
    let centres = payload.data || [];

    // Initial render (unsorted)
    renderList(centres);
    status('Requesting your location to sort centres by proximity…', 'secondary');

    const user = await getUserLocation();
    if(!user){
      status('Location access denied or unavailable. Showing centres in listed order.', 'warning');
      return;
    }
    status('Calculating distances…', 'info');

    // Compute distances progressively
    const BATCH = 5; // geocode concurrency
    let idx = 0;
    async function processBatch(){
      const slice = centres.slice(idx, idx+BATCH);
      await Promise.all(slice.map(async (c) => {
        // Already have coordinates? (from server in future)
        if(c.lat && c.lon){
          c.distance_km = haversineDistance(user.lat, user.lon, c.lat, c.lon);
          return;
        }
        const q = cityGuessFromName(c.name);
        const pt = await geocodeAddress(q);
        if(pt){
          c.lat = pt.lat; c.lon = pt.lon;
          c.distance_km = haversineDistance(user.lat, user.lon, c.lat, c.lon);
        }
      }));
      idx += BATCH;
      // Sort with available distances first
      centres.sort((a,b)=>{
        const da = a.distance_km, db = b.distance_km;
        if(da==null && db==null) return 0;
        if(da==null) return 1;
        if(db==null) return -1;
        return da - db;
      });
      renderList(centres);
      if(idx < centres.length){
        // small delay to be gentle to Nominatim
        setTimeout(processBatch, 1200);
      } else {
        status('Centres sorted by distance.', 'success');
      }
    }

    processBatch();
  }

  document.addEventListener('DOMContentLoaded', init);
})();
