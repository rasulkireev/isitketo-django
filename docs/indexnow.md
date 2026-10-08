# IndexNow

The site serves a stable public proof at `https://isitketo.org/indexnow-key.txt`.
It is separate from Django's private secret key; no new production credential or
migration is required. `X-Deployment-Revision` identifies the running server build.

GitHub Actions submits the canonical public sitemap after **Deploy Prod Server**
succeeds and checks for changes hourly at minute 11 UTC (subject to Actions delays).
Only sitemap pages are submitted: products, blog posts, categories, and public
listing pages. Admin, accounts, API, search, and newsletter endpoints are excluded.

Product and blog `updated_at` values are serialized as full ISO timestamps, so
normal model saves, including same-day edits, are detected. New and previously
observed removed URLs are included. Deployments resubmit all public URLs to cover
static/template changes. A revision mismatch fails without notifying IndexNow.

The standard-library client uses batches of at most 10,000 URLs, bounded requests,
and bounded transient retries. Permanent errors fail visibly. Checkpoint state is
saved atomically only after all batches are accepted (200 or 202). HTTP 202 means
key validation is pending. Neither response guarantees indexing or rankings.

## Manual operations

No Django or third-party dependencies are needed for the standalone CLI:

```
python isitketo/indexnow.py --site-url https://isitketo.org --dry-run
python isitketo/indexnow.py --site-url https://isitketo.org --state indexnow-state.json
python isitketo/indexnow.py --site-url https://isitketo.org --state indexnow-state.json --force
```

An application management command is also available:
`python manage.py submit_indexnow --dry-run`.
Run or rerun the **IndexNow public URL changes** workflow for production operations;
its GitHub cache retains the last successful checkpoint. Local state is separate.
The workflow has read-only repository permissions and serialized execution.

## Limits

- GitHub cache eviction loses historical removal evidence; the next run safely
  resubmits the current sitemap. Failed batches may be retried more than once.
- Pages created and deleted between scans cannot be observed.
- `QuerySet.update`, bulk changes, and `save(update_fields=...)` must explicitly
  update `updated_at` or be followed by a forced notification/deployment.
- Existing category/listing pages have no per-edit timestamps and are refreshed
  on deployment; product/blog detail edits are detected hourly.
- This integration does not repair existing duplicate URLs or page content issues.

## Tests

Install application requirements plus `pytest==8.3.5 pytest-django==4.11.1`, then
run `python -m pytest -q`. Isolated test settings use SQLite and fake credentials;
network submission tests mock transport and never contact search engines.
