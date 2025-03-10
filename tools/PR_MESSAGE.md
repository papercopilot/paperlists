Thanks for your great open source work on the papercopilot project! 

I recently used the keyword search feature on the papercopilot website and noticed that it places a significant burden on the server, resulting in slow response times, unresponsiveness, and lag. Out of concern for these performance issues and a desire to improve the user experience, I have created this pull request.

## PR Title
Add Enhanced Local Paper Search Tool with Improved UX and Multi-keyword Support

## PR Description
This PR adds an improved local paper search tool that provides a more efficient way to search and filter conference papers. The tool includes both a web interface (using Streamlit) and command-line functionality, with enhanced user experience focused on typical search behaviors.

### Key Features
- Fast local paper searching with improved keyword handling
- Multiple keyword search with AND/OR operators
- Default filtering of rejected/withdrawn papers (aligned with user expectations)
- Advanced filter options for including rejected papers when needed
- More intuitive metrics display in the UI
- Multi-field search support
- Results download in JSON format
- User-friendly web interface with better feedback
- Command-line support with additional options
- Directory and multi-conference search capabilities

### Changes
- Added `app.py` for Streamlit interface
- Updated `extract.py` with enhanced keyword parsing and filtering options
- Removed explicit dependence on config.py by inlining configuration
- Improved code organization with helper functions for better maintainability
- Added caching for performance optimization
- Updated UI to provide better guidance and feedback to users

This tool helps reduce server load by allowing users to perform searches locally while maintaining all the functionality of the web version. It also introduces new features like multi-keyword search modes and smarter default filtering that better aligns with user expectations.

The changes have been thoroughly tested and adhere to the existing coding style and best practices. I believe these enhancements will greatly benefit users and contribute to the overall success of the papercopilot project.

Please let me know if you have any questions or feedback regarding this PR. I'm open to discussion and further improvements.

Thank you for considering this contribution!