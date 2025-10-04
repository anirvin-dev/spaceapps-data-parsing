# Framer Export Data

This folder contains all NASA Bioscience data exported as JSON for Framer integration.

## Files

- `papers.json` - All 607 papers with summaries (200 processed)
- `claims.json` - 15 consensus claims with evidence
- `topics.json` - 10 research topics with papers
- `gaps.json` - 8 knowledge gaps
- `insights.json` - 15 mission insights
- `sources.json` - 1,507 additional NASA sources
- `stats.json` - Overall statistics

## Usage in Framer

```javascript
// Fetch papers
fetch('/api/papers.json')
    .then(res => res.json())
    .then(data => console.log(data.papers))

// Fetch claims
fetch('/api/claims.json')
    .then(res => res.json())
    .then(data => console.log(data.claims))
```

## Data Structure

See FRAMER_INTEGRATION_GUIDE.md for complete documentation.

## Updates

Run `python3 export_for_framer.py` to regenerate all JSON files.

Last updated: 2025-10-04
