## Why

We need a systematic way to manage and calculate bulk tier pricing for products, enabling volume discounts for customers ordering multiple cases. Currently there's no structured way to handle tier pricing (e.g., 1-4 cases at $81.60, 5-9 cases at $78.72, 10+ cases at $75.84), making it difficult to provide accurate bulk pricing quotes.

## What Changes

- Add CSV-based tier pricing data storage system
- Create Python utilities for loading, validating, and calculating tier pricing
- Add CLI functionality to display tier pricing for specific products  
- Implement pricing calculation engine that finds the best-matching tier for any quantity
- Add tier pricing validation to detect gaps and overlaps in pricing ranges

## Capabilities

### New Capabilities
- `tier-pricing-data-management`: CSV-based storage and loading of product tier pricing data with validation
- `tier-pricing-calculation`: Calculate optimal pricing for any case quantity based on tier rules
- `tier-pricing-cli`: Command-line interface to display and query tier pricing information

### Modified Capabilities
<!-- No existing capabilities are being modified - this is all new functionality -->

## Impact

**New Files:**
- `data/tier_pricing.csv` - Structured tier pricing data storage
- `tier_pricing_manager.py` - Core tier pricing utilities and calculations

**Modified Files:**
- `main.py` - Add `--show-tiers` CLI option for tier pricing display

**Dependencies:**
- No new external dependencies required
- Uses existing `utils/terminal_colors` for output formatting

**Data Model:**
- Tier pricing stored in CSV format with columns: product_id, product_name, category_code, case_pack_qty, tier_level, qty_min_cases, qty_max_cases, piece_price, case_price
- Local storage only - no Alibaba API synchronization required