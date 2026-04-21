## Context

The `/icbu/product/schema/update` endpoint on Alibaba's OpenAPI v4 enables updating product information (descriptions, properties, metadata) for existing products. The implementation in `buyer_item_update.py` discovered that the endpoint requires XML-formatted schema data, proper parameter mapping, and category context. This design documents the technical patterns, parameter structure, and error handling approach.

## Goals / Non-Goals

**Goals:**
- Document required XML schema format and parameter structure for product schema updates
- Establish error handling patterns for common API failures
- Provide clear guidance on category ID requirement and parameter mapping
- Enable developers to extend product update capabilities for additional metadata fields

**Non-Goals:**
- Modifying Alibaba API endpoint behavior or creating wrapper versions
- Supporting bulk product updates (single product per request)
- Handling product creation (only updates to existing products)
- Supporting non-schema product operations (inventory, display status handled by separate endpoints)

## Decisions

**1. XML-Based Schema Format**
- **Decision**: Use XML-formatted schema_data parameter with `<ProductEdit>` root element
- **Rationale**: Alibaba API v4 requires XML for schema operations; discovered through API error responses. XML format allows structured field updates without JSON serialization.
- **Alternative Considered**: JSON format (rejected due to API validation error `API_SCHEMA_XML_PARSE_ERROR`)

**2. Mandatory Category ID Parameter**
- **Decision**: Require `cat_id` (category ID) as mandatory parameter alongside product_id
- **Rationale**: Alibaba requires category context for schema validation; enables proper field validation against category-specific schema rules
- **Alternative Considered**: Auto-discover category from product (rejected due to additional API call overhead)

**3. XML Character Escaping**
- **Decision**: Pre-process description text to escape XML special characters (`&`, `<`, `>`, `"`, `'`)
- **Rationale**: Prevents XML parsing errors when product descriptions contain special characters or HTML snippets
- **Alternative Considered**: URL encode or CDATA wrapping (CDATA rejected as more fragile; URL encoding rejected as interpretation complexity)

**4. Language Parameter Requirement**
- **Decision**: Make language parameter mandatory with default value "ENGLISH"
- **Rationale**: API validation error confirmed language is required; defaults to English but overridable
- **Alternative Considered**: Auto-detect from access token locale (rejected as adding complexity without clear benefit)

## Risks / Trade-offs

- **Risk**: XML formatting errors from product descriptions containing markup. **Mitigation**: Pre-escape special characters; validate XML before sending to API
- **Risk**: Users must know the category ID in advance. **Mitigation**: Provide helper command to fetch product details and extract category ID
- **Risk**: API requires exact XML element names; field updates may fail silently if schema is wrong. **Mitigation**: Log full API request/response; validate response includes `"success": true`
- **Trade-off**: Single product per request (not batched). **Mitigation**: Acceptable for most workflows; document parallel execution patterns for bulk updates
- **Trade-off**: Requires redundant parameters (product already has category in Alibaba system, but API requires explicit cat_id). **Mitigation**: Document this requirement clearly in usage guides
- **Note**: Website parameter accepted (ICBU/ALIEXPRESS) but not currently utilized in API request. Reserved for future enhancement when Alibaba API extends website targeting support.
