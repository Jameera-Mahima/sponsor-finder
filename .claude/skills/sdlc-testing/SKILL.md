---
name: sdlc-testing
description: Comprehensive testing guidance. Use when writing tests, debugging, or validating functionality. Covers unit, integration, and system testing.
---

# SDLC Testing Skill

## When to Use This Skill
- Writing tests for new features
- Debugging issues
- Validating functionality
- Creating test plans
- Quality assurance

## Testing Strategy

### 1. Unit Testing
**Purpose:** Test individual functions in isolation

**Guidelines:**
- Test one thing at a time
- Mock external dependencies
- Aim for 80%+ coverage
- Test happy path and edge cases

**Example Test Structure:**
\\\python
def test_keyword_extraction():
    # Arrange
    prompt = "Find mental health sponsors in NYC"
    
    # Act
    keywords = extract_keywords(prompt)
    
    # Assert
    assert len(keywords['primary']) > 0
    assert 'mental health' in keywords['primary']
    assert 'NYC' in keywords['location']
\\\

### 2. Integration Testing
**Purpose:** Test how components work together

**What to Test:**
- API endpoints (if applicable)
- Database operations
- External service calls
- Data flow between components

**Example:**
\\\python
def test_complete_workflow():
    # Test Phase 1 -> Phase 2 integration
    keywords = keyword_extractor.extract(prompt)
    sponsors = web_researcher.search(keywords)
    assert len(sponsors) > 0
\\\

### 3. System Testing
**Purpose:** Test entire system end-to-end

**What to Test:**
- Complete workflows
- Performance (response time)
- Error handling
- Data validation

### 4. Edge Case Testing
Always test:
- **Empty inputs:** What if prompt is empty?
- **Null values:** What if no sponsors found?
- **Large datasets:** Can it handle 1000 sponsors?
- **Invalid data:** What if keywords are malformed?
- **Network failures:** What if web search fails?

## Test Categories

### Positive Tests (Happy Path)
- Valid inputs produce expected outputs
- Workflow completes successfully

### Negative Tests (Error Cases)
- Invalid inputs are rejected gracefully
- Errors are logged properly
- System doesn't crash

### Boundary Tests
- Minimum values (0 sponsors)
- Maximum values (500 sponsors)
- Edge of valid range

## Test Template

\\\python
def test_sponsor_search():
    \"\"\"
    Test complete sponsor search functionality
    
    Given: A valid search prompt
    When: The workflow executes
    Then: Return validated sponsor list
    \"\"\"
    # Arrange
    prompt = "Find mental health sponsors in NYC"
    expected_min_sponsors = 10
    
    # Act
    results = search_sponsors(prompt)
    
    # Assert
    assert len(results) >= expected_min_sponsors
    assert all('name' in sponsor for sponsor in results)
    assert all('type' in sponsor for sponsor in results)
    assert all('relevance_score' in sponsor for sponsor in results)
    
    # Verify data quality
    for sponsor in results:
        assert sponsor['relevance_score'] >= 5
        assert sponsor['name'] != ''
        assert sponsor['type'] in ['Corporation', 'Foundation', 'NGO', 'Individual']
\\\

## Testing Checklist

Before marking feature complete:
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Edge cases tested
- [ ] Error handling tested
- [ ] Performance is acceptable
- [ ] Manual testing completed
- [ ] No regressions in existing features
- [ ] Test coverage =80%

## Example Usage

Input: "Create tests for the CSV export feature"

Output:
- Unit tests for export function
- Integration tests with file system
- Edge case tests (empty data, special characters)
- Performance tests (large datasets)
