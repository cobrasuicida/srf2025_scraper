# SRF2025 Conference Data Scraper and Explorer

**Author: Ming Liu (刘铭)**

## Overview

This project extracts conference contribution data from the SRF2025 conference PDF and creates an interactive web-based data explorer. The scraper processes the complete contributions.pdf file (357 pages) and extracts 278 conference papers with full metadata including titles, abstracts, authors, presenters, dates, and session information.

## File Description

- `srf2025_pdf_extractor.py` - Main PDF processing script
- `srf2025_data_explorer.html` - Interactive web data explorer
- `srf2025_data.js` - External JavaScript data file (301KB)
- `index.html` - Project homepage with navigation
- `requirements.txt` - Python dependencies
- `README.md` - This documentation

## Requirements

- Python 3.7+
- PyPDF2 library
- Modern web browser with JavaScript enabled

## Installation

1. Ensure Python 3.7 or higher is installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Extract Data from PDF
```bash
python srf2025_pdf_extractor.py
```

### 2. View Results
Open `index.html` in your web browser to access:
- Project homepage with navigation
- Interactive data explorer with multiple filters

## Features

### Data Extraction
- Complete PDF text extraction (pages 2-357)
- 278 conference contributions processed
- Author and presenter information
- Session and track classifications
- Date/time information
- Abstract content
- Contribution codes and types

### Interactive Web Explorer
- **Search**: Full-text search across titles, codes, and abstracts
- **Filters**:
  - Session filter (16 different sessions)
  - Type filter (Oral, Poster, Student presentations)
  - Author filter (278 unique authors)
  - Presenter filter (278 unique presenters)
  - Date filter (conference dates)

### Modern UI Design
- Gradient backgrounds with particle animations
- Responsive design for mobile devices
- Smooth hover effects and transitions
- Card-based layout with expandable abstracts
- Real-time filter statistics

## Output Files

```
SRF2025_Data/
├── SRF2025_All_Contributions.csv    # Complete CSV dataset
├── SRF2025_Complete_Index.json      # JSON data index
└── SRF2025_Extraction_Report.txt    # Processing statistics
```

## Web Interface Features

### Data Explorer (`srf2025_data_explorer.html`)
- **Real-time Search**: Instant filtering as you type
- **Multiple Filters**: Combine any number of filters
- **Statistics Display**: Shows filtered vs total results
- **Expandable Abstracts**: Click "Read more" for full content
- **Responsive Cards**: Beautiful card layout with session tags
- **Clear Filters**: One-click reset functionality

### Homepage (`index.html`)
- Project overview and navigation
- Author attribution
- Links to data explorer and GitHub
- Modern gradient design

## Technical Details

### Data Structure
```javascript
{
  "scrape_info": {
    "extraction_time": "2025-09-29 20:29:00",
    "total_contributions": 278,
    "sessions_processed": 16
  },
  "sessions": [
    {
      "session_info": {"id": "MOA", "name": "Monday Opening and Awards"},
      "papers": [
        {
          "contribution_id": "2",
          "contribution_code": "MOA01",
          "type": "Invited Oral Presentation",
          "title": "5 year operation of RIKEN super-conducting linac",
          "date_time": "Monday, September 22, 2025 8:30 AM",
          "abstract": "...",
          "footnotes": "Author: SAKAMOTO, Naruhiko...",
          "session": "Monday Opening and Awards"
        }
      ]
    }
  ]
}
```

### Filter Categories
1. **Session Filter**: 16 sessions (MOA, MOP, TUA, etc.)
2. **Type Filter**: Oral, Poster, Student presentations
3. **Author Filter**: All contributing authors
4. **Presenter Filter**: All presenters
5. **Date Filter**: Conference dates

## Browser Compatibility
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Performance
- Data file: 301KB (external loading)
- Initial load: <2 seconds
- Filter response: <100ms
- Memory usage: Minimal (client-side processing)

## Configuration

The web explorer is fully client-side and requires no server configuration. Simply open the HTML files in any modern web browser.

## Important Notes

1. **Data Source**: Original `contributions.pdf` must be present for extraction
2. **File Size**: The JavaScript data file is 301KB - ensure sufficient bandwidth
3. **Browser Security**: Some browsers may block local file access for JavaScript
4. **Mobile Friendly**: Responsive design works on all screen sizes

## FAQ

### Q: How do I run the PDF extraction?
A: Place `contributions.pdf` in the same directory and run `python srf2025_pdf_extractor.py`

### Q: The web explorer doesn't load data?
A: Ensure `srf2025_data.js` is in the same directory as the HTML files

### Q: Can I host this on a web server?
A: Yes, all files are static and can be served from any web server

### Q: How to modify the filters?
A: Edit the JavaScript in `srf2025_data_explorer.html` to add custom filters

### Q: Data appears corrupted?
A: Re-run the PDF extraction script to regenerate clean data files

## Technical Support

If you encounter issues, please check:
1. Verify Python 3.7+ is installed
2. Check all dependencies are installed
3. Ensure `contributions.pdf` is accessible
4. Open browser console for JavaScript errors
5. Check file permissions for data access

## License

This project is for academic and research purposes. Please respect copyright and conference data usage policies.

## Version History

### v1.0 (Current)
- Complete SRF2025 data extraction (278 contributions)
- Interactive web explorer with 5 filter categories
- Modern UI with animations and responsive design
- External data file for performance
- Comprehensive documentation

## Author

**Ming Liu (刘铭)**
- GitHub: [@iuming](https://github.com/iuming)
- Project: SRF2025 Data Scraper and Explorer

## Acknowledgments

- SRF2025 Conference organizers
- PyPDF2 library developers
- Open source community