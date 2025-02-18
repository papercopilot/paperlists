# Local Paper Search Tool

A local Streamlit-based search tool for efficiently filtering and analyzing conference papers. This tool provides a user-friendly interface for searching through paper submissions using keywords across different fields.

## Features

- Fast local paper searching and filtering
- Multiple field search support (keywords, title, primary area, topic)
- Status-based filtering (automatically excludes Withdrawn/Rejected papers)
- Results download in JSON format
- User-friendly web interface
- Support for directory and multi-conference search
- Source tracking for search results

## Installation

1. Clone the repository:
```bash
git clone https://github.com/papercopilot/paperlists.git
cd paperlists/tools
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit application:

For example, to extract papers related to "retrieval" from iclr2025.json:
```bash
python extract.py retrieval -i iclr/iclr2025.json -o retrieval_results.json -f keywords title primary_area topic
```

2. Access the web interface through your browser (typically at `http://localhost:8501`)

3. Use the interface to:
   - Enter search keywords
   - Select fields to search in
   - Choose search mode (Single File/Conference Directory/Multiple Conferences)
   - Filter and analyze papers
   - Download results

## Command Line Usage

The tool also supports command-line operation through `extract.py`:

```bash
python extract.py [keyword] [-i INPUT_PATH] [-o OUTPUT_FILE] [-f FIELDS...]
```

Arguments:
- `keyword`: Search keyword (required)
- `-i, --input_path`: Input JSON file or directory path (default: iclr2025.json)
- `-o, --output_file`: Output JSON file (optional)
- `-f, --fields`: Fields to search in (default: keywords title primary_area topic)

Examples:
```bash
# Search in a single file
python extract.py retrieval -i iclr/iclr2025.json -o retrieval_results.json

# Search in a conference directory
python extract.py retrieval -i iclr -o retrieval_results.json

# Search with custom fields
python extract.py retrieval -i iclr -f title keywords
```

## Why This Tool?

This local search tool was created to:
1. Reduce server load on the main website
2. Provide faster search capabilities
3. Enable offline paper filtering and analysis
4. Support custom JSON file processing
5. Allow for cross-conference paper analysis

## Contributing

Feel free to submit issues and enhancement requests! 