# vpayson.com

Portfolio site for Virginia P. Payson, Basalt CO. No build step, no
dependencies, no framework. Auto-deploys to Render on every push to `main`.

```
index.html                       home — Applications, then Selected work
settings.html                    re-tone the site: hue, chroma, accent, typeface
palette/                         Color Theory Wheel + Golden Section Palette
work/evergreen/index.html        route driver app — case study
work/evergreen/walkthrough.html  the interactive demo
work/evergreen/css/              copied from the app, so the demo looks right
```

## The Evergreen demo is a deliberate copy, not a link

`work/evergreen/walkthrough.html` was copied out of the `evergreen-driver-app`
repo rather than linked to the running service, and **it makes zero network
calls** — no `fetch`, no WebSocket, no Maps key. Keep it that way. The reasons:

- Linking would publish the client's production hostname to every visitor.
- A deploy on the client's service can't change what this page shows.
- It keeps working after the engagement ends, or if that service is deleted.

Every customer, address, note and gate code in it is invented, and the intro
says so. The original used real streets and named real Carbondale developments,
which was fine internally and wrong for a public page — if you ever re-copy the
file from the app, redo that sanitisation.

The same applies to `work/evergreen/img/`. Those three screenshots show demo
data, but they were captured with the client's wordmark in the app's top bar,
so the bar is **cropped off** (86px from the two board shots, 79px from the
phone). Uncropped originals are in git history. If you re-shoot them, crop
again — or stop cropping once the client is named publicly, which is the open
item below.

## Open items

- [ ] **Name the client in the case study.** It currently says "a compost and
      waste hauler" rather than Evergreen ZeroWaste, pending Alyssa's sign-off
      on public credit. One-line change in `work/evergreen/index.html` once she
      agrees — and worth doing, the environmental angle is the point.
- [ ] **`ACCESS_CODE` / `ADMIN_CODE` on the driver app.** Unrelated to this repo
      but blocking the above: both are unset in Render, so `gate.js` skips the
      gate entirely and real route data is readable by anyone with the
      hostname. Fix before crediting the client publicly. Drivers will each
      need the `?c=CODE` link once, so time it with Alyssa, not mid-route.
- [ ] **`sundancefirearms` and `carolynn-heil`** — both deployed 2026-09-25.
      Add to Selected work if they are launched and the clients are happy.
- [ ] **RISD** is deliberately not cited in the hero strip for now. The original
      wording is in an HTML comment there if it should go back.

Not for public listing: the investigative wall projects (BAM, Apostasy, the
Lemmon docket, the case reference tracker). Confidential case documentation —
describe the capability if useful, but do not link them.

## Deploying to Render

1. Push this folder to its own GitHub repo (see below).
2. Render dashboard → **New +** → **Static Site**.
3. Connect the repo.
4. Settings:
   - **Build Command:** *(leave empty)*
   - **Publish Directory:** `.`
5. Create. It deploys in well under a minute.

### Pointing vpayson.com at it

In Render → your static site → **Settings → Custom Domains** → add both
`vpayson.com` and `www.vpayson.com`. Render shows you the DNS records to set.

At your registrar (currently resolving to 162.241.253.117 — Bluehost/Unified Layer):

| Type | Name | Value |
|---|---|---|
| A | `@` | the IP Render gives you |
| CNAME | `www` | the `.onrender.com` hostname Render gives you |

Render issues the TLS certificate automatically once DNS resolves. Propagation
is usually minutes, occasionally up to a few hours.

*(Done: the palette tool was moved to `/palette` so the domain could be
repointed without losing it.)*

## Editing

Everything visual is a CSS custom property in the `:root` block at the top of
`index.html`. The whole palette derives from one number:

```css
--hue: 158;   /* change this and the entire site re-tones */
```

Light and dark palettes are both defined; dark follows the visitor's OS setting.

Content is plain semantic HTML below the `<style>` block — edit the text directly.

### `/settings.html`

Sliders for brand hue, colour intensity and accent hue, plus a typeface picker,
previewing live against real components. It writes a `vp_theme` key to
`localStorage`, and a short applier in the `<head>` of each page reads it before
paint — so a setting follows you around the site **in your browser only**.
Nothing a visitor sees changes until you press **Copy the CSS** and paste the
block into the `:root` of each page.

Adding a page means copying two things into its `<head>`: the token block, and
that applier script. Miss the applier and the new page ignores your settings;
miss the font link and it silently falls back to system-ui — which is exactly
what the whole site was doing until 2026-10-01, because `--font` named Google
Sans Flex but no page ever loaded it.

`work/evergreen/index.html` repeats the same `:root` token block on purpose, so
each page stands alone as one file. If the hue changes, change it in both.

## Deploying a change

```bash
git add -A && git commit -m "…" && git push
```

Render rebuilds on the commit. A static site of this size is live in under a
minute; there is nothing to run locally beyond opening the file in a browser.
