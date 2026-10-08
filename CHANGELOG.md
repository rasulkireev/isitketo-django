# Changelog

## 2026-10-08

- Add IndexNow ownership verification and automatic post-deployment/hourly public
  sitemap notifications, including observed changes and removals, bounded retry,
  and success-only checkpoints.
- Use full product/blog update timestamps in the sitemap to detect same-day edits.
- Add isolated regression tests and CI for IndexNow transport, route wiring,
  sitemap edits/deletions, batching, and checkpoint recovery.
