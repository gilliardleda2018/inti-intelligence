# Changelog

## v0.8.0 — Product Similarity & Portfolio ML
- Added unsupervised product-space representation.
- Added KMeans portfolio clustering with data-driven k selection using silhouette score.
- Added cosine nearest-neighbor product similarity.
- Added conservative near-duplicate radar and sparse portfolio zones.
- Added Portfolio ML dashboard with explicit inference guardrails.

## v0.7.0 — Product Intelligence
- Product Strategic Score and roles.
- Hero Candidate, Premium Anchor, Markdown Watch and structural Redundancy Watch.
- Product Opportunity Radar and Product Explorer.
- Explicit guardrails against inferring sales/cannibalization from public catalog data.

## v0.6.0 — Decision Intelligence
- Added Category Strategic Map and Strategic Score.
- Added explainable category archetypes: Premium Core, Niche Premium, Promotion Pressure, Core Assortment, Long Tail and Watchlist.
- Added executive action recommendations.
- Added Decision Intelligence cockpit page.
- Preserved existing commercial, merchandising and temporal intelligence layers.

## v0.5.0 — Assortment & Merchandising Intelligence
- Added category and color architecture.
- Added variant density and size coverage scoring.
- Added transparent Merchandising Opportunity Engine.
- Added merchandising outputs and cockpit page.
- Preserved all temporal snapshots and existing price/commercial intelligence.

## v0.3.1 — Consolidated Full Build
- Consolidated all previous Sprint 1, Sprint 2, Sprint 3 and Sprint 3.1 work into a single project tree.
- Integrated public catalog collector.
- Integrated catalog normalization and data-quality gates.
- Integrated Premium Cockpit.
- Integrated temporal snapshot comparison.
- Integrated JSON-LD price parser and price probe.
- Integrated resumable full-catalog price enrichment.
- Preserved Snapshot 01 and current analytical outputs.
- Integrated the initial FastAPI demand/inventory MVP and synthetic dataset as supporting modules.
- Replaced fragmented per-sprint dependency files with one root `requirements.txt`.

## v0.4.0 — Commercial Intelligence + Single Source of Truth
- Added a central data layer that automatically prefers `catalog_enriched_latest.csv` when available.
- Rebuilt Data Quality from the active source, fixing the stale `price = MISSING` state after enrichment.
- Unified Overview, Catalog, Price Intelligence and Data Quality on the same source of truth.
- Added Commercial Intelligence page.
- Added transparent Price Position Index, Category Price Tier and Markdown Pressure Index heuristics.
- Added price ladder, category economics and Assortment × Price Matrix.
- Added `build_commercial_intelligence.py` for persisted commercial outputs.
- No Snapshot 02 is created by this update.

## v0.4.1 — Commercial Temporal Intelligence
- Added enriched-snapshot commercial comparison engine.
- Added PRICE_INCREASED / PRICE_DECREASED detection.
- Added MARKDOWN_STARTED / ENDED / DEEPENED / REDUCED detection.
- Added ENTERED_SALE / LEFT_SALE semantic events.
- Added auditable commercial temporal comparison ledger and KPI summary.
- Upgraded Temporal Signals cockpit to separate Catalog Signals from Commercial Signals.
- Fixed snapshot counting so raw and enriched snapshots are not mixed.
