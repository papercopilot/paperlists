"""
Streamlit-based web interface for paper searching and filtering.
This module provides a user-friendly interface for searching and analyzing academic papers.
"""

import streamlit as st
import json
import os
import glob
from typing import List, Dict, Any, Optional
import logging
from extract import load_data, filter_data, count_results, SEARCH_MODE_AND, SEARCH_MODE_OR, DEFAULT_FIELDS

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
CONFERENCES = [
    "iclr", "nips", "icml", "cvpr", "iccv", "eccv", "emnlp", "corl", 
    "siggraph", "siggraphasia", "www", "wacv", "aistats", "colm"
]
DATA_SEARCH_MODES = ["Single File", "Conference Directory", "Multiple Conferences"]

# Use Streamlit cache for expensive operations
@st.cache_data
def load_conference_data(conference_name: str) -> Optional[List[Dict[str, Any]]]:
    """
    Load conference data with dynamic year selection.
    
    Args:
        conference_name (str): Name of the conference to load data for
        
    Returns:
        Optional[List[Dict[str, Any]]]: Conference data if successful, None otherwise
    """
    # Base directories to search
    base_dirs = [
        "",  # Current directory
        "../",  # Parent directory
        "paperlists/",  # paperlists subdirectory
        "../paperlists/"  # paperlists in parent directory
    ]
    
    # Find directory containing conference data
    conf_dir = None
    for base in base_dirs:
        possible_dir = os.path.join(base, conference_name)
        if os.path.isdir(possible_dir):
            conf_dir = possible_dir
            break
    
    if not conf_dir:
        st.error(f"Could not find directory for {conference_name}")
        return None
    
    # Find all conference JSON files
    pattern = os.path.join(conf_dir, f"{conference_name}*.json")
    json_files = glob.glob(pattern)
    
    if not json_files:
        st.error(f"No JSON files found for {conference_name}")
        return None
    
    # Sort files and get the latest one
    latest_file = sorted(json_files)[-1]
    
    try:
        with open(latest_file, encoding='utf-8') as f:
            data = json.load(f)
            st.info(f"Loaded data from {os.path.basename(latest_file)}")
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"Error loading {os.path.basename(latest_file)}: {str(e)}")
        return None


def create_search_sidebar() -> Dict[str, Any]:
    """
    Create sidebar for search configuration.
    
    Returns:
        Dict[str, Any]: Dictionary containing search parameters
    """
    with st.sidebar:
        st.header("Search Configuration")
        keyword = st.text_input(
            "Enter keyword(s):", 
            value="retrieval",
            help="Multiple keywords can be separated by commas or spaces (e.g., 'retrieval agent' or 'retrieval,agent')"
        )
        
        search_mode = st.radio(
            "Keywords Search Mode:",
            [SEARCH_MODE_OR, SEARCH_MODE_AND],
            help=f"{SEARCH_MODE_OR}: Find papers with ANY of these keywords. {SEARCH_MODE_AND}: Find papers with ALL of these keywords."
        )
        
        fields_to_search = st.multiselect(
            "Select fields to search:",
            options=DEFAULT_FIELDS,
            default=DEFAULT_FIELDS
        )
        
        # Add advanced filtering options
        st.subheader("Advanced Filters")
        include_rejected = st.checkbox(
            "Include rejected/withdrawn papers", 
            value=False,
            help="By default, only accepted papers are shown. Check this to include rejected or withdrawn papers."
        )

        # Add conference selection
        st.subheader("Conference Selection")
        data_search_mode = st.radio(
            "Data Source:",
            DATA_SEARCH_MODES,
            help="Choose how you want to search for papers"
        )
        
    return {
        "keyword": keyword,
        "search_mode": search_mode,
        "fields_to_search": fields_to_search,
        "include_rejected": include_rejected,  # Add new parameter
        "data_search_mode": data_search_mode
    }


