Thanks for your great open source work on the papercopilot project! 

I recently used the keyword search feature on the papercopilot website and noticed that it places a significant burden on the server, resulting in slow response times, unresponsiveness, and lag. Out of concern for these performance issues and a desire to improve the user experience, I have created this pull request.

## PR Title
Add Local Paper Search Tool with Streamlit Interface

## PR Description
This PR adds a local paper search tool that provides a more efficient way to search and filter conference papers. The tool includes both a web interface (using Streamlit) and command-line functionality.

### Key Features
- Fast local paper searching and filtering
- Multiple field search support
- Status-based filtering
- Results download in JSON format
- User-friendly web interface
- Command-line support
- Directory and multi-conference search capabilities
- Source tracking for search results

### Changes
- Added `app.py` for Streamlit interface
- Updated `extract.py` for enhanced functionality and directory support
- Added `config.py` for configuration management
- Updated `requirements.txt`
- Updated `README.md` with new features and usage instructions
- Updated `.gitignore`

This tool helps reduce server load by allowing users to perform searches locally while maintaining all the functionality of the web version. It also introduces new features like directory search and multi-conference analysis.

The changes have been thoroughly tested and adhere to the existing coding style and best practices. I believe these enhancements will greatly benefit users and contribute to the overall success of the papercopilot project.

Please let me know if you have any questions or feedback regarding this PR. I'm open to discussion and further improvements.

Thank you for considering this contribution! 