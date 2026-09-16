# vpayson.com — splash site

Single-page site for Virginia P. Payson, Basalt CO. One file, no build step,
no dependencies, no framework.

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

**Note:** vpayson.com currently serves the Golden Section Palette tool. Move that
to a subpath (e.g. `/palette`) or its own subdomain before repointing the domain,
so it isn't lost.

## Editing

Everything visual is a CSS custom property in the `:root` block at the top of
`index.html`. The whole palette derives from one number:

```css
--hue: 158;   /* change this and the entire site re-tones */
```

Light and dark palettes are both defined; dark follows the visitor's OS setting.

Content is plain semantic HTML below the `<style>` block — edit the text directly.

## Creating the GitHub repo

```bash
cd vpayson-splash
git init -b main
git add .
git commit -m "Splash site for vpayson.com"
gh repo create vpayson-site --private --source=. --push
```

Swap `--private` for `--public` if you'd rather it be open.
