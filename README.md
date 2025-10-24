# Met Museum Browser

A macOS desktop application for browsing The Metropolitan Museum of Art's Open Access collection. Built with PySide6 and the Met's public API.

## Overview

This application allows users to explore the Met's collection by classification (Paintings, Prints, Sculptures, etc.), with options to filter by image availability and sort chronologically. The app displays up to 80 results with images and metadata including title, artist, department, and creation date.

## Features

- **Browse by Classification**: Select from 100+ classifications from the Met's collection
- **Image Filtering**: Toggle to show only works with displayable public domain images
- **Date Sorting**: Sort results by creation date (ascending or descending)
- **Progressive Loading**: Results appear as they load, with progress indicators
- **Image Cache**: Local cache of ~349k record ids with images for fast filtering

## Requirements

- Python 3.10+
- macOS (for bundled .app) or any platform for development
- Internet connection (for Met API access)

## Installation & Running

### Running from Source

```bash
# Install dependencies
uv sync

# Run the application
uv run python src/main.py
```

## Architecture

The application consists of three main layers:

1. **API Layer** (`src/api/`): Handles communication with the Met API and manages local data indexes
2. **UI Layer** (`src/ui/`): PySide6 components including main window, custom widgets, and worker threads
3. **Data Layer** (`data/`): Local caches for classifications and image availability

## Technical Details

### Classifications

Since the API does not expose the `classification` field, the classifications dictionary is built from the CSV found at https://github.com/metmuseum/openaccess. The list is not sanitized in any way other than marking empty entries as "N/A".

#### Data Coverage

Because of the API limitation and the use of the CSV file, there are about 14,000 new records in the database, and some obsolete records in the CSV file. For this exercise I've decided to leave it this way, under the assumption that for a production app these additional records can be fetched incrementally, dealing with the API rate limits.

- Records in DB: 498,172
- Records in local index: 484,956
- In DB but not local: 14,135
- In local but not DB: 919

### Images

I could not find clear documentation on how to fetch all records that have an image. The API offers a `hasImages` parameter on the search endpoint, but it must be accompanied with a `q` parameter, and a `*` wildcard does not seem to get all records.

I have decided to iterate over the alphabet (a-z) and save all found record IDs in a local cache that can be updated by the user via Tools → Refresh Image Cache. While it's unclear how much of the records with images it finds, this method finds 348,803 records which offers coverage of ~70%.

A secondary issue is that while the API returns records that are supposed to have images, if the image is marked as not in the public domain, the image URL is not provided. In these cases, an additional client-side filter is applied, removing records without displayable images and updating the count to be "approximate".

## Design Decisions

### Two-Column Layout

The application uses a two-column layout inspired by Apple Mail:

- Left: Classifications list with search and filtering
- Right: Results list with images and metadata

### Performance Trade-offs

When "Has Images" is enabled, the app may return fewer than 80 results due to filtering out copyrighted works. Rather than making dozens of additional API calls (which would take 5+ minutes), the app shows available results quickly. This prioritizes user experience over hitting an exact result count.

## Known Limitations

- The Met API's rate limiting is stated to be 80 requests per second. While that's true it seems that after each burst of 80 requests there's a required wait period of 60 seconds or so.
- While the API has a `hasImages` parameter it delivers unreliable results. Many records returned do not, in fact, have an image. Likely since they are not in the public domain.
- Therefore, Classification counts are approximate when filtering by images

## Future Improvements

- Add caching for fetched object data
- Implement result pagination beyond first 80
- Add detail view with full metadata and multiple images
- Support for additional search parameters (artist, date range, department)

## About

**Met Collection API**: https://metmuseum.github.io/  
**Met Open Access**: https://www.metmuseum.org/about-the-met/policies-and-documents/open-access
