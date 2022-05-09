(() => {
    if (location.protocol !== 'https:' && location.hostname !== 'localhost') return;
    const js = document.createElement('script')
    js.type = 'module'
    js.src = 'wake-up.es.js'
    document.body.appendChild(js)
})();