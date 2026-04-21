## ADDED Requirements

### Requirement: Display tier pricing via CLI
The system SHALL provide a `--show-tiers <product_id>` command-line option in main.py to display all tier pricing information for a specific product.

#### Scenario: Display tiers for valid product
- **WHEN** user runs `python main.py --show-tiers 11000023639542`
- **THEN** system SHALL display product name, case pack quantity, and formatted tier table

#### Scenario: Handle invalid product ID
- **WHEN** user runs `--show-tiers` with a non-existent product_id  
- **THEN** system SHALL display warning message "Product {id} not found in tier pricing data"

#### Scenario: Handle missing tier data file
- **WHEN** user runs `--show-tiers` but tier_pricing.csv does not exist
- **THEN** system SHALL display warning about missing tier pricing file

### Requirement: Format tier pricing output
The system SHALL display tier pricing information in a structured, readable table format with columns for tier level, quantity range, piece price, and case price.

#### Scenario: Display formatted tier table
- **WHEN** system displays tier pricing for Superman Bag
- **THEN** output SHALL include header with product info and aligned columns showing "Tier | Qty Range (cases) | Price/Piece | Price/Case"

#### Scenario: Include product context information
- **WHEN** system displays tier pricing
- **THEN** output SHALL show product_id, product_name, and case pack quantity

#### Scenario: Use color-coded output
- **WHEN** system displays tier pricing information
- **THEN** system SHALL use terminal_colors for success/info/warning formatting

### Requirement: Integrate with existing CLI architecture
The system SHALL extend main.py's existing argument parser to include tier pricing functionality without breaking existing command-line options.

#### Scenario: Add --show-tiers argument
- **WHEN** argument parser is configured
- **THEN** system SHALL add `--show-tiers` argument that accepts a product_id

#### Scenario: Handle --show-tiers with other arguments
- **WHEN** user provides `--show-tiers` along with incompatible options
- **THEN** system SHALL prioritize tier pricing display and ignore conflicting arguments

#### Scenario: Maintain existing CLI functionality
- **WHEN** user runs existing commands without `--show-tiers`
- **THEN** system SHALL operate normally with no impact from tier pricing integration

### Requirement: Standalone demonstration mode
The system SHALL provide demonstration functionality when tier_pricing_manager.py is run directly, showing examples of tier pricing for all available products.

#### Scenario: Run tier_pricing_manager.py as script
- **WHEN** user runs `python tier_pricing_manager.py` 
- **THEN** system SHALL display all products with tier pricing, validation results, and example calculations

#### Scenario: Include example calculations  
- **WHEN** demonstration mode runs
- **THEN** system SHALL show sample pricing calculations for different quantities and products