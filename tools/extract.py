"""
Core functionality for paper filtering and analysis.
This module provides functions for loading, filtering, and analyzing academic paper data.
"""

import json
import argparse
import os
import glob
import logging
from typing import List, Dict, Tuple, Optional, Any, Callable

# Constants
SEARCH_MODE_AND = "AND"
SEARCH_MODE_OR = "OR"
EXCLUDED_STATUSES = ('Withdraw', 'Reject')
DEFAULT_FIELDS = ["keywords", "title", "primary_area", "topic"]

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path configuration
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(TOOLS_DIR, ".."))
DATA_DIR = PROJECT_ROOT


def _parse_keywords(keyword_str: str) -> List[str]:
    """
    Parse keyword string into a list of keywords.
    
    Args:
        keyword_str (str): Comma or space separated keywords
        
    Returns:
        List[str]: List of parsed keywords
    """
    return [k.strip().lower() for k in keyword_str.replace(',', ' ').split() if k.strip()]


def _match_keyword_in_fields(item: Dict[str, Any], keyword: str, fields: List[str]) -> bool:
    """
    Check if any field in the item contains the keyword.
    
    Args:
        item (Dict[str, Any]): Data item to check
        keyword (str): Keyword to search for
        fields (List[str]): Fields to search in
        
    Returns:
        bool: True if any field contains the keyword
    """
    return any(keyword in str(item.get(field, '')).lower() for field in fields)


def _filter_by_search_mode(
    items: List[Dict[str, Any]], 
    keywords: List[str], 
    fields: List[str], 
    search_mode: str
) -> List[Dict[str, Any]]:
    """
    Filter items based on search mode.
    
    Args:
        items (List[Dict[str, Any]]): List of items to filter
        keywords (List[str]): List of keywords
        fields (List[str]): Fields to search in
        search_mode (str): Search mode (AND/OR)
        
    Returns:
        List[Dict[str, Any]]: Filtered items
    """
    if search_mode.upper() == SEARCH_MODE_AND:
        return [
            item for item in items
            if all(_match_keyword_in_fields(item, kw, fields) for kw in keywords)
        ]
    else:  # Default to OR mode
        return [
            item for item in items
            if any(_match_keyword_in_fields(item, kw, fields) for kw in keywords)
        ]


