# Agent Interaction Sequence Diagram

This diagram shows the detailed interaction between agents, tools, and data throughout a sponsor search.

```mermaid
sequenceDiagram
    participant User
    participant Claude as Claude Code
    participant KE as Keyword Extractor<br/>(Haiku 4.5)
    participant WR as Web Researcher<br/>(Haiku 4.5)
    participant Cat as Categorizer<br/>(Haiku 4.5)
    participant Val as Validator<br/>(Sonnet 4.5)
    participant FS as File System<br/>(docs/)

    User->>Claude: "Find NYC arts education sponsors<br/>for disability programs with $50k+ grants"

    Note over Claude: Initialize 4-phase workflow

    Claude->>KE: Task: Extract keywords from prompt
    Note over KE: Tools: WebSearch, Read
    KE->>KE: Parse user prompt
    KE->>KE: Load CSOAF mission from CLAUDE.md
    KE->>KE: Extract entities and keywords
    KE->>KE: Structure as JSON
    KE-->>Claude: Keywords JSON:<br/>{primary: ["arts education", "disability"],<br/>location: ["NYC"], grant_size: "$50k+"}

    Claude->>WR: Task: Research sponsors with keywords
    Note over WR: Tools: WebSearch, WebFetch
    WR->>WR: Build search queries
    loop For each keyword combination
        WR->>WebSearch: Search for sponsors
        WebSearch-->>WR: Search results URLs
        WR->>WebFetch: Fetch sponsor website
        WebFetch-->>WR: Website content (markdown)
        WR->>WR: Extract contact info, mission, grants
        WR->>WR: Calculate relevance score
    end
    WR->>WR: Compile sponsor list (15-25)
    WR-->>Claude: Raw Sponsors Array:<br/>[{name, website, mission, contact,<br/>relevance_score}, ...]

    Claude->>Cat: Task: Categorize sponsors by type
    Note over Cat: Tools: Read (no web access)
    Cat->>Cat: Analyze each sponsor's mission
    Cat->>Cat: Identify organizational type
    Cat->>Cat: Group by category
    Cat->>Cat: Add metadata (focus areas, grant range)
    Cat-->>Claude: Categorized Object:<br/>{foundations: [...],<br/>corporations: [...],<br/>ngos: [...], government: [...]}

    Claude->>Val: Task: Validate quality and giving programs
    Note over Val: Tools: WebFetch, WebSearch, Read
    loop For each sponsor
        Val->>WebSearch: Search for recent grants/awards
        WebSearch-->>Val: Grant history results
        Val->>WebFetch: Verify website legitimacy
        WebFetch-->>Val: Current website status
        Val->>Val: Check giving program activity
        Val->>Val: Verify contact information
        Val->>Val: Assess mission alignment
        Val->>Val: Calculate quality score (1-10)
        alt Quality score < 5
            Val->>Val: Remove from list
        else Quality score >= 5
            Val->>Val: Keep and rank
        end
    end
    Val->>Val: Sort by quality score + relevance
    Val-->>Claude: Validated Sponsors:<br/>[20+ sponsors with scores ≥5]<br/>+ Quality Report

    Claude->>FS: Write Markdown report
    FS-->>Claude: File created

    Claude->>FS: Write CSV export
    FS-->>Claude: File created

    Claude->>FS: Write JSON data
    FS-->>Claude: File created

    Claude->>User: ✓ Search complete<br/>Generated 3 reports in docs/<br/>Found 22 validated sponsors

    User->>User: Review reports and begin outreach
```

## Interaction Patterns

### Agent Invocation
- **Trigger**: Claude Code's Task tool with agent name
- **Input**: Structured prompt + previous phase output
- **Output**: JSON data passed to next phase

### Tool Usage by Phase

**Phase 1 (Keyword Extractor)**
- Read: Access CSOAF mission context from CLAUDE.md
- WebSearch: Optional - research unfamiliar terms

**Phase 2 (Web Researcher)**
- WebSearch: Primary - find sponsor prospects
- WebFetch: Primary - crawl sponsor websites for details

**Phase 3 (Categorizer)**
- Read: Only - no external web access needed
- Analyzes in-memory data from Phase 2

**Phase 4 (Validator)**
- WebSearch: Verify recent grant activity
- WebFetch: Check website legitimacy and current status
- Read: Access validation criteria from specs

### Data Handoffs

1. **User → Phase 1**: Natural language prompt
2. **Phase 1 → Phase 2**: Structured keywords JSON
3. **Phase 2 → Phase 3**: Raw sponsor array (unorganized)
4. **Phase 3 → Phase 4**: Categorized sponsor object
5. **Phase 4 → Output**: Validated + ranked sponsor list
6. **Output → File System**: Multiple format exports

### Error Handling

```mermaid
sequenceDiagram
    participant Agent
    participant WebSearch
    participant Fallback

    Agent->>WebSearch: Search for sponsor info

    alt Search succeeds
        WebSearch-->>Agent: Results found
        Agent->>Agent: Process normally
    else Search fails or no results
        WebSearch-->>Agent: Empty/error
        Agent->>Fallback: Try alternative keywords
        alt Fallback succeeds
            Fallback-->>Agent: Alternative results
            Agent->>Agent: Process with warnings
        else Fallback fails
            Fallback-->>Agent: Still no results
            Agent->>Agent: Skip this sponsor with note
        end
    end
```

## Timing Expectations

| Phase | Agent | Expected Duration | Rate Limiting Factor |
|-------|-------|-------------------|---------------------|
| 1 | Keyword Extractor | 10-20 seconds | Model processing |
| 2 | Web Researcher | 2-4 minutes | Web searches + fetches (15-25 sites) |
| 3 | Categorizer | 20-40 seconds | In-memory analysis only |
| 4 | Validator | 2-3 minutes | Web verification (20+ sites) |
| **Total** | **All phases** | **5-7 minutes** | **Web I/O bound** |

## Parallelization Opportunities

- Phase 2: Can parallelize multiple web searches
- Phase 4: Can parallelize sponsor validation checks
- Output: Can write multiple file formats simultaneously
