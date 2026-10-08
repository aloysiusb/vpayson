#!/usr/bin/env python3
"""Build a public, self-contained demo of the wall from the private case build.

Replaces every piece of real case content with a public-domain subject (the
1872 Mary Celeste), repoints the storage keys, disables the two feed-driven
sections that need a server, and shims the one remaining server endpoint
(/api/geocode) with baked coordinates so the whole thing runs as a static file.
"""
import re
import sys
import pathlib

SRC = pathlib.Path(sys.argv[1])
DST = pathlib.Path(sys.argv[2])
s = SRC.read_text(encoding="utf-8")
orig_len = len(s)
checks = []


def must(label, cond):
    checks.append((label, bool(cond)))
    if not cond:
        print(f"FAIL: {label}")


def replace_span(text, start_pat, last_decl_pat, new, label, term="\n];\n"):
    """Replace from start_pat through the array terminator that closes last_decl_pat.

    The naive "first ]; after the start" is wrong when the span covers several
    consecutive array declarations — it stops at the first one's terminator. So
    locate the final declaration in the span first, then close from there.
    """
    m = re.search(start_pat, text, re.M)
    must(f"found start of {label}", m)
    if not m:
        return text
    last = re.search(last_decl_pat, text[m.start():], re.M)
    must(f"found last decl of {label}", last)
    if not last:
        return text
    end = text.index(term, m.start() + last.start()) + len(term)
    return text[: m.start()] + new + text[end:]


