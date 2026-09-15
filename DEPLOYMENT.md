# Deployment

The site is built and published by GitHub Actions. Nothing is deployed from this machine.

| | |
|---|---|
| Repo | <https://github.com/GitOfTheHub/GitOfTheHub.github.io> (public) |
| Workflow | `.github/workflows/publish.yml` — runs on every push to `main`, and on demand |
| Live now | <https://gitofthehub.github.io> |
| Final URL | <https://harjoatbhamra.com> (after the DNS switch below) |

## Publishing a change

```bash
git add -A && git commit -m "Update publications" && git push
```

The workflow installs Quarto 1.9.37 + Jupyter, runs `quarto render`, and deploys `_site/` to Pages. Takes about 5 minutes. Watch it with:

```bash
gh run watch --exit-status
```

If CV content changed, rebuild the PDFs first (`bash cv/build.sh`) and commit `pdf/Bhamra-CV.pdf` — the workflow does not run LaTeX.

## Switching harjoatbhamra.com off Wix

Verified 2026-09-15:

| | |
|---|---|
| Registrar | **Network Solutions** — the domain is *not* owned by Wix |
| Paid until | 2027-11-10 |
| Nameservers | `ns12.wixdns.net`, `ns13.wixdns.net` — Wix hosts the DNS only |
| MX records | none — no email runs on this domain, so nothing to preserve |

So the domain is kept simply by not cancelling it at Network Solutions. Wix is only providing
the website and the DNS, and both are replaceable. **Order matters: do not cancel the Wix plan
while Wix's nameservers still answer for the domain — the site would go dark.**

**1. At Network Solutions, move DNS off Wix.** Change the nameservers from `ns12/ns13.wixdns.net`
to Network Solutions' own DNS, then edit the zone there. (Cloudflare's free DNS works too, and is
faster, but it means one more account — Network Solutions is already paid for.)

**2. Create the GitHub Pages records.**

Apex (`harjoatbhamra.com`) — four A records:

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

and four AAAA records if the registrar supports them:

```
2606:50c0:8000::153
2606:50c0:8001::153
2606:50c0:8002::153
2606:50c0:8003::153
```

`www` — one CNAME:

```
www  CNAME  gitofthehub.github.io.
```

**3. Tell GitHub about the domain** — only after step 2 has propagated, because setting it makes
`gitofthehub.github.io` redirect to the custom domain:

```bash
gh api -X PUT repos/GitOfTheHub/GitOfTheHub.github.io/pages -f cname=harjoatbhamra.com
```

GitHub re-checks DNS and issues a Let's Encrypt certificate; tick "Enforce HTTPS" once it is offered.

**4. Verify.**

```bash
dig +short harjoatbhamra.com
curl -sI https://harjoatbhamra.com | head -3
```

**5. Only now cancel the Wix Premium plan** (Wix dashboard → Subscriptions). Keep the Network
Solutions registration — that is what owns the name.

Optional, later: Network Solutions renewals are expensive. The domain can be transferred to
Cloudflare Registrar (at cost, about $11/yr) any time; the transfer adds a year to the expiry.

## If a push does not start a deploy

This happened once when the repo was new: pushes created no workflow run at all (no Actions
check suite on the commit), while manual runs worked. Toggling Actions off and back on for the
repo re-attached the push trigger:

```bash
gh api -X PUT repos/GitOfTheHub/GitOfTheHub.github.io/actions/permissions -F enabled=false
gh api -X PUT repos/GitOfTheHub/GitOfTheHub.github.io/actions/permissions -F enabled=true -f allowed_actions=all
```

Either way, a deploy can always be started by hand:

```bash
gh workflow run "Render and publish" --ref main
```

## Notes

- `_quarto.yml` already sets `site-url: https://harjoatbhamra.com`, so the sitemap and canonical links point at the final domain. Until the DNS switch they will name a URL that still serves the Wix site; no action needed, it resolves itself on cutover.
- Pages is configured with `build_type: workflow` — there is no `gh-pages` branch, and `_site/` is never committed.
