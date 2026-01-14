Format sponsor search results into structured, professional output.

Take raw sponsor data and format it as:

1. **Summary Report** - Overview with total count by category
2. **Detailed List** - Each sponsor with:
   - Name
   - Type (Corporation/Foundation/NGO/Individual)
   - Contact information
   - Giving history/range
   - Relevance score (1-10)
   - Mission alignment notes

3. **CSV Format** - Ready for export with columns:
   Name, Type, Contact, Phone, Email, Website, Giving_History, Relevance_Score, Notes

4. **JSON Format** - Structured data:
```json
{
  "total": number,
  "categories": {
    "corporations": [...],
    "foundations": [...],
    "ngos": [...],
    "individuals": [...]
  }
}
```

Prioritize sponsors by relevance score and format for easy review.