# ─────────────────────────────── the demo board ───────────────────────────────
ZONES = """const ZONES = [
  { id:'voyage', label:'The Voyage — New York to Genoa', sublabel:'Cleared Staten Island 7 Nov 1872 · 1,701 barrels of denatured alcohol · ten aboard',
    x:77, y:77, w:2000, h:1900, cls:'corporate' },
  { id:'discovery', label:'The Discovery — 4 December 1872', sublabel:'Dei Gratia sights her under sail and unmanned · Gibraltar salvage hearing',
    x:2650, y:77, w:2000, h:1900, cls:'legallymine' },
];

const CLUSTERS = [
  { id:'c-aboard',   zone:'voyage',    label:'Aboard at departure — ten souls', x:160, y:180, w:1830, h:470, cls:'cl-officers' },
  { id:'c-cargo',    zone:'voyage',    label:'The cargo and the ship', x:160, y:790, w:1180, h:900, cls:'cl-fdd' },
  { id:'c-found',    zone:'discovery', label:'What was found aboard', x:2730, y:180, w:1840, h:470, cls:'cl-delaware' },
  { id:'c-theories', zone:'discovery', label:'Theories, then and since', x:2730, y:1070, w:1840, h:570, cls:'cl-storeweb' },
];

const NODES = [

{
  id:'celeste', x:2360, y:850, type:'center', tier:1, label:'Mary\\nCeleste', avatar:'\\u2693',
  detail:{ title:'Mary Celeste', subtitle:'Brigantine, 282 tons · found abandoned 4 December 1872', tag:'entity',
    sections:[
      { h:'The short version', items:[
        'Left New York for Genoa on 7 November 1872 with ten people aboard: Captain Benjamin Briggs, his wife Sarah, their two-year-old daughter Sophia, and a crew of seven.',
        'Sighted on 4 December 1872 about 400 miles east of the Azores, under partial sail, on a starboard tack, with nobody aboard.',
        'She was seaworthy. The cargo was largely intact. There was food and water. The single lifeboat was gone.',
        'Not one of the ten was ever seen again, and no explanation has ever been established.',
      ]},
      { h:'Why she is the standing example', items:[
        'The Gibraltar salvage hearing produced a large documentary record and no finding of cause, which is why the case is still argued from primary sources rather than settled.',
        'Almost every popular detail — a hot meal on the table, a still-warm stove, a cat asleep on a locker — comes from a short story Arthur Conan Doyle published in 1884, not from the record.',
      ]},
    ], docs:[] },
},

{
  id:'briggs', x:600, y:390, type:'person', tier:2, label:'Capt. Benjamin\\nBriggs',
  detail:{ title:'Captain Benjamin Spooner Briggs', subtitle:'Master · part-owner · 37 years old', tag:'person',
    sections:[
      { h:'Role', items:[
        'An experienced and, by every account gathered at the hearing, notably careful master — a temperance man who held a share in the vessel himself.',
        'His personal stake is the standard argument against the mutiny and barratry theories: he had money and family aboard and nothing to gain.',
        'Brought his wife and younger child on the voyage; their elder son Arthur was left at school in Massachusetts and so survived.',
      ]},
    ], docs:[] },
},

{
  id:'sarah', x:1180, y:390, type:'person', tier:2, label:'Sarah Briggs\\n& Sophia, 2',
  detail:{ title:'Sarah Elizabeth Briggs and Sophia Matilda', subtitle:'The captain\\u2019s wife and their younger child', tag:'person',
    sections:[
      { h:'Role', items:[
        'Sarah\\u2019s letters home from New York, written days before sailing, are among the last direct accounts of the ship and her company.',
        'A melodeon was aboard for her. It was still aboard when the ship was found.',
        'The presence of a toddler is the usual objection to any theory requiring a calm, orderly, voluntary departure in a small boat.',
      ]},
    ], docs:[] },
},

{
  id:'crew', x:1760, y:390, type:'entity', tier:2, label:'Crew of seven',
  detail:{ title:'The crew', subtitle:'Two mates, a cook, four seamen', tag:'entity',
    sections:[
      { h:'Role', items:[
        'Albert Richardson (first mate), Andrew Gilling (second mate), Edward Head (steward and cook), and four German seamen — the brothers Volkert and Boz Lorenzen, Arian Martens and Gottlieb Goodschaad.',
        'Briggs had written that he considered them a capable company. No disciplinary record or grievance was produced at the hearing.',
        'The four German seamen\\u2019s nationality was leaned on heavily by the prosecuting advocate at Gibraltar, on no evidence, and is a fair illustration of how the hearing ran.',
      ]},
    ], docs:[] },
},

{
  id:'cargo', x:420, y:980, type:'confirmed', tier:2, label:'1,701 barrels\\nof alcohol',
  detail:{ title:'The cargo', subtitle:'Denatured industrial alcohol, consigned to Genoa', tag:'confirmed',
    sections:[
      { h:'What it was', items:[
        'Crude industrial alcohol in red oak barrels, shipped for a Genoese firm and insured at roughly $36,000 — far more than the vessel.',
        'The cargo was found essentially undisturbed, which is the central fact against piracy: a pirate who boards and takes nothing is not a pirate.',
      ]},
    ], docs:[] },
},

{
  id:'barrels', x:1000, y:980, type:'keyfind', tier:2, label:'Nine barrels\\nfound empty',
  detail:{ title:'Nine empty barrels', subtitle:'Discovered on unloading at Genoa', tag:'keyfind',
    sections:[
      { h:'Why it matters', items:[
        'When the cargo was finally discharged at Genoa, nine of the 1,701 barrels were empty.',
        'Red oak is more porous than white oak, so leakage is unremarkable in itself — but leaking alcohol in a closed hold produces vapour.',
        'This is the evidential root of the strongest surviving theory: a vapour build-up, a frightening noise or a visible flash, and a precautionary evacuation that went wrong.',
      ]},
    ], docs:[] },
},

{
  id:'amazon', x:420, y:1420, type:'dissolved', tier:3, label:'Was the\\nAmazon',
  detail:{ title:'Amazon', subtitle:'Her first name and first decade', tag:'dissolved',
    sections:[
      { h:'Before', items:[
        'Launched at Spencer\\u2019s Island, Nova Scotia in 1861 as Amazon. Her first master died days into her first voyage.',
        'Driven ashore in a storm in 1867, sold as a wreck, rebuilt, re-registered under American ownership and renamed Mary Celeste.',
        'The run of misfortune before 1872 is why she was later written about as a cursed ship — a reading that postdates the events and explains nothing.',
      ]},
    ], docs:[] },
},

{
  id:'deigratia', x:3000, y:390, type:'entity', tier:2, label:'Dei Gratia',
  detail:{ title:'Dei Gratia', subtitle:'The brigantine that found her', tag:'entity', mapEmbed:'Gibraltar',
    sections:[
      { h:'Role', items:[
        'Sighted the Mary Celeste yawing oddly under partial sail and closed with her after signalling and getting no answer.',
        'Her master, David Morehouse, had dined with Briggs in New York shortly before both ships sailed — a coincidence the Gibraltar court treated with open suspicion.',
        'Put three men aboard, who found her abandoned, and brought her into Gibraltar to claim salvage.',
      ]},
    ], docs:[] },
},

{
  id:'morehouse', x:3580, y:390, type:'person', tier:2, label:'Capt. David\\nMorehouse',
  detail:{ title:'Captain David Reed Morehouse', subtitle:'Master of the Dei Gratia · salvage claimant', tag:'person',
    sections:[
      { h:'Role', items:[
        'Brought the derelict in and claimed salvage, which put him immediately under suspicion of collusion with Briggs.',
        'The court found nothing, but awarded only about a fifth of the insured value — unusually low, and generally read as a signal of lingering doubt rather than a finding of fact.',
      ]},
    ], docs:[] },
},

{
  id:'logslate', x:4160, y:390, type:'branch', tier:2, label:'The log slate\\n— 25 Nov',
  detail:{ title:'The log slate', subtitle:'Last entry 8 a.m., 25 November 1872', tag:'branch',
    sections:[
      { h:'What it recorded', items:[
        'The final entry put the ship just off Santa Maria Island in the Azores — around six miles from land and nine days before she was found.',
        'In those nine days she sailed on, unmanned, roughly 400 miles further east.',
        'The entry is entirely routine. Nothing in it anticipates anything.',
      ]},
    ], docs:[] },
},

{
  id:'yawl', x:3000, y:1270, type:'keyfind', tier:2, label:'The yawl\\nis missing',
  detail:{ title:'The missing yawl', subtitle:'The single lifeboat, launched — not torn away', tag:'keyfind',
    sections:[
      { h:'Why it matters', items:[
        'The ship\\u2019s one small boat was gone from above the main hatch, and the evidence read as a deliberate launch rather than a loss over the side.',
        'A length of rope was found trailing from the ship, frayed at the end — the origin of the idea that the boat was tied astern and then parted.',
        'Everything about the abandonment looks orderly and voluntary. That is the hardest fact in the case, because an orderly evacuation implies a reason, and no reason was ever found.',
      ]},
    ], docs:[] },
},

{
  id:'nostruggle', x:3580, y:1270, type:'bomb', tier:2, label:'No sign of\\nstruggle',
  detail:{ title:'No sign of violence or struggle', subtitle:'The finding that closes off most of the obvious answers', tag:'bomb',
    sections:[
      { h:'What the boarding party found', items:[
        'The crew\\u2019s personal effects, including seamen\\u2019s chests, oilskins and pipes, were still aboard and undisturbed. Men fleeing violence do not pack, and men taken by force do not leave an orderly ship.',
        'About three and a half feet of water in the hold — significant, but well within what her pumps could handle and not enough to sink her.',
        'The ship\\u2019s papers were gone, but the log slate was not, which fits a captain leaving in a hurry with what mattered.',
      ]},
    ], docs:[] },
},

{
  id:'sword', x:4160, y:1270, type:'warning', tier:3, label:'The\\nsword',
  detail:{ title:'The sword under the captain\\u2019s berth', subtitle:'The hearing\\u2019s one piece of apparent physical evidence', tag:'warning',
    sections:[
      { h:'What it actually was', items:[
        'An ornamental sword was found and the discolouration on it presented at Gibraltar as blood, in support of a mutiny theory.',
        'Analysis found no blood. The marks were rust.',
        'Worth keeping on the board as the example it is: the single most quoted detail of the case was wrong, and was corrected within the same proceeding that produced it.',
      ]},
    ], docs:[] },
},

{
  id:'fate', x:3580, y:1700, type:'danger', tier:1, label:'What happened\\nto the ten?',
  detail:{ title:'Open question', subtitle:'Unresolved since 1872', tag:'danger',
    sections:[
      { h:'The theories that survive contact with the record', items:[
        'Alcohol vapour: a leak from the nine barrels, a bang or a flash, and a precautionary evacuation to a boat tied astern that then parted in weather. Fits the empty barrels, the launched yawl, the trailing rope and the absence of fire damage.',
        'Pumping and misjudgement: a sounding rod or a blocked pump leads Briggs to believe she is filling faster than she is, and he abandons a ship that was never going to sink.',
        'Waterspout or sudden squall: accounts for water in the hold and disordered rigging, but not for an orderly departure with the papers.',
      ]},
      { h:'The theories that do not', items:[
        'Mutiny — no violence, nothing taken, and the sword stain was rust.',
        'Piracy — a cargo worth $36,000 left aboard.',
        'Insurance fraud by collusion — investigated at length at Gibraltar and unsupported; Briggs\\u2019s own stake and family aboard argue against it.',
      ]},
    ], docs:[] },
},

{
  id:'after', x:4160, y:1700, type:'replacement', tier:3, label:'Her last\\nvoyage, 1885',
  detail:{ title:'Afterwards', subtitle:'Twelve more years, then deliberately wrecked', tag:'replacement',
    sections:[
      { h:'The end', items:[
        'She sailed on under a succession of owners, unprofitably, with the story attached to her.',
        'In 1885 her last master ran her deliberately onto the Rochelois Bank off Haiti in an attempted insurance fraud. She would not sink quickly; the scheme was exposed.',
        'The wreck closed the ship\\u2019s history. The question of December 1872 stayed open.',
      ]},
    ], docs:[] },
},

{
  id:'note-demo', x:2360, y:1700, type:'sticky', tier:3, label:'Demo board.\\nDrag me.',
  detail:{ title:'This is a demonstration board', subtitle:'Public-domain subject, no real case material', tag:'sticky',
    sections:[
      { h:'Try it', items:[
        'Drag any circle to move it. Drag the handle at its corner to resize, and double-click that handle to reset.',
        'Click a circle to read its detail panel.',
        'Hit the Edit button in the top bar, then the Key and Style buttons, to recolour and restyle every node type live.',
        'Your changes save in your own browser only. Nothing here reaches a server, and nothing you do affects anyone else\\u2019s view.',
      ]},
    ], docs:[] },
},

{
  id:'note-scroll', x:600, y:1700, type:'sticky', tier:3, label:'Scroll down\\nfor the map',
  detail:{ title:'The map section', subtitle:'Below the board', tag:'sticky',
    sections:[
      { h:'What is down there', items:[
        'Leaflet and OpenStreetMap, with no API key anywhere. Pick a location to fly to it, or click anywhere on the map to drop a pin.',
        'The Dei Gratia circle on the board is filled with a live map rather than a photograph — the same mechanism, scaled into a node.',
      ]},
    ], docs:[] },
},

];

const EDGES = [
  ['celeste','briggs','strong'],
  ['celeste','deigratia','strong'],
  ['celeste','fate','strong'],
  ['briggs','sarah','strong'],
  ['briggs','crew','normal'],
  ['briggs','yawl','normal'],
  ['celeste','cargo','normal'],
  ['cargo','barrels','bomb'],
  ['barrels','fate','bomb'],
  ['amazon','celeste','normal'],
  ['deigratia','morehouse','strong'],
  ['deigratia','logslate','normal'],
  ['morehouse','sword','normal'],
  ['logslate','fate','normal'],
  ['yawl','nostruggle','strong'],
  ['yawl','fate','bomb'],
  ['nostruggle','fate','strong'],
  ['sword','nostruggle','normal'],
  ['celeste','after','normal'],
  ['fate','after','normal'],
];
"""

