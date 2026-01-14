Extract keywords from the user's prompt for sponsor searching.

Given a prompt about finding sponsors, extract and return in JSON format:
- Primary keywords (main topics like 'mental health', 'healing')
- Secondary keywords (related terms)
- Location keywords (cities, states, regions)
- Sector keywords (industries, organization types)
- Budget filters (minimum amounts, ranges)

Consider the Healing NY mission:
- Mental health support
- Arts education  
- Community healing
- New York focus

After extracting keywords, search for potential sponsors matching the criteria and categorize them as:
- Corporations
- Foundations
- NGOs
- Individual donors

Present results with relevance scores.
