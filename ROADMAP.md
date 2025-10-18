# AIVIA Roadmap

This document outlines the planned development milestones for AIVIA.

## Current Version: v0.1.0 (Unreleased)

### Core Features
- [x] Basic Neo4j graph construction from CSV data
- [x] Sales CRM demo with synthetic data
- [x] Jupyter notebook examples
- [x] Minimal requirements and documentation

## Upcoming Milestones

### v0.2.0 - Natural Language to Cypher
- [ ] **NL Query Parser**: Convert natural language questions to Cypher queries
- [ ] **Schema Indexing**: Build semantic indexes for graph schema matching
- [ ] **Value Indexing**: Create embeddings for property values
- [ ] **Query Orchestration**: End-to-end pipeline from question to results
- [ ] **Demo Notebook**: Complete NL→Cypher→Results workflow

### v0.3.0 - Visualization & UX
- [ ] **Graph Visualization**: Interactive Neo4j graph display in notebooks
- [ ] **Query Explanation**: Show reasoning behind generated Cypher
- [ ] **Result Formatting**: Pretty-print query results with context
- [ ] **Error Handling**: User-friendly error messages and suggestions

### v0.4.0 - Package & Distribution
- [ ] **Pip Package**: Installable via `pip install aivia`
- [ ] **CLI Tool**: Command-line interface for quick queries
- [ ] **Configuration**: YAML/JSON config for different graph schemas
- [ ] **Documentation**: Comprehensive API docs and tutorials

### v0.5.0 - Advanced Features
- [ ] **Multi-Schema Support**: Handle different graph schemas (healthcare, finance, etc.)
- [ ] **Query Optimization**: Suggest better Cypher queries
- [ ] **Caching**: Cache embeddings and query results
- [ ] **Batch Processing**: Handle multiple queries efficiently

### v1.0.0 - Production Ready
- [ ] **Performance Optimization**: Handle large graphs efficiently
- [ ] **Enterprise Features**: Authentication, logging, monitoring
- [ ] **Integration**: REST API, webhooks, cloud deployment
- [ ] **Testing**: Comprehensive test suite and CI/CD

## Long-term Vision

### Beyond v1.0
- **Multi-Database Support**: Extend beyond Neo4j to other graph databases
- **AI Integration**: Leverage LLMs for better query understanding
- **Real-time Updates**: Handle streaming data and live graph updates
- **Community Ecosystem**: Plugin system for custom indexers and matchers

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Feedback

Have ideas for features or improvements? Open an issue or start a discussion!

---

*This roadmap is subject to change based on community feedback and development priorities.*
