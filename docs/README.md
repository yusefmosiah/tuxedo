# Architecture Documentation Index

This directory contains comprehensive documentation for Tuxedo's architecture and migrations.

## Core Documentation

### [LocalWorkspace Migration Guide](./LOCALWORKSPACE_MIGRATION.md)

Complete guide to the DockerWorkspace → LocalWorkspace migration, including:

- Architecture changes and motivation
- Implementation details
- Multi-environment deployment (dev, Render, Phala)
- API reference and troubleshooting
- **Status:** ✅ Phase 1 Complete (Nov 26, 2025)

### [Phala Deployment Checklist](./PHALA_DEPLOYMENT_CHECKLIST.md)

Step-by-step deployment guide for Phala Network CVM:

- Prerequisites and account setup
- Docker image preparation
- CVM creation and configuration
- Security best practices
- **Status:** 📝 Ready for Phase 3

### [Economic Model](./ECONOMIC_MODEL.md)

Documentation of the Choir "Thought Bank" economic system:

- Three-currency model (USDC, CHIP, governance)
- Citation economics
- Treasury mechanics
- **Status:** 📝 Active design

### [Choir Whitepaper](./CHOIR_WHITEPAPER.md)

Original vision document for the Choir protocol:

- Hypothesis-driven research
- Multi-model orchestration
- Anonymous publishing
- **Status:** 📚 Reference

## Migration Timeline

### ✅ Phase 1: Stabilization (Week 1) - COMPLETE

- Replaced DockerWorkspace with LocalWorkspace
- Created PersistentPathManager utility
- Updated Dockerfile for Phala compatibility
- **Deliverable:** [LocalWorkspace Migration Guide](./LOCALWORKSPACE_MIGRATION.md)

### 🔄 Phase 2: Cleanup (Week 2) - IN PROGRESS

- Remove Stellar/DeFindex code
- Update system prompt
- Archive Rust contracts
- **Target Date:** Dec 3, 2025

### 📋 Phase 3: Somnia Integration (Weeks 3-4) - PLANNED

- Build Somnia MCP server
- Deploy to Phala CVM
- Multi-user testing
- **Target Date:** Dec 17, 2025

### 📋 Phase 4: Production (Week 5) - PLANNED

- Performance testing
- Security audit
- Monitoring setup
- **Target Date:** Dec 24, 2025

## Quick Links

### For Developers

- **Getting Started:** [LocalWorkspace Migration](./LOCALWORKSPACE_MIGRATION.md#migration-guide)
- **API Reference:** [LocalWorkspace Migration - API](./LOCALWORKSPACE_MIGRATION.md#api-reference)
- **Testing:** [LocalWorkspace Migration - Testing](./LOCALWORKSPACE_MIGRATION.md#testing--validation)

### For DevOps

- **Local Testing:** [Environment Setup](./ENVIRONMENT_SETUP.md)
- **Render Deployment:** [LocalWorkspace Migration - Render](./LOCALWORKSPACE_MIGRATION.md#scenario-2-rendercom-ephemeral)
- **Phala Deployment:** [Phala Checklist](./PHALA_DEPLOYMENT_CHECKLIST.md)

### For Product

- **Architecture Overview:** [LocalWorkspace Migration - Architecture](./LOCALWORKSPACE_MIGRATION.md#architecture-changes)
- **Economic Model:** [Economic Model](./ECONOMIC_MODEL.md)
- **Vision:** [Choir Whitepaper](./CHOIR_WHITEPAPER.md)

## Recent Changes

### November 26, 2025

- ✅ Completed Phase 1: LocalWorkspace migration
- ✅ Created comprehensive migration documentation
- ✅ Validated PersistentPathManager in dev environment
- 📝 Updated deployment guides for multi-environment support

### November 23, 2025

- 🔧 Fixed Ghostwriter pipeline infinite loop
- 🐛 Resolved Docker Python version mismatch
- 📝 Generated code status report

## Contributing

When adding new documentation:

1. **Create markdown file** in `/docs` directory
2. **Update this README** with link and description
3. **Follow structure:**
   - Executive summary
   - Detailed content
   - Examples and code snippets
   - Troubleshooting section
   - References

4. **Use consistent formatting:**
   - Headers: `##` for major sections
   - Code blocks: Triple backticks with language
   - Links: Relative paths for internal docs
   - Status indicators: ✅ ❌ 🔄 📋 📝 📚

---

**Last Updated:** November 26, 2025
**Maintained By:** Development Team
