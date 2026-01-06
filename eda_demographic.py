"""
Comprehensive Exploratory Data Analysis (EDA) for Aadhaar Demographic Data
Following DataSentinel_XLSX protocol for statistical analysis and visualization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

# Create output directories
output_dir = Path("visualizations/demographic")
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("COMPREHENSIVE EDA: AADHAAR DEMOGRAPHIC DATA")
print("=" * 80)

# ============================================================================
# PHASE 1: CATALOGING
# ============================================================================
print("\n## PHASE 1: CATALOGING")
print("-" * 80)

data_folder = Path("api_data_aadhar_demographic/api_data_aadhar_demographic")
csv_files = sorted(data_folder.glob("*.csv"))

print(f"\nFound {len(csv_files)} CSV files:")
for i, file in enumerate(csv_files, 1):
    print(f"  {i}. {file.name}")

# ============================================================================
# PHASE 2: DATA LOADING AND COMBINATION
# ============================================================================
print("\n## PHASE 2: DATA LOADING")
print("-" * 80)

dataframes = []
for file in csv_files:
    print(f"Loading {file.name}...")
    df = pd.read_csv(file)
    print(f"  Rows: {len(df):,}, Columns: {len(df.columns)}")
    dataframes.append(df)

# Combine all dataframes
df = pd.concat(dataframes, ignore_index=True)
print(f"\nCombined dataset: {len(df):,} rows, {len(df.columns)} columns")

# ============================================================================
# PHASE 3: SCHEMA AUDIT
# ============================================================================
print("\n## PHASE 3: SCHEMA AUDIT")
print("-" * 80)

print("\n### Column Information:")
print(f"Total columns: {len(df.columns)}")
print("\nColumn names and data types:")
for col in df.columns:
    dtype = df[col].dtype
    null_count = df[col].isnull().sum()
    null_pct = (null_count / len(df)) * 100
    print(f"  {col:20s} | Type: {str(dtype):15s} | Nulls: {null_count:8,} ({null_pct:5.2f}%)")

print("\n### First 10 Rows:")
print(df.head(10).to_string())

print("\n### Data Quality Issues:")
issues = []
if df.isnull().sum().sum() > 0:
    issues.append(f"Missing values detected: {df.isnull().sum().sum()} total")
if df.duplicated().sum() > 0:
    issues.append(f"Duplicate rows: {df.duplicated().sum()}")
if 'date' in df.columns:
    try:
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
        invalid_dates = df['date'].isnull().sum()
        if invalid_dates > 0:
            issues.append(f"Invalid date formats: {invalid_dates}")
    except:
        issues.append("Date column conversion issues")

if issues:
    for issue in issues:
        print(f"  [WARNING] {issue}")
else:
    print("  [OK] No major data quality issues detected")

# ============================================================================
# PHASE 4: STATISTICAL PROFILING
# ============================================================================
print("\n## PHASE 4: STATISTICAL PROFILING")
print("-" * 80)

# Identify numeric columns
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
print(f"\nNumeric columns: {numeric_cols}")

# Descriptive statistics
print("\n### Descriptive Statistics:")
desc_stats = df[numeric_cols].describe()
print(desc_stats.to_string())

# Additional statistics
print("\n### Additional Statistics:")
additional_stats = []
for col in numeric_cols:
    mean_val = df[col].mean()
    median_val = df[col].median()
    std_val = df[col].std()
    var_val = df[col].var()
    skew_val = stats.skew(df[col].dropna())
    kurt_val = stats.kurtosis(df[col].dropna())
    
    additional_stats.append({
        'Column': col,
        'Mean': mean_val,
        'Median': median_val,
        'Std Dev': std_val,
        'Variance': var_val,
        'Skewness': skew_val,
        'Kurtosis': kurt_val
    })
    
    print(f"\n{col}:")
    print(f"  Mean:     {mean_val:,.2f}")
    print(f"  Median:   {median_val:,.2f}")
    print(f"  Std Dev:  {std_val:,.2f}")
    print(f"  Variance: {var_val:,.2f}")
    print(f"  Skewness: {skew_val:.4f}")
    print(f"  Kurtosis: {kurt_val:.4f}")

# Demographic group analysis
print("\n### Demographic Group Analysis:")
if all(col in df.columns for col in ['demo_age_5_17', 'demo_age_17_']):
    total_by_demo = {
        'Age 5-17': df['demo_age_5_17'].sum(),
        'Age 17+': df['demo_age_17_'].sum()
    }
    total_all = sum(total_by_demo.values())
    
    print("\nTotal demographic records by age group:")
    for demo_group, count in total_by_demo.items():
        pct = (count / total_all) * 100
        print(f"  {demo_group:15s}: {count:12,} ({pct:5.2f}%)")
    print(f"  {'Total':15s}: {total_all:12,} (100.00%)")

# IQR-based outlier detection
print("\n### Outlier Detection (IQR Method):")
outlier_summary = []
for col in numeric_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
    outlier_count = len(outliers)
    outlier_pct = (outlier_count / len(df)) * 100
    
    outlier_summary.append({
        'Column': col,
        'Q1': Q1,
        'Q3': Q3,
        'IQR': IQR,
        'Lower Bound': lower_bound,
        'Upper Bound': upper_bound,
        'Outlier Count': outlier_count,
        'Outlier %': outlier_pct
    })
    
    print(f"\n{col}:")
    print(f"  Q1: {Q1:,.2f}, Q3: {Q3:,.2f}, IQR: {IQR:,.2f}")
    print(f"  Bounds: [{lower_bound:,.2f}, {upper_bound:,.2f}]")
    print(f"  Outliers: {outlier_count:,} ({outlier_pct:.2f}%)")

# ============================================================================
# PHASE 5: VISUALIZATION
# ============================================================================
print("\n## PHASE 5: VISUALIZATION")
print("-" * 80)

# 1. Distribution plots
print("\nGenerating distribution plots...")
fig, axes = plt.subplots(len(numeric_cols), 1, figsize=(12, 6 * len(numeric_cols)))
if len(numeric_cols) == 1:
    axes = [axes]

for idx, col in enumerate(numeric_cols):
    axes[idx].hist(df[col].dropna(), bins=50, edgecolor='black', alpha=0.7)
    axes[idx].set_title(f'Distribution of {col}', fontsize=14, fontweight='bold')
    axes[idx].set_xlabel(col, fontsize=12)
    axes[idx].set_ylabel('Frequency', fontsize=12)
    axes[idx].axvline(df[col].mean(), color='red', linestyle='--', 
                      label=f'Mean: {df[col].mean():,.2f}')
    axes[idx].axvline(df[col].median(), color='green', linestyle='--', 
                      label=f'Median: {df[col].median():,.2f}')
    axes[idx].legend()
    axes[idx].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(output_dir / "distributions.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"  [OK] Saved: {output_dir / 'distributions.png'}")

# 2. Box plots for outlier visualization
print("\nGenerating box plots...")
fig, axes = plt.subplots(1, len(numeric_cols), figsize=(8 * len(numeric_cols), 8))
if len(numeric_cols) == 1:
    axes = [axes]

for idx, col in enumerate(numeric_cols):
    bp = axes[idx].boxplot(df[col].dropna(), patch_artist=True)
    bp['boxes'][0].set_facecolor('lightgreen')
    axes[idx].set_title(f'Box Plot: {col}', fontsize=14, fontweight='bold')
    axes[idx].set_ylabel(col, fontsize=12)
    axes[idx].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(output_dir / "boxplots.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"  [OK] Saved: {output_dir / 'boxplots.png'}")

# 3. Correlation heatmap
if len(numeric_cols) > 1:
    print("\nGenerating correlation heatmap...")
    corr_matrix = df[numeric_cols].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm', 
                center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8})
    plt.title('Correlation Heatmap: Demographic Age Groups', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(output_dir / "correlations.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Saved: {output_dir / 'correlations.png'}")

# 4. Demographic group comparison
if all(col in df.columns for col in ['demo_age_5_17', 'demo_age_17_']):
    print("\nGenerating demographic group comparison...")
    demo_totals = {
        'Age 5-17': df['demo_age_5_17'].sum(),
        'Age 17+': df['demo_age_17_'].sum()
    }
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Pie chart
    ax1.pie(demo_totals.values(), labels=demo_totals.keys(), autopct='%1.1f%%',
            startangle=90, colors=['#66b3ff', '#99ff99'])
    ax1.set_title('Demographic Distribution by Age Group', fontsize=14, fontweight='bold')
    
    # Bar chart
    ax2.bar(demo_totals.keys(), demo_totals.values(), color=['#66b3ff', '#99ff99'])
    ax2.set_title('Total Demographic Records by Age Group', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Total Count', fontsize=12)
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(output_dir / "demographic_group_comparison.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Saved: {output_dir / 'demographic_group_comparison.png'}")

# 5. Geographic distribution (Top 20 states)
if 'state' in df.columns:
    print("\nGenerating geographic distribution...")
    state_stats = df.groupby('state')[numeric_cols].sum().sort_values(
        by=numeric_cols[0], ascending=False).head(20)
    
    fig, axes = plt.subplots(len(numeric_cols), 1, figsize=(14, 5 * len(numeric_cols)))
    if len(numeric_cols) == 1:
        axes = [axes]
    
    for idx, col in enumerate(numeric_cols):
        state_stats[col].plot(kind='barh', ax=axes[idx], color='steelblue')
        axes[idx].set_title(f'Top 20 States by {col}', fontsize=14, fontweight='bold')
        axes[idx].set_xlabel('Total Count', fontsize=12)
        axes[idx].set_ylabel('State', fontsize=12)
        axes[idx].grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig(output_dir / "geographic_distribution.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Saved: {output_dir / 'geographic_distribution.png'}")

# 6. Time series analysis
if 'date' in df.columns:
    print("\nGenerating time series analysis...")
    try:
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
        time_series = df.groupby('date')[numeric_cols].sum().reset_index()
        
        fig, axes = plt.subplots(len(numeric_cols), 1, figsize=(14, 5 * len(numeric_cols)))
        if len(numeric_cols) == 1:
            axes = [axes]
        
        for idx, col in enumerate(numeric_cols):
            axes[idx].plot(time_series['date'], time_series[col], 
                          marker='o', linewidth=2, markersize=4)
            axes[idx].set_title(f'Time Series: {col}', fontsize=14, fontweight='bold')
            axes[idx].set_xlabel('Date', fontsize=12)
            axes[idx].set_ylabel('Total Count', fontsize=12)
            axes[idx].grid(True, alpha=0.3)
            axes[idx].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_dir / "time_series.png", dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  [OK] Saved: {output_dir / 'time_series.png'}")
    except Exception as e:
        print(f"  [WARNING] Time series generation failed: {e}")

# ============================================================================
# PHASE 6: SYNTHESIS AND SUMMARY
# ============================================================================
print("\n## PHASE 6: SYNTHESIS")
print("-" * 80)

# Create summary statistics table
summary_data = {
    'Metric': [],
    'Value': []
}

summary_data['Metric'].extend(['Total Records', 'Total Columns', 'Numeric Columns'])
summary_data['Value'].extend([f"{len(df):,}", f"{len(df.columns)}", f"{len(numeric_cols)}"])

for col in numeric_cols:
    summary_data['Metric'].append(f'{col} - Mean')
    summary_data['Value'].append(f"{df[col].mean():,.2f}")
    summary_data['Metric'].append(f'{col} - Median')
    summary_data['Value'].append(f"{df[col].median():,.2f}")
    summary_data['Metric'].append(f'{col} - Std Dev')
    summary_data['Value'].append(f"{df[col].std():,.2f}")

summary_df = pd.DataFrame(summary_data)
print("\n### Summary Statistics Table:")
print(summary_df.to_string(index=False))

# Save summary to CSV
summary_df.to_csv(output_dir.parent / "demographic_summary_stats.csv", index=False)
print(f"\n  [OK] Summary statistics saved to: {output_dir.parent / 'demographic_summary_stats.csv'}")

print("\n" + "=" * 80)
print("EDA COMPLETE: DEMOGRAPHIC DATA")
print("=" * 80)
print(f"\nAll visualizations saved to: {output_dir}")
print("\nNext steps:")
print("  1. Review generated visualizations")
print("  2. Check summary statistics CSV")
print("  3. Generate markdown report with insights")