s = replace_span(s, r"^const ZONES = \[", r"^const EDGES = \[", ZONES, "ZONES..EDGES")
must("real case zones gone", "littering" not in s and "261000015" not in s)
must("demo zones in", "Mary\\nCeleste" in s and "Dei Gratia" in s)

# ───────────────────────── storage keys (avoid collisions) ─────────────────────
for old, new in (
    ("lemmondociere_v1", "wall_demo_v1"),
    ("lemmondociere_colors_v1", "wall_demo_colors_v1"),
):
    s = s.replace(f"'{old}'", f"'{new}'")
must("storage keys repointed", "lemmondociere" not in s)

# ─────────────────── disable the two server-fed feed sections ──────────────────
s = s.replace("channelId: 'UC69kQbE6q52QEYQZt3LAjbQ'", "channelId: ''")
must("video desk disabled", "channelId: ''" in s)

# the two `enabled: true` flags are NEWS_CONFIG.watch and NEWS_CONFIG.onion
n_before = s.count("enabled: true")
s = s.replace("enabled: true", "enabled: false")
must("both news sections disabled", n_before == 2 and "enabled: true" not in s)

# ────────── remaining identifiers outside the data block ──────────
# The data arrays were the bulk of it, but the engine comment, the static
# exporter's own output strings, the feed cache keys, one UI placeholder and the
# news configs all still name the real deployment or its subject.
LEFTOVERS = [
    ("// THE LEMMON DOCIERE — APP ENGINE",
     "// INVESTIGATION WALL — APP ENGINE"),
    ("'<title>The Lemmon Docière ('+today+')</title>',",
     "'<title>Investigation wall — demo ('+today+')</title>',"),
    ("a.download = 'lemmon_dociere_static_' + today + '.html';",
     "a.download = 'wall_demo_static_' + today + '.html';"),
    ("cacheKey: 'lemmon_films_cache3'", "cacheKey: 'wall_demo_films_cache1'"),
    ("cacheKey: 'lemmon_watch_cache6'", "cacheKey: 'wall_demo_watch_cache1'"),
    ("cacheKey: 'lemmon_onion_cache'", "cacheKey: 'wall_demo_onion_cache1'"),
    ('placeholder="An address, or a place name like &quot;Kaysville Police Department, UT&quot;"',
     'placeholder="An address, or a place name like &quot;Gibraltar&quot;"'),
    ("freshFilter: /utah|salt lake|provo|ogden|kaysville/i",
     "freshFilter: /gibraltar|azores|genoa/i"),
    ("'kaysville':[41.03,-111.94],", ""),
]
for old, new in LEFTOVERS:
    must(f"leftover present: {old[:46]}", old in s)
    s = s.replace(old, new)

