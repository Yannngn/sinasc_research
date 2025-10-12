# 📚 SINASC Research Documentation Index

## 📖 Documentation Overview

This directory contains comprehensive documentation for the SINASC Research Dashboard and its ETL data pipeline.

---

## 🎯 Getting Started

### **[QUICKSTART.md](QUICKSTART.md)** ⭐ **START HERE**
- Complete setup instructions for local development
- Database configuration with Docker
- Step-by-step pipeline execution
- Running the dashboard locally

### **[README.md](../README.md)** 📊 **PROJECT OVERVIEW**
- High-level project description
- Key features and metrics
- Quick start commands
- Technology stack

---

## 📋 Reference Documents

### **[PIPELINE_QUICK_REFERENCE.md](PIPELINE_QUICK_REFERENCE.md)** 🔖 **COMMAND CHEAT SHEET**
- Common workflows (copy-paste ready)
- Database status checks
- Performance modes
- Troubleshooting tips
- Decision tree

### **[PIPELINE_ARCHITECTURE_VISUAL.md](PIPELINE_ARCHITECTURE_VISUAL.md)** 🎨 **VISUAL DIAGRAMS**
- Architecture overview
- Data flow diagrams
- Performance timeline charts
- File relationships
- Command flow visualization

---

## 🔬 Technical Deep Dives

### **[DATA_PIPELINE_ANALYSIS.md](DATA_PIPELINE_ANALYSIS.md)** 🔍 **ANALYSIS & STRATEGY**
- Complete pandas `to_sql` usage audit
- Optimization opportunities identified
- Performance impact estimates
- Implementation priorities
- Code examples (before/after)

### **[PIPELINE_IMPROVEMENTS_SUMMARY.md](PIPELINE_IMPROVEMENTS_SUMMARY.md)** 📝 **FEATURE DOCUMENTATION**
- Incremental ingestion implementation
- Auto-optimization details
- SQL promotion implementation
- Migration guide
- Testing procedures
- Command reference

### **[SQL_OPTIMIZATION_IMPLEMENTATION.md](SQL_OPTIMIZATION_IMPLEMENTATION.md)** ⚡ **SQL OPTIMIZATION**
- SQL conversion techniques
- Direct SQL examples
- Performance comparisons
- Integration with staging.py
- Testing procedures

---

## 🗺️ Geographic Analysis & Dashboard

### **[GEOGRAPHIC_PLANNING.md](GEOGRAPHIC_PLANNING.md)** 📍 **PLANNING DOCUMENT**
- Geographic page architecture
- State and municipal level design
- Data requirements
- Implementation phases

### **[GEOGRAPHIC_IMPLEMENTATION.md](GEOGRAPHIC_IMPLEMENTATION.md)** 🏗️ **STATE-LEVEL PAGE**
- State-level analysis implementation
- Choropleth maps with GeoJSON
- Regional comparisons
- Metric calculations

### **[MUNICIPAL_LEVEL_ENHANCEMENT.md](MUNICIPAL_LEVEL_ENHANCEMENT.md)** 🏘️ **MUNICIPAL-LEVEL PAGE** ⭐ **NEW**
- State-filtered municipality loading
- Smart top/bottom N rankings
- Municipal choropleth maps
- Performance optimizations (10x faster)
- Database-level filtering
- User controls and UX

### **[DRY_REFACTORING_SUMMARY.md](DRY_REFACTORING_SUMMARY.md)** ♻️ **CODE REFACTORING** ⭐ **NEW**
- Shared component extraction
- Eliminated code duplication
- Municipal page reduced by 19%
- Reusable formatting, charts, and maps
- Improved maintainability
- Future development guidelines

---

## 📂 Project Structure

