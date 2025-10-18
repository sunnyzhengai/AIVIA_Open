# Changelog

All notable changes to AIVIA will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure with Sales CRM demo
- Synthetic CSV data for customers, orders, and related entities
- Jupyter notebook demonstrating graph construction and querying
- Basic Neo4j integration for graph database operations
- Apache-2.0 license for open source distribution
- Comprehensive documentation including README, contributing guidelines, and code of conduct
- Security policy and vulnerability reporting process
- Development roadmap with planned milestones

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [0.1.0] - 2024-01-XX

### Added
- **Core Infrastructure**
  - Basic project structure with `src/`, `docs/`, `examples/`, and `notebooks/` directories
  - `requirements.txt` with minimal dependencies (neo4j, pandas, faiss-cpu, sentence-transformers)
  - `.gitignore` for Python/Jupyter artifacts
  - Apache-2.0 license

- **Documentation**
  - `README.md` with project overview and quick start guide
  - `CONTRIBUTING.md` with contribution guidelines and commit message standards
  - `CODE_OF_CONDUCT.md` with Contributor Covenant
  - `SECURITY.md` with vulnerability reporting process
  - `ROADMAP.md` with development milestones
  - `CHANGELOG.md` for tracking changes

- **Examples & Demos**
  - Sales CRM demo with synthetic data:
    - `accounts.csv` - Customer account information
    - `contacts.csv` - Contact details and relationships
    - `deals.csv` - Sales opportunities and pipeline
    - `activities.csv` - Customer interactions and touchpoints
    - `campaigns.csv` - Marketing campaign data
    - `touches.csv` - Customer touchpoint history
    - `users.csv` - Sales team member information
  - `demo_sales_crm.ipynb` - End-to-end Jupyter notebook demonstration
  - Sales CRM graph diagram (`docs/diagrams/sales_crm_graph.png`)

- **Graph Database Integration**
  - Neo4j connection and session management
  - CSV data loading into graph structure
  - Basic Cypher query examples
  - Graph visualization preparation

### Technical Details
- **Dependencies**: neo4j, pandas, faiss-cpu, sentence-transformers, jupyter
- **Database**: Neo4j (local or Aura Free)
- **Data Format**: CSV files with synthetic business data
- **Notebook**: Jupyter with Python 3.9+ support

### Known Limitations
- No natural language to Cypher conversion yet
- Limited to basic graph construction and manual querying
- Synthetic data only (no real-world data integration)
- No query optimization or performance tuning

---

## Version History

- **v0.1.0**: Initial release with Sales CRM demo and basic graph operations
- **v0.2.0** (Planned): Natural language to Cypher conversion
- **v0.3.0** (Planned): Visualization and user experience improvements
- **v0.4.0** (Planned): Pip package and CLI tool
- **v0.5.0** (Planned): Advanced features and multi-schema support
- **v1.0.0** (Planned): Production-ready release
