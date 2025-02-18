"""
Core functionality for paper filtering and analysis.
This module provides functions for loading, filtering, and analyzing academic paper data.
"""

import json
import argparse
import os
import glob
from typing import List, Dict, Tuple, Optional, Any


def load_data(input_path: str) -> Optional[List[Dict[str, Any]]]:
    """
    Load data from a JSON file or directory.

    Args:
        input_path (str): Path to the input JSON file or directory.

    Returns:
        Optional[List[Dict[str, Any]]]: List containing the data if successful, None otherwise.
    """
    try:
        # Check if input_path is a directory
        if os.path.isdir(input_path):
            # Find all JSON files in the directory
            json_files = glob.glob(os.path.join(input_path, "*.json"))
            if not json_files:
                print(f"Error: No JSON files found in directory '{input_path}'.")
                return None
            
            # Load and combine data from all JSON files
            combined_data = []
            for json_file in json_files:
                with open(json_file, encoding='utf-8') as f:
                    file_data = json.load(f)
                    if isinstance(file_data, list):
                        combined_data.extend(file_data)
                    else:
                        combined_data.append(file_data)
            return combined_data
        else:
            # Load single JSON file
            with open(input_path, encoding='utf-8') as f:
                data = json.load(f)
            return data if isinstance(data, list) else [data]
            
    except FileNotFoundError:
        print(f"Error: Path '{input_path}' does not exist.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{input_path}'.")
        return None
    except Exception as e:
        print(f"Error: Failed to load data - {str(e)}")
        return None


def filter_data(
    data: List[Dict[str, Any]], 
    keyword: str, 
    fields_to_search: List[str]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Filter data based on keyword and fields.

    Args:
        data (List[Dict[str, Any]]): List of paper data.
        keyword (str): Keyword to search for.
        fields_to_search (List[str]): List of fields to search in.

    Returns:
        Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]: 
            A tuple containing two lists:
            - First list: Data filtered by status
            - Second list: Data filtered by both status and keyword
    """
    # First filter out entries with 'Withdraw' or 'Reject' status
    status_filtered = [
        item for item in data
        if item.get('status') not in ('Withdraw', 'Reject')
    ]

    # Then filter entries containing the keyword in specified fields
    filtered = [
        item for item in status_filtered
        if any(
            keyword.lower() in str(item.get(field, '')).lower()
            for field in fields_to_search
        )
    ]
    
    return status_filtered, filtered


def count_results(
    data: List[Dict[str, Any]], 
    status_filtered: List[Dict[str, Any]], 
    filtered: List[Dict[str, Any]], 
    keyword: str, 
    fields: List[str]
) -> Dict[str, int]:
    """
    Calculate statistics for various filtering results.

    Args:
        data (List[Dict[str, Any]]): Original paper data list.
        status_filtered (List[Dict[str, Any]]): Status-filtered data list.
        filtered (List[Dict[str, Any]]): Keyword-filtered data list.
        keyword (str): Search keyword.
        fields (List[str]): List of fields searched.

    Returns:
        Dict[str, int]: Dictionary containing various statistics.
    """
    # Calculate papers containing keyword before status filtering
    retrieval_before_filter = [
        item for item in data
        if any(
            keyword.lower() in str(item.get(field, '')).lower()
            for field in fields
        )
    ]

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
        help="Keyword to search for"
    )
    parser.add_argument(
        "-i", "--input_path",
        default="iclr2025.json",
        help="Input JSON file or directory path (default: iclr2025.json)"
    )
    parser.add_argument(
        "-o", "--output_file",
        help="Output JSON filename"
    )
    parser.add_argument(
        "-f", "--fields",
        nargs="+",
        default=["keywords", "title", "primary_area", "topic"],
        help="Fields to search in (default: keywords title primary_area topic)"
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

    status_filtered, filtered = filter_data(data, args.keyword, args.fields)
    counts = count_results(data, status_filtered, filtered, args.keyword, args.fields)

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
    print(f"Filtered data has been written to: {args.output_file}")


if __name__ == "__main__":
    main()
