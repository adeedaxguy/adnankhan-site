# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

The primary users of the Lofts Security Center tool are WordPress administrators who suspect unwanted executable or disguised PHP files on a website and need a cautious first response without FTP or shell access. Lofts Studio operators are a secondary audience when a customer needs managed follow-up.

## Product Purpose

Lofts Studio provides a self-service WordPress security tool that lets an administrator install a local plugin, inspect conservative file-integrity signals, and move one reviewed eligible file into a reversible local quarantine. Success is a user who can take the first safe action without exposing their site's files to a third-party dashboard.

## Positioning

The tool is local-first: the WordPress plugin performs the scan and any quarantine on the customer's own server, preserves a restore route, and never exposes a remote shell, automatic bulk deletion, or a claim that a clean scan guarantees safety.

## Operating Context

The journey begins on a dedicated Lofts Studio tool page. A visitor supplies basic contact and website details through the existing Lofts lead endpoint, downloads the plugin, installs it through WordPress Admin, runs a local scan, reviews individual findings, and chooses whether to quarantine one eligible file. Managed monitoring is a separate, later Lofts service rather than a prerequisite for local cleanup.

## Capabilities and Constraints

- The public route must be isolated so it does not alter the established Lofts Studio site experience.
- The page is search-led around the verified commercial intent cluster: “WordPress malware scanner plugin,” with “WordPress malware removal” and “WordPress malware cleanup” only where the copy truthfully describes reviewed quarantine rather than automatic deletion.
- The existing public lead form is the simple signup/access path; it is not an account system and must not imply a remote customer dashboard.
- The WordPress plugin scans high-risk writable upload and cache paths and compares available WordPress core files against WordPress.org checksums.
- The app's existing multi-tenant control-plane UI is an in-memory demo and cannot be made public as a shared customer console until durable identity, storage, and tenant isolation exist.

## Brand Commitments

Use the existing Lofts Studio identity and quiet, direct editorial voice. Avoid hype, fear-based claims, and aggressive service sales. The feature is called “Lofts Security Center for WordPress.”

## Evidence on Hand

- Installable plugin source and tests: `/Users/adeedaxguy/website-security-platform/agents/wordpress/security-center-agent/`.
- Existing local-first security design and tests: `/Users/adeedaxguy/website-security-platform/README.md`.
- Existing Lofts lead endpoint: `api/contact.js`.
- Keyword research was limited to live SERP evidence because the configured SEO workspace currently has DataForSEO disconnected; the relevant current SERP includes WordPress malware scanner, malware removal plugin, and cleanup intent, alongside explicit warnings against automatic removal claims.

## Product Principles

1. Local action stays under the WordPress administrator's control.
2. Review before quarantine, and quarantine before irreversible deletion.
3. A scanner reports evidence; it never certifies that a site is clean.
4. The public tool must be useful without exposing a not-yet-production control plane.

## Accessibility & Inclusion

The flow must remain usable with keyboard navigation, visible focus states, clear labels, native form controls, readable error recovery, and responsive layouts.
