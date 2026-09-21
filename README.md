# Lightweight Retail Platform Backend Core

A structured, testable Python core representing a clean retail catalog, inventory management, and checkout system using **Pydantic** for rigorous data validation.

## Project Structure
```text
retail_platform/
├── app/
│   └── main.py          # Core logic, Pydantic models, and inventory state
└── tests/
    └── test_main.py     # Suite covering stock validation, safety limits, and calculations
```

## Setup & Execution

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

### 2. Install Dependencies
Install the required packages for data modeling and test runners:
```bash
pip install pydantic pytest
```

### 3. Run the Test Suite
Execute the tests directly from the root project directory:
```bash
pytest
```
