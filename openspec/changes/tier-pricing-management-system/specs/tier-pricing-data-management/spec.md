## ADDED Requirements

### Requirement: Load tier pricing data from CSV
The system SHALL load tier pricing data from a CSV file located at `data/tier_pricing.csv`. The CSV SHALL contain columns: product_id, product_name, category_code, case_pack_qty, tier_level, qty_min_cases, qty_max_cases, piece_price, case_price.

#### Scenario: Successfully load valid CSV file
- **WHEN** TierPricingManager is initialized with a valid CSV file
- **THEN** the system SHALL parse all rows and organize data by product_id

#### Scenario: Handle missing CSV file
- **WHEN** TierPricingManager is initialized but the CSV file does not exist
- **THEN** the system SHALL log a warning and continue with empty tier data

#### Scenario: Handle malformed CSV data
- **WHEN** TierPricingManager encounters invalid data types (non-numeric prices)
- **THEN** the system SHALL log an error and skip the invalid row

### Requirement: Validate tier pricing data integrity
The system SHALL validate tier pricing data to detect gaps and overlaps in quantity ranges for each product.

#### Scenario: Detect quantity range gaps
- **WHEN** validation finds a tier ending at 4 cases followed by a tier starting at 6 cases
- **THEN** system SHALL report a gap error between tiers

#### Scenario: Detect quantity range overlaps  
- **WHEN** validation finds two tiers with overlapping quantity ranges
- **THEN** system SHALL report an overlap error

#### Scenario: Validate tier sequence starts at 1
- **WHEN** validation checks the lowest tier for a product
- **THEN** the lowest tier SHALL start at qty_min_cases = 1

#### Scenario: Validation passes for valid data
- **WHEN** all tiers have contiguous ranges with no gaps or overlaps
- **THEN** validation SHALL return True with no errors

### Requirement: Organize tier data by product
The system SHALL store loaded tier pricing data organized by product_id for efficient lookup and sorted by qty_min_cases within each product.

#### Scenario: Access tiers for specific product
- **WHEN** user requests tiers for product_id "11000023639542"
- **THEN** system SHALL return all tier records for that product in ascending qty_min_cases order

#### Scenario: Handle request for non-existent product
- **WHEN** user requests tiers for a product_id not in the data
- **THEN** system SHALL return None

### Requirement: Reload tier pricing data
The system SHALL provide functionality to reload tier pricing data without recreating the manager instance.

#### Scenario: Reload updated CSV file
- **WHEN** user calls load_tier_pricing() after CSV file has been modified
- **THEN** system SHALL re-parse the CSV and update internal data structures