def load_data(input_file: str) -> Optional[List[Dict[str, Any]]]:
    """
    Load JSON data using unified configuration path.

    Args:
        input_file (str): Path to the JSON file relative to DATA_DIR.

    Returns:
        Optional[List[Dict[str, Any]]]: List of paper data if successful, None otherwise.
    """
    # Build absolute path
    absolute_path = os.path.join(DATA_DIR, input_file)
    
    # Handle case where input_file is a list
    if isinstance(input_file, list):
        absolute_path = os.path.join(DATA_DIR, *input_file)
    
    # Try to load the file
    try:
        with open(absolute_path, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {absolute_path}")
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format in file: {absolute_path}")
    return None


def filter_data(
    data: List[Dict[str, Any]], 
    keyword: str, 
    fields_to_search: List[str],
    search_mode: str = SEARCH_MODE_OR,
    include_rejected: bool = False  # Add new parameter
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Filter data based on keywords and fields.

    Args:
        data (List[Dict[str, Any]]): List of paper data.
        keyword (str): Keywords to search for, can be comma or space separated.
        fields_to_search (List[str]): List of fields to search in.
        search_mode (str): "AND" requires all keywords to match, "OR" requires any keyword to match.
        include_rejected (bool): Whether to include rejected/withdrawn papers.

    Returns:
        Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]: 
            A tuple containing two lists:
            - First list: Data filtered by status
            - Second list: Data filtered by both status and keywords
    """
    # First filter out entries with excluded statuses if not including rejected papers
    if include_rejected:
        status_filtered = data  # No status filtering
    else:
        status_filtered = [
            item for item in data
            if item.get('status') not in EXCLUDED_STATUSES
        ]

    # Parse keywords
    keywords = _parse_keywords(keyword)
    
    if not keywords:
        return status_filtered, []

    # Filter by keywords according to search mode
    filtered = _filter_by_search_mode(status_filtered, keywords, fields_to_search, search_mode)
    
    return status_filtered, filtered


def count_results(
    data: List[Dict[str, Any]], 
    status_filtered: List[Dict[str, Any]], 
    filtered: List[Dict[str, Any]], 
    keyword: str, 
    fields: List[str],
    search_mode: str = SEARCH_MODE_OR
) -> Dict[str, int]:
    """
    Calculate statistics for various filtering results.

    Args:
        data (List[Dict[str, Any]]): Original paper data list.
        status_filtered (List[Dict[str, Any]]): Status-filtered data list.
        filtered (List[Dict[str, Any]]): Keyword-filtered data list.
        keyword (str): Search keywords.
        fields (List[str]): List of fields searched.
        search_mode (str): "AND" requires all keywords to match, "OR" requires any keyword to match.

    Returns:
        Dict[str, int]: Dictionary containing various statistics.
    """
    # Parse keywords
    keywords = _parse_keywords(keyword)
    
    if not keywords:
        return {
            "retrieval_before_status_filter": 0,
            "status_filtered_count": len(status_filtered),
            "retrieval_filtered_count": 0,
        }

    # Calculate papers containing keyword before status filtering
    retrieval_before_filter = _filter_by_search_mode(data, keywords, fields, search_mode)

    return {
        "retrieval_before_status_filter": len(retrieval_before_filter),
        "status_filtered_count": len(status_filtered),
        "retrieval_filtered_count": len(filtered),
    }


def main():
    """
    Main function that handles command line arguments and orchestrates the data processing.
    """
    parser = argparse.ArgumentParser(
        description="Extract paper information from JSON files based on keyword."
    )
    parser.add_argument(
        "keyword",
        help="Keyword(s) to search for. Multiple keywords can be comma or space separated."
    )
    parser.add_argument(
        "-i", "--input_path",
        default="iclr/iclr2025.json",
        help="Input path relative to paperlists directory (e.g. 'iclr/iclr2025.json')"
    )
    parser.add_argument(
        "-o", "--output_file",
        help="Output JSON filename"
    )
    parser.add_argument(
        "-f", "--fields",
        nargs="+",
        default=DEFAULT_FIELDS,
        help=f"Fields to search in (default: {' '.join(DEFAULT_FIELDS)})"
    )
    parser.add_argument(
        "-m", "--search_mode",
        choices=[SEARCH_MODE_AND, SEARCH_MODE_OR],
        default=SEARCH_MODE_OR,
        help=f"{SEARCH_MODE_AND} requires all keywords to match, {SEARCH_MODE_OR} requires any keyword to match"
    )
    parser.add_argument(
        "--include_rejected",
        action="store_true",
        help="Include rejected and withdrawn papers in the results"
    )

    args = parser.parse_args()
    
    # Generate output filename if not provided
    if not args.output_file:
        base_name = os.path.basename(args.input_path.rstrip(os.sep))
        base_filename = os.path.splitext(base_name)[0]
        args.output_file = f"{base_filename}-{args.keyword}.json"

    # Load and process data
    data = load_data(args.input_path)
    if data is None:
        return

    status_filtered, filtered = filter_data(data, args.keyword, args.fields, args.search_mode, args.include_rejected)
    counts = count_results(data, status_filtered, filtered, args.keyword, args.fields, args.search_mode)

    # Add source information to filtered papers
    for paper in filtered:
        if 'source' not in paper:
            paper['source'] = os.path.basename(args.input_path)

    # Prepare output data
    output_data = {
        "retrieval_before_status_filter": counts["retrieval_before_status_filter"],
        "status_filtered_count": counts["status_filtered_count"],
        "retrieval_filtered_count": counts["retrieval_filtered_count"],
        "filtered_papers": filtered
    }

    # Write results to file
    with open(args.output_file, 'w', encoding='utf-8') as fw:
        json.dump(output_data, fw, ensure_ascii=False, indent=2)
    logger.info(f"Filtered data has been written to: {args.output_file}")


if __name__ == "__main__":
    main()
