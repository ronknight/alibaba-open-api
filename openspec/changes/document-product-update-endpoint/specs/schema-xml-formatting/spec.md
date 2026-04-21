## ADDED Requirements

### Requirement: Format product schema data as XML with proper structure
The system SHALL format product schema data as XML with a `<ProductEdit>` root element containing the fields to update. The XML SHALL be well-formed, properly encoded in UTF-8, and include XML declaration.

#### Scenario: Minimal XML schema with description field
- **WHEN** constructing XML schema data with only a description field
- **THEN** the XML contains `<?xml version="1.0" encoding="UTF-8"?>` declaration and `<ProductEdit><Description>...content...</Description></ProductEdit>` structure

#### Scenario: Description with special XML characters
- **WHEN** product description contains special XML characters (`&`, `<`, `>`, `"`, `'`)
- **THEN** each special character is escaped as: `&amp;`, `&lt;`, `&gt;`, `&quot;`, `&apos;` before being placed in the XML

#### Scenario: Description containing HTML markup
- **WHEN** product description is complex HTML (e.g., `<div>Product</div><p>&copy; Company</p>`)
- **THEN** all `<` characters are escaped to `&lt;`, all `>` characters to `&gt;`, and all `&` characters to `&amp;` to prevent XML parsing errors

#### Scenario: Empty or null description field
- **WHEN** description field is empty string or None
- **THEN** the `<Description>` element is included with empty content (`<Description></Description>`) without causing validation errors

### Requirement: Ensure XML is parseable by Alibaba OpenAPI
The system SHALL validate that XML schema data passes XML parsing before sending to the Alibaba OpenAPI. Parse errors SHALL be caught and reported with details about the XML formatting issue.

#### Scenario: Valid XML passes validation
- **WHEN** XML is well-formed and UTF-8 encoded
- **THEN** no parse errors occur and the XML is accepted by the API

#### Scenario: Malformed XML rejected before API call
- **WHEN** XML contains unclosed tags or invalid structure
- **THEN** the system detects the parse error and raises an exception before attempting the API request

#### Scenario: Non-UTF-8 encoding causes parse error
- **WHEN** XML contains non-UTF-8 bytes in the declaration or content
- **THEN** the system rejects the content with an encoding error message and does not send the request
