## ADDED Requirements

### Requirement: Calculate tier pricing for case quantity
The system SHALL calculate the best-matching tier price for a given product and case quantity. The system SHALL find the tier where qty_min_cases <= quantity_cases <= qty_max_cases.

#### Scenario: Calculate price for low-tier quantity
- **WHEN** user requests pricing for 3 cases of Superman Bag (product_id "11000023639542")  
- **THEN** system SHALL return Tier 1 pricing: $0.85/piece, $81.60/case

#### Scenario: Calculate price for mid-tier quantity
- **WHEN** user requests pricing for 7 cases of Superman Bag
- **THEN** system SHALL return Tier 2 pricing: $0.82/piece, $78.72/case  

#### Scenario: Calculate price for high-tier quantity
- **WHEN** user requests pricing for 15 cases of Superman Bag
- **THEN** system SHALL return Tier 3 pricing: $0.79/piece, $75.84/case

#### Scenario: Handle exact tier boundary
- **WHEN** user requests pricing for exactly 5 cases (tier boundary)
- **THEN** system SHALL return the tier where 5 falls within the range (Tier 2)

#### Scenario: Handle product not found
- **WHEN** user requests pricing for a non-existent product_id
- **THEN** system SHALL return None

#### Scenario: Handle quantity outside all tiers
- **WHEN** user requests pricing for 0 cases (below minimum)
- **THEN** system SHALL return None

### Requirement: Return detailed pricing information
The system SHALL provide detailed pricing breakdown including total costs and unit calculations when requested.

#### Scenario: Return basic pricing information
- **WHEN** user requests pricing with return_details=False
- **THEN** system SHALL return price_per_piece, price_per_case, and total_price only

#### Scenario: Return detailed pricing information
- **WHEN** user requests pricing with return_details=True  
- **THEN** system SHALL return product_id, product_name, quantity_cases, case_pack_qty, tier_level, tier ranges, prices, total_price, and total_units

#### Scenario: Calculate correct total price
- **WHEN** user orders 7 cases at $78.72/case
- **THEN** total_price SHALL equal $551.04 (7 × $78.72)

#### Scenario: Calculate correct total units
- **WHEN** user orders 7 cases of Superman Bag (96 units/case)
- **THEN** total_units SHALL equal 672 units (7 × 96)

### Requirement: Support convenience pricing functions
The system SHALL provide standalone functions that don't require managing a TierPricingManager instance directly.

#### Scenario: Use convenience function for quick lookup
- **WHEN** user calls get_tier_price(product_id, quantity_cases)
- **THEN** system SHALL automatically load tier data and return pricing details

#### Scenario: Handle convenience function with custom manager
- **WHEN** user calls get_tier_price() with an existing TierPricingManager instance
- **THEN** system SHALL use the provided manager instead of creating a new one