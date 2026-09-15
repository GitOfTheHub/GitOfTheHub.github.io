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

Do this once the github.io site looks right. Until the DNS records change, the Wix site stays up and nothing breaks.

**1. Find where the domain's DNS is managed.** If it was bought through Wix, the nameservers point at Wix and the records are edited in the Wix dashboard (Domains → harjoatbhamra.com → DNS Records). Check with:

```bash
dig +short NS harjoatbhamra.com
```

**2. Replace the existing A / CNAME records for the apex and `www` with GitHub's.** Delete Wix's records for those hosts first — leftovers will keep serving the old site.

Apex (`harjoatbhamra.com`) — four A records:

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

and, if the registrar supports AAAA, four more:

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

**3. Tell GitHub about the domain** (repo Settings → Pages → Custom domain), or:

```bash
gh api -X PUT repos/GitOfTheHub/GitOfTheHub.github.io/pages -f cname=harjoatbhamra.com
```

GitHub re-checks DNS, then issues a Let's Encrypt certificate. Once "Enforce HTTPS" can be ticked (usually within an hour of propagation), tick it.

**4. Verify.**

```bash
dig +short harjoatbhamra.com
curl -sI https://harjoatbhamra.com | head -3
```

**5. Cancel the Wix plan** once the new site has been live for a few days. Keep the domain registration itself — only the hosting plan is being retired.

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
