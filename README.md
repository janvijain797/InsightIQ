# InsightIQ – AI-Powered Data Analytics Platform

InsightIQ is an AI-powered data analytics platform that helps users analyze raw CSV datasets through a simple and interactive interface.

It automates the initial data analysis workflow by providing dataset inspection, data cleaning, visualization, AI-generated insights, and downloadable reports in one application.

---

## 📌 Problem Statement

Working with raw datasets often involves repetitive tasks such as:

- Understanding dataset structure
- Checking missing values
- Detecting duplicate records
- Identifying numeric and categorical columns
- Analyzing data quality
- Creating basic visualizations
- Finding meaningful patterns and insights
- Preparing reports

These tasks can require significant manual effort, especially when working with different datasets.

InsightIQ was developed to simplify and automate this initial data analysis workflow.

---

## 🎯 Project Objective

The main objective of InsightIQ is to provide a simple platform where a user can:

1. Upload a CSV dataset
2. Inspect the dataset
3. Detect and handle common data-quality issues
4. Analyze numeric and categorical columns
5. Visualize important data
6. Generate AI-powered insights
7. Download the cleaned dataset and analysis report

---

## ✨ Key Features

### 📂 1. Dataset Upload

Users can upload CSV datasets directly through the application.

InsightIQ automatically reads the dataset using Pandas and displays an initial preview.

---

### 🧹 2. Data Cleaning & Quality Analysis

The application checks the dataset for common quality issues such as:

- Missing values
- Duplicate rows
- High-missing-value columns
- Data types
- Numeric columns
- Categorical columns
- Column cardinality

The platform can:

- Remove duplicate rows
- Remove columns with a high percentage of missing values
- Fill missing numeric values using the median
- Fill missing categorical values using `"Unknown"`

The original dataset is also preserved so that the analysis can be viewed after navigating between application sections.

---

### 📊 3. Dataset Analysis

InsightIQ automatically analyzes the uploaded dataset and provides:

- Dataset dimensions
- Column names
- Data types
- Numeric column statistics
- Categorical column information
- Value counts
- Correlation analysis for numeric columns
- Cardinality analysis

The application is designed to work with different tabular datasets instead of being hardcoded to one specific dataset.

---

### 📈 4. Interactive Dashboard

The Dashboard provides a visual summary of the cleaned dataset.

It includes:

- Dataset KPIs
- Numeric column visualization
- Categorical data visualization
- Automatic column-type detection
- Identifier-like numeric column filtering

Identifier-like columns such as IDs, PIN codes, postal codes, and phone numbers are excluded from measurement-based visualizations when detected through the application's heuristic rules.

---

### 🤖 5. AI-Powered Insights

InsightIQ integrates the Google Gemini API to generate human-readable insights from the cleaned dataset.

The AI analysis is structured into:

1. Key Findings
2. Important Data Issues
3. Statistical Insights
4. Recommendations
5. Overall Summary

The application sends relevant dataset information to Gemini and displays the generated analysis inside the platform.

---

### 📄 6. Reports

Users can download:

- Cleaned dataset as a CSV file
- Analysis report

This makes it easier to use the processed data outside the application.

---

### ⚙️ 7. Settings

The Settings section provides options for:

- Light/Dark theme
- Number of rows displayed in tables
- Success notifications
- Project information
- Help section

---

## 🛠️ Technology Stack

### Programming Language

- Python

### Application Framework

- Streamlit

### Data Processing & Analysis

- Pandas
- NumPy

### AI Integration

- Google Gemini API
- Google GenAI Python SDK

### Visualization

- Streamlit built-in charts

### Version Control

- Git
- GitHub

---

## 🔄 Application Workflow

```text
             ┌─────────────────┐
             │  Upload CSV     │
             └────────┬────────┘
                      ↓
             ┌─────────────────┐
             │ Dataset         │
             │ Inspection      │
             └────────┬────────┘
                      ↓
             ┌─────────────────┐
             │ Data Cleaning   │
             │ & Quality Check │
             └────────┬────────┘
                      ↓
             ┌─────────────────┐
             │ Data Analysis   │
             └────────┬────────┘
                      ↓
             ┌─────────────────┐
             │ Dashboard &     │
             │ Visualization   │
             └────────┬────────┘
                      ↓
             ┌─────────────────┐
             │ Gemini AI       │
             │ Insights        │
             └────────┬────────┘
                      ↓
             ┌─────────────────┐
             │ Reports &       │
             │ Cleaned Data    │
             └─────────────────┘
```
