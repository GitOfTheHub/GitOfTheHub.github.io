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

## The domain (done 2026-09-15)

`harjoatbhamra.com` was bought through Wix, which registers domains via Network Solutions —
that is why whois names Network Solutions while everything is managed in the Wix account.
Wix does not allow a registrant to move nameservers off Wix, so the DNS records themselves
were repointed inside Wix (Account → Domains → ⋯ → Manage DNS records):

| Record | Host | Value |
|---|---|---|
| A | harjoatbhamra.com | 185.199.108.153 |
| A | harjoatbhamra.com | 185.199.109.153 |
| A | harjoatbhamra.com | 185.199.110.153 |
| A | harjoatbhamra.com | 185.199.111.153 |
| CNAME | www | gitofthehub.github.io |

GitHub Pages then had the custom domain attached and HTTPS enforced:

```bash
gh api -X PUT repos/GitOfTheHub/GitOfTheHub.github.io/pages -f cname=harjoatbhamra.com
gh api -X PUT repos/GitOfTheHub/GitOfTheHub.github.io/pages -F https_enforced=true
```

`www` 301-redirects to the apex — that is GitHub's own behaviour and is correct.

Wix's DNS hosting stays in place because it comes with the registration; no Wix site plan is
needed for it. Left over in the Wix zone: `m.harjoatbhamra.com` (Wix's mobile host), which now
points at nothing useful and can be deleted.

### Money

- **Wix Premium plan (VIP):** auto-renew already OFF, prepaid to **3 Jan 2027**, then it lapses.
  No refund is possible this far into the term, so there is nothing to cancel — let it expire.
- **Domain registration:** separate Wix subscription, renews **10 Nov 2027** on a 3-year cycle.
  This is the one to keep.
- A Cloudflare zone for the domain was created during this work and is unused (it never
  activated, because the nameservers cannot leave Wix). Delete it, or keep it in case the
  domain is ever transferred to Cloudflare Registrar — which is the way to get off Wix
  entirely and onto cheaper renewals, and can be done any time before Nov 2027.

## Verifying the domain

```bash
dig +short A harjoatbhamra.com @ns12.wixdns.net    # authoritative — the truth
dig +short A harjoatbhamra.com                      # your resolver — may lag up to an hour
curl -sI https://harjoatbhamra.com | head -3
```

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
