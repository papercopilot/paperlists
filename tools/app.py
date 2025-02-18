"""
Streamlit-based web interface for paper searching and filtering.
This module provides a user-friendly interface for searching and analyzing academic papers.
"""

import streamlit as st
import json
import os
from extract import load_data, filter_data, count_results

def load_conference_data(conference_name):
    """Load conference data (with automatic path handling)"""
    possible_paths = [
        f"paperlists/{conference_name}/{conference_name}2025.json",
        f"../paperlists/{conference_name}/{conference_name}2025.json",
        f"{conference_name}/{conference_name}2025.json"
    ]
    
    for path in possible_paths:
        try:
            with open(path, encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            continue
    
    st.error(f"Could not find data file for {conference_name}")
    return None

def main():
    """Main function that sets up the Streamlit interface and handles user interactions."""
    st.title("Paper Search Tool")

    # Sidebar for search configuration
    with st.sidebar:
        st.header("Search Configuration")
        keyword = st.text_input("Enter keyword:", value="retrieval")
        
        fields_to_search = st.multiselect(
            "Select fields to search:",
            options=["keywords", "title", "primary_area", "topic"],
            default=["keywords", "title", "primary_area", "topic"]
        )

        # Add conference selection
        st.subheader("Conference Selection")
        search_mode = st.radio(
            "Search Mode:",
            ["Single File", "Conference Directory", "Multiple Conferences"],
            help="Choose how you want to search for papers"
        )

    # Main content area
    if search_mode == "Single File":
        uploaded_file = st.file_uploader("Upload JSON file:", type=["json"])
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                source = uploaded_file.name
            except json.JSONDecodeError:
                st.error("Invalid JSON file format. Please check the file.")
                data = None
        else:
            data = load_data("iclr2025.json")
            source = "iclr2025.json"
    else:
        # Directory selection
        if search_mode == "Conference Directory":
            conference = st.selectbox(
                "Select Conference:",
                ["iclr", "nips", "icml", "cvpr", "iccv", "eccv", "emnlp", "corl", 
                 "siggraph", "siggraphasia", "www", "wacv", "aistats", "colm"]
            )
            data = load_conference_data(conference)
            source = conference
        else:  # Multiple Conferences
            conferences = st.multiselect(
                "Select Conferences:",
                ["iclr", "nips", "icml", "cvpr", "iccv", "eccv", "emnlp", "corl", 
                 "siggraph", "siggraphasia", "www", "wacv", "aistats", "colm"]
            )
            if conferences:
                data = []
                for conf in conferences:
                    conf_data = load_conference_data(conf)
                    if conf_data:
                        data.extend(conf_data)
                source = "+".join(conferences)
            else:
                data = None
                st.warning("Please select at least one conference.")

    # Search button and results
    if st.button("Search Papers"):
        if data is not None:
            if not keyword:
                st.warning("Please enter a keyword.")
            else:
                # Filter data
                status_filtered, filtered = filter_data(data, keyword, fields_to_search)

                # Calculate statistics
                counts = count_results(data, status_filtered, filtered, keyword, fields_to_search)

                # Display results
                st.subheader("Search Statistics")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Papers with keyword",
                        counts['retrieval_before_status_filter']
                    )
                with col2:
                    st.metric(
                        "After status filter",
                        counts['status_filtered_count']
                    )
                with col3:
                    st.metric(
                        "Final results",
                        counts['retrieval_filtered_count']
                    )

                # Display filtered papers
                if filtered:
                    st.subheader("Filtered Papers")
                    
                    # Add source information if not present
                    for paper in filtered:
                        if 'source' not in paper:
                            paper['source'] = source

                    # Convert to DataFrame for better display
                    st.dataframe(filtered)

                    # Download button
                    output_data = {
                        "retrieval_before_status_filter": counts['retrieval_before_status_filter'],
                        "status_filtered_count": counts['status_filtered_count'],
                        "retrieval_filtered_count": counts['retrieval_filtered_count'],
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
        else:
            st.error("Unable to load data. Please check the input file or directory.")

if __name__ == "__main__":
    main() 