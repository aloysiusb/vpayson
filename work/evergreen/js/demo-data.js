/* ─────────────────────────────────────────────────────────────────────────
   demo-data.js — makes dispatch.html run on a portfolio site.

   dispatch.html is the office board from a live route-hauling application. It
   normally talks to a Node server: four REST endpoints and a WebSocket
   carrying every event as it happens. None of that exists here.

   Rather than fork the page into a mock, this file swaps out the only two
   things it uses to reach the outside world, the same way the app's own
   sim.js does for a test drive:

       window.fetch      → answers the four endpoints from fixtures below
       window.WebSocket  → a fake socket that plays a scripted morning

   Every line of rendering, feed-merging, progress and styling logic in
   dispatch.html is the real code, untouched. That is the point: a mock would
   drift away from the thing it is meant to show. Load this BEFORE any other
   script on the page.

   EVERY CUSTOMER, ADDRESS, NOTE AND DRIVER HERE IS INVENTED. The streets do
   not exist in the towns named. There is no real route data on this page and
   no server behind it, so there is nothing to redact and nothing to leak.
   ───────────────────────────────────────────────────────────────────────── */

(function () {
  'use strict';

  /* ── Invented customers ───────────────────────────────────────────────
     The five on the walkthrough page appear here too, so the two demos
     describe the same fictional morning rather than contradicting each
     other. */
  const STOPS = {
    'Weds DV Res': [
      { sectionLabel: 'Carbondale — east' },
      { accountName: 'R. Halloway',        address: '412 Fireweed Ave',   city: 'Carbondale', notes: '', directions: 'Bin behind the blue gate' },
      { accountName: 'Kestrel Bakery',     address: '88 Cottonwood St',   city: 'Carbondale', notes: 'Extra bin Weds', noteUrgency: 'info' },
      { accountName: 'M. Truesdale',       address: '7 Larkspur Ct',      city: 'Carbondale', notes: '' },
      { sectionLabel: 'Carbondale — west' },
      { accountName: 'Elk Meadow HOA',     address: '35 Wapiti Trail',    city: 'Carbondale', notes: '', directions: 'Gate code on file' },
      { accountName: 'Dry Creek Ranch',    address: 'Dry Creek Bend',     city: 'Carbondale', notes: 'Watch the cattle guard' },
      { accountName: 'P. Ostrowski',       address: '19 Tin Cup Row',     city: 'Carbondale', notes: '' },
    ],
    'Tues DV': [
      { sectionLabel: 'Silt' },
      { accountName: 'Riverbend House',    address: '1190 County Rd 118', city: 'Silt',       notes: 'Dog — call on arrival', noteUrgency: 'urgent' },
      { accountName: 'J. Amery',           address: '64 Aspenwood Ln',    city: 'Silt',       notes: '' },
      { sectionLabel: 'New Castle' },
      { accountName: 'Coalcreek Cafe',     address: '2 Ember St',         city: 'New Castle', notes: 'Two bins on Tues' },
      { accountName: 'H. Vandermeer',      address: '881 Quarry Bend',    city: 'New Castle', notes: '' },
    ],
    'Weds Commercial': [
      { accountName: 'Valley Grange Co-op', address: '7 Foundry Pl',      city: 'Glenwood',   notes: 'On hold until Oct', noteUrgency: 'hold' },
      { accountName: 'Redstone Provisions', address: '14 Kiln Row',       city: 'Glenwood',   notes: '' },
      { accountName: 'The Hoptree Taproom', address: '331 Millrace Way',  city: 'Glenwood',   notes: 'Use the alley door' },
      { accountName: 'Fireweed Flowers',    address: '9 Foundry Pl',      city: 'Glenwood',   notes: '' },
    ],
    'Thurs UV': [
      { accountName: 'Marmot Lodge',       address: '500 Sundial Rd',     city: 'Basalt',     notes: '' },
      { accountName: 'S. Achterberg',      address: '77 Willowbend',      city: 'Basalt',     notes: 'New customer — first pickup' },
      { accountName: 'Blue Columbine Inn', address: '12 Ptarmigan Ct',    city: 'El Jebel',   notes: '' },
    ],
    'TUES 4WD ACTION': [
      { accountName: 'Highwater Cabins',   address: '4 Switchback Spur',  city: 'Marble',     notes: 'Chains Nov–Apr', noteUrgency: 'info' },
      { accountName: 'T. Brandhagen',      address: '2100 Gravel Fork Rd', city: 'Marble',    notes: '' },
    ],
    'Thursday COM/EAGLE': [
      { accountName: 'Gypsum Feed & Seed', address: '40 Chaff Ave',       city: 'Gypsum',     notes: '' },
      { accountName: 'Eagle River Bakery', address: '6 Millstone Ct',     city: 'Eagle',      notes: '' },
    ],
    'Friday': [
      { accountName: 'Sopris Sundries',    address: '88 Tinder St',       city: 'Carbondale', notes: '' },
      { accountName: 'K. Lindqvist',       address: '23 Harebell Ln',     city: 'Carbondale', notes: '' },
    ],
    'Monday': [
      { accountName: 'Thistledown Farm',   address: '3 Furrow Rd',        city: 'Silt',       notes: '' },
      { accountName: 'R. Mbeki',           address: '150 Chokecherry Dr', city: 'Rifle',      notes: '' },
    ],
    'Max Routes': [
      { accountName: 'Overflow — Carbondale', address: 'Various',         city: 'Carbondale', notes: 'Catch-up stops' },
    ],
  };

  // Which stops start the morning already done, so progress bars are not all zero.
  const PREDONE = { 'Weds DV Res': 3, 'Tues DV': 2, 'Weds Commercial': 1, 'Thurs UV': 1 };

  /* Build the shape /api/routes/:tab returns: a flat list of rows, section
     headers included, exactly as the server's column whitelist emits it. */
  const routeItems = {};
  Object.keys(STOPS).forEach(tab => {
    let row = 3;
    let doneLeft = PREDONE[tab] || 0;
    routeItems[tab] = STOPS[tab].map(s => {
      row += 1;
      if (s.sectionLabel) {
        return { rowNumber: row, isSectionHeader: true, sectionLabel: s.sectionLabel,
                 done: false, address: '', notes: '', directions: '', accountName: '', city: '' };
      }
      const done = doneLeft > 0;
      if (done) doneLeft -= 1;
      return {
        rowNumber: row,
        done,
        address: s.address,
        notes: s.notes || '',
        directions: s.directions || '',
        accountName: s.accountName,
        city: s.city,
        isSectionHeader: false,
        sectionLabel: '',
        rowColor: '',
        noteUrgency: s.noteUrgency || '',
      };
    });
  });

  function firstUndone(tab) {
    return (routeItems[tab] || []).find(i => !i.isSectionHeader && !i.done);
  }

  /* ── Fake network ─────────────────────────────────────────────────────
     Only the endpoints dispatch.html actually calls. Anything else falls
     through to a 404 rather than silently reaching the real internet. */
  const routeRe = /\/api\/routes\/([^/?]+)/;

  function json(body) {
    return Promise.resolve(new Response(JSON.stringify(body), {
      status: 200, headers: { 'Content-Type': 'application/json' },
    }));
  }

  window.fetch = function (input, opts) {
    const url = String(input && input.url ? input.url : input);
    const method = ((opts && opts.method) || 'GET').toUpperCase();

    // Nothing on a demo page may write anywhere.
    if (method !== 'GET') {
      return json({ ok: true, demo: true });
    }

    const m = url.match(routeRe);
    if (m) {
      const tab = decodeURIComponent(m[1]);
      return json({ items: routeItems[tab] || [] });
    }
    if (url.indexOf('/api/activity') === 0 || url.indexOf('/api/activity') > -1) {
      return json({ events: replay() });
    }
    if (url.indexOf('/api/requests') > -1) {
      return json({ counts: { pending: pendingRequests } });
    }
    if (url.indexOf('/health') > -1) {
      // No broken tabs: the "cannot be saved to" banner stays hidden.
      return json({ ok: true, sheet: { problems: {} } });
    }
    if (url.indexOf('/api/styles') > -1) {
      return json({});                       // page keeps its shipped styling
    }
    if (url.indexOf('/api/maps-key') > -1) {
      return json({ key: '' });              // drawn map, no Google call
    }
    return Promise.resolve(new Response('demo: not found', { status: 404 }));
  };

  let pendingRequests = 2;

  /* ── This morning, already recorded ───────────────────────────────────
     What /api/activity replays when the board opens, so it does not start
     empty. Times are relative to page load, so it always reads as today. */
  function ago(min) { return new Date(Date.now() - min * 60000).toISOString(); }

  function replay() {
    return [
      { type: 'stop-updated', tabName: 'Weds DV Res', rowNumber: 5,  done: true,  at: ago(96) },
      { type: 'stop-updated', tabName: 'Weds DV Res', rowNumber: 6,  done: true,  at: ago(88) },
      { type: 'notes-log-entry', driverName: 'Driver 2', text: 'Cottonwood St plowed, fine to run', at: ago(74) },
      { type: 'stop-updated', tabName: 'Tues DV', rowNumber: 5,  done: true, at: ago(61) },
      { type: 'photo-added', tabName: 'Weds DV Res', rowNumber: 7, link: '#', at: ago(52) },
      { type: 'note-updated', tabName: 'Weds DV Res', rowNumber: 9,
        notes: 'Gate code changed — see office', at: ago(41) },
      { type: 'request-created', id: 'req-1041', kind: 'hold',
        name: 'A. Ferreira', account: '19 Tin Cup Row, Carbondale', at: ago(33) },
      { type: 'stop-updated', tabName: 'Weds Commercial', rowNumber: 4, done: true, at: ago(21) },
      { type: 'request-created', id: 'req-1042', kind: 'new_customer',
        name: 'Larkspur Bakehouse', account: '5 Harebell Ln, Carbondale', at: ago(12) },
    ];
  }

  /* ── Fake WebSocket ───────────────────────────────────────────────────
     Reports itself open, then plays a scripted rest-of-the-morning so the
     board is visibly live rather than a screenshot. dispatch.html cannot
     tell the difference: it only uses onopen, onmessage and onclose. */
  const SCRIPT = [
    { after: 4000,  ev: () => loc('Weds DV Res', 39.4021, -107.2114) },
    { after: 3500,  ev: () => markNext('Weds DV Res') },
    { after: 5000,  ev: () => ({ type: 'notes-log-entry', driverName: 'Driver 1',
        text: 'Foundry Pl bin blocked by a delivery van — will retry after lunch' }) },
    { after: 4500,  ev: () => loc('Weds DV Res', 39.3996, -107.2149) },
    { after: 4000,  ev: () => markNext('Thurs UV') },
    { after: 5500,  ev: () => ({ type: 'request-decided', id: 'req-1041', status: 'approved' }) },
    { after: 4000,  ev: () => ({ type: 'hazard-added', tabName: 'Tues DV',
        hazard: { label: 'Ice on County Rd 118 switchback' } }) },
    { after: 4500,  ev: () => markNext('Weds Commercial') },
    { after: 5000,  ev: () => ({ type: 'photo-added', tabName: 'Thurs UV',
        rowNumber: 5, link: '#' }) },
    { after: 4000,  ev: () => markNext('Weds DV Res') },
    { after: 6000,  ev: () => ({ type: 'request-created', id: 'req-1043', kind: 'missed',
        name: 'H. Vandermeer', account: '881 Quarry Bend, New Castle' }) },
    { after: 4500,  ev: () => markNext('Tues DV') },
  ];

  function loc(tabName, lat, lng) {
    return { type: 'driver-location', tabName, lat, lng, accuracy: 12, driverName: 'Driver 1' };
  }

  function markNext(tabName) {
    const stop = firstUndone(tabName);
    if (!stop) return null;
    stop.done = true;
    return { type: 'stop-updated', tabName, rowNumber: stop.rowNumber, done: true };
  }

  function FakeSocket() {
    this.readyState = 0;
    const self = this;
    setTimeout(function () {
      self.readyState = 1;
      if (typeof self.onopen === 'function') self.onopen({});
      run(0);
    }, 300);

    function run(i) {
      if (i >= SCRIPT.length) return;          // morning over; socket stays open
      setTimeout(function () {
        const msg = SCRIPT[i].ev();
        if (msg) {
          if (msg.type === 'request-created') pendingRequests += 1;
          if (msg.type === 'request-decided') pendingRequests = Math.max(0, pendingRequests - 1);
          if (typeof self.onmessage === 'function') {
            self.onmessage({ data: JSON.stringify(msg) });
          }
        }
        run(i + 1);
      }, SCRIPT[i].after);
    }
  }
  FakeSocket.prototype.send = function () {};    // the board never sends
  FakeSocket.prototype.close = function () { this.readyState = 3; };
  window.WebSocket = FakeSocket;

  /* A quiet marker, so it is obvious in the console that this is the demo
     harness and not a misconfigured build pointing at nothing. */
  console.log('[demo] dispatch running on invented fixtures — no network, no real routes');
})();