```
sinasc_research/
│
├── README.md                    # Main project documentation
├── docs/                        # All documentation (this directory)
│   ├── QUICKSTART.md           # ⭐ Start here for setup
│   ├── ARCHITECTURE.md         # System architecture
│   ├── DEPLOYMENT_GUIDE.md     # Deployment instructions
│   └── ...
│
├── dashboard/                   # Dashboard application
│   ├── app.py                  # Main application entry point
│   ├── pages/                  # Dashboard pages (home, annual, geographic)
│   ├── components/             # Reusable UI components (cards, charts)
│   ├── config/                 # Configuration and constants
│   └── data/                   # Data pipeline and loading
│       ├── staging.py          # Ingest raw data from APIs
│       ├── optimize.py         # Optimize data types
│       ├── promote.py          # Copy to production database
│       ├── loader.py           # Dashboard data loading
│       ├── database.py         # Database connections
│       ├── pandas/             # Pandas-based fallback scripts
│       └── pipeline/           # SQL-based pipeline (5 steps)
│           ├── README.md       # Pipeline documentation
│           ├── run_all.py      # Run complete pipeline
│           ├── step_01_select.py
│           ├── step_02_create.py
│           ├── step_03_bin.py
│           ├── step_04_engineer.py
│           └── step_05_aggregate.py
│
├── deployment/                  # Deployment configuration
│   ├── Dockerfile
│   └── render.yaml
│
└── docker-compose.yml           # Local database setup
```

---

## 🎯 Reading Guide by Role

### For New Users (Getting Started)
1. **[../README.md](../README.md)** - Project overview
2. **[QUICKSTART.md](QUICKSTART.md)** - Setup and installation
3. **[dashboard/data/pipeline/README.md](../dashboard/data/pipeline/README.md)** - Pipeline architecture

### For Data Engineers (Running the Pipeline)
1. **[dashboard/data/pipeline/README.md](../dashboard/data/pipeline/README.md)** - Pipeline architecture and execution
2. **[QUICKSTART.md](QUICKSTART.md)** - Setup and pipeline commands
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Database design

### For Developers (Contributing Code)
1. **[STRUCTURE.md](STRUCTURE.md)** - Project organization
2. **[CODING_STANDARDS.md](CODING_STANDARDS.md)** - Code guidelines
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design
4. **[DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)** - UI guidelines

### For DevOps (Deploying the Application)
1. **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Deployment steps
2. **[PRODUCTION_DATA_GRANULARITY.md](PRODUCTION_DATA_GRANULARITY.md)** - Production optimization
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Infrastructure design

---

## 🚀 Common Workflows

### "I want to set up the project locally"
1. Read **[QUICKSTART.md](QUICKSTART.md)**
2. Follow the setup steps
3. Run `docker-compose up -d` and `python -m dashboard.data.run_all`

### "I want to add new SINASC data"
1. Run `python dashboard/data/staging.py --years 2025`
2. Run `python dashboard/data/pipeline/run_all.py`
3. Run `python dashboard/data/promote.py --target local`

### "I want to understand the pipeline"
1. Read **[dashboard/data/pipeline/README.md](../dashboard/data/pipeline/README.md)**
2. Review pipeline step scripts
3. Check **[QUICKSTART.md](QUICKSTART.md)** for setup and execution

### "I want to deploy to production"
1. Read **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**
2. Configure environment variables
3. Follow cloud provider instructions

### "I want to contribute code"
1. Review **[CODING_STANDARDS.md](CODING_STANDARDS.md)**
2. Understand **[STRUCTURE.md](STRUCTURE.md)**
3. Follow **[DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)** for UI changes

---

## 📝 Document Update History

| Date | Change |
|------|--------|
| 2025-10-11 | Documentation cleanup - removed temporary completion reports and outdated references |
| Previous | Various feature documentation and implementation guides |

---

## ✅ Available Documentation

Core documentation:
- ✅ Quick start guide (QUICKSTART.md)
- ✅ Project overview (README.md)
- ✅ Architecture documentation (ARCHITECTURE.md)
- ✅ Pipeline documentation (pipeline/README.md)
- ✅ Deployment guide (DEPLOYMENT_GUIDE.md)
- ✅ Code standards (CODING_STANDARDS.md)
- ✅ Design system (DESIGN_SYSTEM.md)
- ✅ Data structure docs (YEARLY_SUMMARY_VARIABLES.md)

---

**Ready to explore Brazilian perinatal health data!** 🚀