# The watch/onion queries are the real deployment's research subject. Both
# sections are switched off above, but leaving the queries in source would
# still telegraph what the private build is about, so they go too.
s = replace_span(
    s,
    r"^      queries: \[",
    r"^      queries: \[",
    """      queries: [
        'Mary Celeste',
        'maritime mystery derelict ship',
      ],
""",
    "watch queries",
    term="\n      ],\n",
)
s = replace_span(
    s,
    r"^      archiveQueries: \[",
    r"^      archiveQueries: \[",
    """      archiveQueries: [
        'theonion.com ship', 'theonion.com "lost at sea"',
      ],
""",
    "onion archiveQueries",
    term="\n      ],\n",
)

# ──────────── remove the chrome of the sections that are switched off ─────────
# Turning a feed section off in its config stops it fetching, but its markup
# still renders — and these three headings name the real deployment's channel
# and subject. A demo with three empty sections and a nav pointing at them is
# also just bad, so the markup and the nav entries come out together.
dead_start = s.index('<div class="pageSection" id="filmsSection">')
dead_end = s.index("</div>\n\n<div id=\"storyLight\">", dead_start) + len("</div>\n")
must("dead section span looks sane", 1000 < dead_end - dead_start < 3000)
removed = s[dead_start:dead_end]
must("span covers all three sections",
     all(k in removed for k in ('filmsSection', 'watchSection', 'onionSection')))