def load_data_source(data_search_mode: str) -> tuple:
    """
    Load data based on selected source mode.
    
    Args:
        data_search_mode (str): Type of data source to load
        
    Returns:
        tuple: (data, source) where data is the loaded data and source is its description
    """
    data = None
    source = ""
    
    if data_search_mode == DATA_SEARCH_MODES[0]:  # Single File
        uploaded_file = st.file_uploader("Upload JSON file:", type=["json"])
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                source = uploaded_file.name
            except json.JSONDecodeError:
                st.error("Invalid JSON file format. Please check the file.")
        else:
            data = load_data("iclr2025.json")
            source = "iclr2025.json"
    
    elif data_search_mode == DATA_SEARCH_MODES[1]:  # Conference Directory
        conference = st.selectbox("Select Conference:", CONFERENCES)
        data = load_conference_data(conference)
        source = conference
    
    else:  # Multiple Conferences
        conferences = st.multiselect("Select Conferences:", CONFERENCES)
        if conferences:
            data = []
            for conf in conferences:
                conf_data = load_conference_data(conf)
                if conf_data:
                    data.extend(conf_data)
            source = "+".join(conferences)
        else:
            st.warning("Please select at least one conference.")
    
    return data, source


def display_search_results(data, source, search_params):
    """
    Filter data and display search results.
    
    Args:
        data: The data to search
        source: Source description of the data
        search_params: Dictionary of search parameters
    """
    keyword = search_params["keyword"]
    search_mode = search_params["search_mode"]
    fields_to_search = search_params["fields_to_search"]
    include_rejected = search_params["include_rejected"]  # Get new parameter
    
    if not data:
        st.error("Unable to load data. Please check the input file or directory.")
        return
        
    if not keyword:
        st.warning("Please enter at least one keyword.")
        return
        
    # Show what keywords are being searched
    keywords_list = [k.strip() for k in keyword.replace(',', ' ').split() if k.strip()]
    if len(keywords_list) > 1:
        if search_mode == SEARCH_MODE_OR:
            st.write(f"Searching for papers containing ANY of these keywords: {', '.join(keywords_list)}")
        else:
            st.write(f"Searching for papers containing ALL of these keywords: {', '.join(keywords_list)}")
    
    # Add filtering condition description
    if not include_rejected:
        st.info("Showing only accepted papers. To include rejected/withdrawn papers, check the advanced filter option.")
    
    with st.spinner('Processing data...'):
        # Filter data
        status_filtered, filtered = filter_data(data, keyword, fields_to_search, search_mode, include_rejected)

        # Calculate statistics
        counts = count_results(data, status_filtered, filtered, keyword, fields_to_search, search_mode)

        # Display results with more intuitive metric names
        st.subheader("Search Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Papers",
                len(data)
            )
        with col2:
            st.metric(
                "Papers After Status Filter" if include_rejected else "Accepted Papers",
                counts['status_filtered_count']
            )
        with col3:
            st.metric(
                "Matching Results",
                counts['retrieval_filtered_count']
            )

        # Display filtered papers
        if filtered:
            st.subheader(f"Found {len(filtered)} Matching Papers")
            
            # Add source information if not present
            for paper in filtered:
                if 'source' not in paper:
                    paper['source'] = source

            # Convert to DataFrame for better display
            st.dataframe(filtered)

            # Download button
            output_data = {
                "total_papers": len(data),
                "papers_after_status_filter": counts['status_filtered_count'],
                "matching_results": counts['retrieval_filtered_count'],
                "filtered_papers": filtered
            }
            
            st.download_button(
                label="Download Results (JSON)",
                data=json.dumps(output_data, ensure_ascii=False, indent=2),
                file_name=f"filtered_results-{keyword}-{source}.json",
                mime="application/json"
            )
        else:
            st.info(f"No papers found containing the keyword '{keyword}'.")


def main():
    """Main function that sets up the Streamlit interface and handles user interactions."""
    st.title("Paper Search Tool")

    # Get search parameters from sidebar
    search_params = create_search_sidebar()

    # Load data from selected source
    data, source = load_data_source(search_params["data_search_mode"])

    # Search button and results
    if st.button("Search Papers"):
        display_search_results(data, source, search_params)


if __name__ == "__main__":
    main()