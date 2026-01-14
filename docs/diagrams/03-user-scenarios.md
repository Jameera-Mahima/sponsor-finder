# User Scenario Flowcharts

This document shows different user journeys through the sponsor-finder system.

## Scenario 1: Basic Search Flow

```mermaid
flowchart TD
    Start([User wants to find<br/>arts education sponsors]) --> Prompt[User enters search prompt]

    Prompt --> System[System processes request<br/>through 4-phase pipeline]

    System --> Check{Results found?}

    Check -->|Yes, 20+ sponsors| Review[User reviews<br/>generated reports]
    Check -->|No, < 20 sponsors| Refine[System suggests<br/>refining search criteria]

    Refine --> Prompt

    Review --> Quality{Quality<br/>acceptable?}

    Quality -->|Yes| Export[User exports data<br/>Markdown/CSV/JSON]
    Quality -->|No| Adjust[Adjust search parameters<br/>or filters]

    Adjust --> Prompt

    Export --> Use[User loads into CRM<br/>or begins outreach]

    Use --> End([Search Complete])

    style Start fill:#e1f5ff
    style End fill:#e1ffe1
    style Export fill:#ffe1e1
```

## Scenario 2: Iterative Refinement

```mermaid
flowchart TD
    Start([User starts broad search]) --> First[First search:<br/>'Find arts sponsors in NYC']

    First --> Results1[System returns<br/>150+ results]

    Results1 --> TooMany{Too many<br/>results?}

    TooMany -->|Yes| Narrow[User narrows criteria:<br/>'NYC arts sponsors for<br/>disability programs']

    Narrow --> Second[Second search with<br/>refined keywords]

    Second --> Results2[System returns<br/>40 results]

    Results2 --> Better{Better<br/>scope?}

    Better -->|Still too broad| Further[User adds grant size:<br/>'$50k+ grants']
    Better -->|Good| Review

    Further --> Third[Third search with<br/>budget filter]

    Third --> Results3[System returns<br/>22 results]

    Results3 --> Review[User reviews<br/>targeted list]

    Review --> End([Optimal results found])

    style Start fill:#e1f5ff
    style End fill:#e1ffe1
```

## Scenario 3: Category-Specific Search

```mermaid
flowchart TD
    Start([User needs specific<br/>sponsor type]) --> Type{What type<br/>needed?}

    Type -->|Foundations| Found[Search prompt:<br/>'Find foundations supporting<br/>arts education']
    Type -->|Corporations| Corp[Search prompt:<br/>'Find corporate sponsors<br/>for disability arts programs']
    Type -->|Government| Gov[Search prompt:<br/>'Find NYC government grants<br/>for special education arts']

    Found --> Process1[System processes<br/>with foundation focus]
    Corp --> Process2[System processes<br/>with corporate focus]
    Gov --> Process3[System processes<br/>with government focus]

    Process1 --> Cat1[Categorization emphasizes<br/>private/family foundations]
    Process2 --> Cat2[Categorization emphasizes<br/>CSR programs]
    Process3 --> Cat3[Categorization emphasizes<br/>municipal/state grants]

    Cat1 --> Results
    Cat2 --> Results
    Cat3 --> Results

    Results[Targeted sponsor list<br/>in preferred category]

    Results --> Export[User exports<br/>category-specific data]

    Export --> End([Focused outreach begins])

    style Start fill:#e1f5ff
    style End fill:#e1ffe1
```

## Scenario 4: Multi-Program Search

```mermaid
flowchart TD
    Start([CSOAF has multiple<br/>programs to fund]) --> Programs{Which programs?}

    Programs --> P1[Dance classes for<br/>students with disabilities]
    Programs --> P2[Adult arts education<br/>online courses]
    Programs --> P3[Free community<br/>workshops]

    P1 --> Search1[Search 1:<br/>'NYC disability dance<br/>education sponsors']
    P2 --> Search2[Search 2:<br/>'Adult learning arts<br/>education funders']
    P3 --> Search3[Search 3:<br/>'Community arts program<br/>sponsors']

    Search1 --> Results1[20 sponsors for<br/>disability programs]
    Search2 --> Results2[15 sponsors for<br/>adult education]
    Search3 --> Results3[25 sponsors for<br/>community programs]

    Results1 --> Combine
    Results2 --> Combine
    Results3 --> Combine

    Combine[Merge results<br/>Remove duplicates]

    Combine --> Dedup[40 unique sponsors<br/>across all programs]

    Dedup --> Prioritize[Prioritize sponsors by:<br/>- Multi-program fit<br/>- Grant size<br/>- Mission alignment]

    Prioritize --> End([Comprehensive sponsor<br/>database created])

    style Start fill:#e1f5ff
    style End fill:#e1ffe1
    style Combine fill:#fff4e1
```

## Common User Paths

### Quick Search (Power User)
1. Enter detailed prompt with all criteria
2. Review results
3. Export to CSV
4. Load into Salesforce

### Exploratory Search (New User)
1. Start with broad prompt
2. Review initial results
3. Refine based on categories found
4. Iterate until optimal scope
5. Export final list

### Targeted Campaign
1. Specify sponsor type + program + location
2. Review high-quality matches
3. Export with contact info
4. Begin personalized outreach

### Research Mode
1. Run multiple searches for different programs
2. Compare sponsor types across searches
3. Identify overlapping prospects
4. Build comprehensive sponsor database