must("span stops before storyLight", 'storyLight' not in removed)
s = s[:dead_start] + s[dead_end:]

for nav in ('    <a class="navlink" data-go="filmsSection">Videos</a>\n',
            '    <a class="navlink" data-go="watchSection">World Watch</a>\n',
            '    <a class="navlink" data-go="onionSection">The Onion</a>\n'):
    must(f"nav link present: {nav.strip()[:40]}", nav in s)
    s = s.replace(nav, "")

must("eagleDog gone", "eagleDog" not in s)
must("Utah headings gone", "Utah police corruption" not in s and "Utah desk" not in s)

# The feed scripts are interleaved with the map script block (NEWS_CONFIG lives
# at the top of it), so they are not safely removable — and they still write
# into the containers that just went. Give them empty hidden ones to write into
# rather than reaching into that entanglement.
STUBS = (
    '<!-- The video and news sections are switched off in this demo build; their\n'
    '     scripts share a block with the map and still address these containers,\n'
    '     so they stay as empty hidden stubs rather than null references. -->\n'
    '<div hidden>\n'
    '  <div id="filmsControls"></div><div id="filmsGrid"></div>\n'
    '  <div id="watchMap"></div><div id="watchStrip"></div>\n'
    '  <div id="onionMap"></div><div id="onionStrip"></div>\n'
    '</div>\n\n'
)
anchor_sl = '<div id="storyLight"></div>'
must("storyLight anchor found", anchor_sl in s)
s = s.replace(anchor_sl, STUBS + anchor_sl, 1)
must("stubs inserted", 'id="filmsGrid"' in s and 'id="onionStrip"' in s)

# the map blurb still calls them case locations
s = s.replace(
    "Click a 📍 on any case location (in the wall's detail panel, or the chips "
    "below) to view it here.",
    "Click a 📍 on any location (in the wall's detail panel, or the chips "
    "below) to view it here.",
)
must("map blurb reworded", "any case location" not in s)

