# PropBot  

## Overview  
PropBot is a tool for efficiently searching and analyzing grant and contract opportunities. It aggregates funding data from multiple sources, processes it into structured formats, and enables fast retrieval. While the system is designed to support **FAISS-based semantic search**, this has not yet been implemented. The current implementation relies on keyword-based search.  

## System Components  

### Backend  
- **FastAPI service** for handling search queries and serving grant data.  
- **Planned FAISS vector index** for semantic search on funding opportunities (not yet implemented).  
- **Data pipeline** for ingesting and processing structured and unstructured funding data.  

### Frontend  
- **React-based UI** for grant search and exploration.  
- **Filtering and sorting options** based on funding amount, agency, and deadline.  
- **Future support** for interactive dashboards and user accounts.  

### Data Processing  
- **Grants.gov and SAM.gov ingestion** via API and web scraping.  
- **XML and JSON parsing** for structured data extraction.  
- **Planned FAISS indexing** for efficient similarity search (not yet implemented).  

## Roadmap  

### Data Expansion  
- Integrate additional funding sources, including private and international grants.  
- Improve real-time updates and API integration.  

### Search and Matching  
- Optimize FAISS indexing for improved query performance (**not yet implemented**).  
- Implement entity recognition to match grants to specific research domains.  

### Automation  
- Implement scheduled data refresh and background processing.  
- Add webhook and email notifications for new funding opportunities.  

### Proposal Assistance  
- Develop AI-assisted grant writing and template generation.  
- Provide guidance based on historical successful proposals.  

### API and Integrations  
- Expose a REST API for third-party applications to query the funding database.  
- Build integrations with research management and CRM tools.  

## Contribution  
- The project is open to contributions in data processing, search optimization, and UI development.  
- The planned FAISS-based search functionality has **not yet been implemented**, and contributions toward it are welcome.  

## License  
MIT License (or applicable license for your project).  
