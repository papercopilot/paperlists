# Paper Search Tool

A Streamlit-based tool for efficiently searching and analyzing conference papers locally. 
## Why This Tool?
- Fast local searching and filtering across multiple fields
- Support for directory and multi-conference search
- Status-based filtering to exclude withdrawn/rejected papers
- User-friendly web interface and command-line support
- Results download in JSON format with source tracking

This tool reduces server load, enables offline analysis, and allows for custom processing and cross-conference comparisons.

## Setup

1. Clone the repo and navigate to the `tools` directory
```bash
git clone https://github.com/hhh2210/paperlists.git
cd paperlists/tools
```
2. Install dependencies: `pip install -r requirements.txt`

## Usage

### Web Interface

1. Run `streamlit run app.py`
2. Access the web UI at `http://localhost:8501`
3. Enter search criteria, select search mode, and analyze results

### Command Line

```bash
python extract.py [keyword] [-i INPUT_PATH] [-o OUTPUT_FILE] [-f FIELDS...]
```

- `keyword`: Search keyword (required)
- `-i, --input_path`: Input JSON file or directory (default: iclr2025.json)
- `-o, --output_file`: Output JSON file (optional)
- `-f, --fields`: Fields to search (default: keywords title primary_area topic)

Example:
```bash
python extract.py retrieval -i iclr -o results.json -f title keywords
``` 