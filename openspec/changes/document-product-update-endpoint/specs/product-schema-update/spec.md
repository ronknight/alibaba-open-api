## ADDED Requirements

### Requirement: Update product schema via /icbu/product/schema/update endpoint
The system SHALL allow updating product information (descriptions, properties, metadata) for an existing product using the `/icbu/product/schema/update` endpoint. The endpoint requires POST request with app credentials, product ID, category ID, language, and XML-formatted schema data. The API SHALL return success confirmation with product_id on successful update.

#### Scenario: Successful product schema update
- **WHEN** a valid product_id, cat_id, language, and XML schema_data are provided with valid credentials
- **THEN** the API returns HTTP 200 with `"success": true` and echoes the product_id

#### Scenario: Missing required category ID
- **WHEN** product_id is provided but cat_id parameter is omitted
- **THEN** the API returns HTTP 200 with error code `MissingParameter` and message indicating cat_id is required

#### Scenario: Missing language parameter
- **WHEN** product_id and cat_id are provided but language parameter is omitted
- **THEN** the API returns HTTP 200 with error code `MissingParameter` and message indicating language is required

#### Scenario: Invalid XML format in schema data
- **WHEN** schema_data contains malformed XML (e.g., unclosed tags, invalid character encoding)
- **THEN** the API returns HTTP 200 with error code `API_SCHEMA_XML_PARSE_ERROR` and message indicating XML formatting error

#### Scenario: Unauthenticated request
- **WHEN** request is sent without valid access_token or with expired token
- **THEN** the API returns HTTP 200 with error code indicating authentication failure

### Requirement: Map product to category before schema update
The calling code SHALL resolve the category ID from the product information before constructing the schema update request. The category ID is required by the API and cannot be auto-discovered from the product_id alone.

#### Scenario: Category lookup integration
- **WHEN** updating a product whose category ID is known (from product listing API)
- **THEN** the category ID is passed to the schema update endpoint with the product_id

#### Scenario: Error when category ID unknown
- **WHEN** attempting to update a product without first retrieving its category ID
- **THEN** the update fails with MissingParameter error for cat_id

### Requirement: Accept optional or default description parameter
The system SHALL accept an optional description parameter. If description is not provided by the caller, the system SHALL use a default description from `data/sample.json`.

#### Scenario: Explicit description provided
- **WHEN** a custom description is provided as parameter
- **THEN** the provided description is used in the schema update request (with proper XML escaping applied)

#### Scenario: Default description used
- **WHEN** description parameter is omitted or None
- **THEN** the system reads description from `data/sample.json` and uses it for the schema update
