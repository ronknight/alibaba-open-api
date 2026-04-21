## Context

The Alibaba Product API project currently lacks a systematic approach to managing bulk tier pricing for products. Users need to quote different prices based on case quantity (bulk orders), but there's no structured system to store, validate, or calculate tier-based pricing. The system needs to handle examples like Superman Bag (96 units/case) with 3-tier pricing: 1-4 cases @ $81.60, 5-9 cases @ $78.72, 10+ cases @ $75.84.

## Goals / Non-Goals

**Goals:**
- Create a local tier pricing management system with CSV storage
- Provide Python utilities for loading, validating, and calculating tier pricing  
- Add CLI interface for querying tier pricing information
- Ensure pricing calculations are accurate and handle edge cases
- Validate tier data integrity (no gaps/overlaps in quantity ranges)

**Non-Goals:**
- Integration with live Alibaba API for tier pricing synchronization
- Real-time pricing updates or dynamic pricing algorithms
- Multi-currency support (USD only for initial implementation)
- Web interface or GUI (CLI only)
- Historical pricing tracking or versioning

## Decisions

**CSV Storage Format**
- **Decision**: Use CSV format for tier pricing data storage
- **Rationale**: Human-readable, easily editable in spreadsheets, simple parsing with Python csv module
- **Alternatives**: JSON (more complex structure, less user-friendly), Database (overkill for local reference data)

**Data Model Structure** 
- **Decision**: One row per tier per product with columns: product_id, product_name, category_code, case_pack_qty, tier_level, qty_min_cases, qty_max_cases, piece_price, case_price
- **Rationale**: Denormalized design allows easy CSV management and fast lookups, explicit tier ranges prevent ambiguity
- **Alternatives**: Normalized with separate tiers table (too complex for CSV), Range notation like "1-4" (harder to validate programmatically)

**Class-Based Architecture**
- **Decision**: Create TierPricingManager class with methods for loading, validation, and calculation
- **Rationale**: Encapsulates state (loaded data), provides clean API, enables future extensions
- **Alternatives**: Functional approach (stateless but requires passing data around), Static utility class (less flexible)

**Tier Matching Algorithm**
- **Decision**: Linear search through sorted tiers, match on quantity_cases >= min AND quantity_cases <= max  
- **Rationale**: Simple, predictable, works well for small tier counts (typically 3-5 tiers per product)
- **Alternatives**: Binary search (optimization not needed for small datasets), Range trees (overkill for this use case)

**CLI Integration Approach**
- **Decision**: Add `--show-tiers <product_id>` argument to main.py, extend existing CLI pattern
- **Rationale**: Consistent with existing CLI architecture, reuses argument parsing infrastructure
- **Alternatives**: Separate CLI script (fragmented UX), Interactive mode (scope creep)

## Risks / Trade-offs

**CSV Format Limitations** → Accept trade-off for simplicity
- Risk: CSV doesn't enforce data types or constraints
- Mitigation: Implement validation in TierPricingManager.validate_tier_pricing()

**Manual Data Management** → Document clear update procedures  
- Risk: Users might create gaps/overlaps when editing tier data manually
- Mitigation: Provide validation function that detects and reports data issues

**Performance with Large Datasets** → Monitor and optimize if needed
- Risk: Linear search might become slow with hundreds of products
- Mitigation: Start simple; can optimize with indexing or caching if performance becomes an issue

**No Currency Conversion** → Document USD-only limitation
- Risk: May limit international usage 
- Mitigation: Document assumption clearly, design for future extension with currency field

**No Live API Integration** → Clearly communicate local-only nature
- Risk: Users might expect tier pricing to sync with Alibaba automatically
- Mitigation: Document that this is local reference data only, not synchronized with live API