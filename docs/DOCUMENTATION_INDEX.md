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

## 📋 Core Documentation

### Architecture & Design

#### **[ARCHITECTURE.md](ARCHITECTURE.md)** 🏗️
- Three-tiered database architecture
- Staging vs production environments
- System design and data flow

#### **[STRUCTURE.md](STRUCTURE.md)** 📁
- Project file organization
- Directory structure
- Module descriptions

#### **[DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)** 🎨
- UI/UX design guidelines
- Color schemes and typography
- Component design patterns

### Data Pipeline

#### **[dashboard/data/pipeline/README.md](../dashboard/data/pipeline/README.md)** ⚡
- SQL-based pipeline architecture
- 5-step transformation process
- Memory-efficient implementation
- Performance benchmarks
- Complete pipeline execution guide

### Dashboard Features



#### **[YEARLY_SUMMARY_VARIABLES.md](YEARLY_SUMMARY_VARIABLES.md)** 📈
- Annual summary metrics
- Data structure documentation
- Variable definitions

#### **[YEAR_CARDS_TABS_LAYOUT.md](YEAR_CARDS_TABS_LAYOUT.md)** 🗂️
- Dashboard layout design
- Component organization
- User interface structure

#### **[PIPELINE_GEOGRAPHIC_ENHANCEMENT.md](PIPELINE_GEOGRAPHIC_ENHANCEMENT.md)** 🗺️
- Geographic analysis features
- Regional data processing
- Geospatial capabilities

### Deployment & Operations

#### **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** 🚀
- Cloud deployment instructions
- Environment configuration
- Production setup (Render, Hugging Face Spaces)

#### **[PRODUCTION_DATA_GRANULARITY.md](PRODUCTION_DATA_GRANULARITY.md)** 📉
- Production database optimization
- Data granularity decisions
- Storage and performance trade-offs

#### **[CODING_STANDARDS.md](CODING_STANDARDS.md)** 📝
- Code style guidelines
- Best practices
- Development standards

#### **[PYTHON_313_COMPATIBILITY.md](PYTHON_313_COMPATIBILITY.md)** 🐍
- Python version compatibility
- Dependency management
- Known issues and workarounds

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