# ───────────────────────────── title and provenance ───────────────────────────
s = s.replace(
    "<title>The Lemmon Docière</title>",
    "<title>Investigation wall — live demo</title>",
)
must("title replaced", "<title>Investigation wall \u2014 live demo</title>" in s)

# ───────────────── static shim: answer /api/geocode from baked coords ─────────
SHIM = """<script>
/* Static demo shim.
   The real build runs behind a small Express server that proxies geocoding,
   feeds and saves. This copy is a single file on static hosting, so the one
   endpoint the page still needs is answered here from baked coordinates and
   the rest are allowed to fail, which the page already handles: saves fall
   back to this browser's localStorage, and the feed sections are switched off
   in their config above. Coordinates are approximate centres, which is all the
   map needs. */
(function(){
  var BAKED = {
    'new york harbor, new york, ny':        {lat:40.6895, lon:-74.0450, label:'New York Harbor, New York'},
    'santa maria island, azores, portugal': {lat:36.9833, lon:-25.1000, label:'Santa Maria, Azores, Portugal'},
    'gibraltar':                            {lat:36.1408, lon:-5.3536,  label:'Gibraltar'},
    'genoa, italy':                         {lat:44.4056, lon:8.9463,   label:'Genoa, Liguria, Italy'},
    'spencers island, nova scotia, canada': {lat:45.3833, lon:-64.7000, label:"Spencer's Island, Nova Scotia, Canada"},
    'rochelois bank, haiti':                {lat:18.5500, lon:-73.1500, label:'Rochelois Bank, Gulf of Gon\\u00e2ve, Haiti'}
  };
  var _fetch = window.fetch.bind(window);
  window.fetch = function(input, init){
    var url = (typeof input === 'string') ? input : (input && input.url) || '';
    if(url.indexOf('/api/geocode') !== -1){
      var q = '';
      try{
        q = new URLSearchParams(url.slice(url.indexOf('?') + 1)).get('q') || '';
      }catch(e){ q = ''; }
      var hit = BAKED[q.trim().toLowerCase()] || null;
      return Promise.resolve(new Response(JSON.stringify(hit), {
        status: 200, headers: {'Content-Type':'application/json'}
      }));
    }
    return _fetch(input, init);
  };
})();
</script>
"""

anchor = "<script src=\"https://unpkg.com/leaflet@1.9.4/dist/leaflet.js\"></script>"
must("leaflet anchor found", anchor in s)
s = s.replace(anchor, anchor + "\n" + SHIM, 1)
must("shim inserted", "Static demo shim" in s)

# ──────────────────────── map section: demo locations ─────────────────────────
LOCS = """  const LOCATIONS = [
    { id:'ny',   label:'Departure — New York', query:'New York Harbor, New York, NY' },
    { id:'last', label:'Last log entry — Azores', query:'Santa Maria Island, Azores, Portugal' },
    { id:'gib',  label:'Salvage hearing — Gibraltar', query:'Gibraltar' },
    { id:'gen',  label:'Intended destination — Genoa', query:'Genoa, Italy' },
    { id:'built',label:'Built 1861 — Spencer\\u2019s Island', query:'Spencers Island, Nova Scotia, Canada' },
    { id:'end',  label:'Wrecked 1885 — Rochelois Bank', query:'Rochelois Bank, Haiti' },
  ];
"""
s = replace_span(s, r"^  const LOCATIONS = \[", r"^  const LOCATIONS = \[", LOCS, "LOCATIONS", term="\n  ];\n")
must("case locations gone", "Davis County" not in s and "Kaysville" not in s)

# ─────────────────────────── final content sweep ──────────────────────────────
for term in ("Lemmon", "Kaysville", "Davis County", "Ynchausti", "261000015",
             "265005444", "T-Mobile", "lemmondociere", "/files/", "injuries"):
    must(f"no residual '{term}'", term not in s)

ok = sum(1 for _, c in checks if c)
if ok != len(checks):
    print(f"\nchecks: {ok}/{len(checks)} passed - NOT written")
    sys.exit(1)

DST.parent.mkdir(parents=True, exist_ok=True)
DST.write_text(s, encoding="utf-8")
print(f"\n{SRC.name}: {orig_len:,} bytes  ->  {DST}: {len(s):,} bytes")
print(f"checks: {ok}/{len(checks)} passed")
