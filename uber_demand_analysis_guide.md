# Uber NYC Temporal and Spatial Demand Analysis - Complete Guide

## Project Overview
This project analyzes Uber ride request patterns across New York City to uncover hourly, daily, and location-based demand fluctuations that support fleet optimization and surge pricing decisions.

---

## Prerequisites

### Required Libraries
```bash
pip install pandas numpy matplotlib seaborn plotly folium
```

### Dataset
You'll need Uber trip data with at least these columns:
- `START_DATE` - Pickup timestamp
- `END_DATE` - Dropoff timestamp
- `START_LON`, `START_LAT` - Pickup coordinates
- `END_LON`, `END_LAT` - Dropoff coordinates

**Data Sources:**
- NYC Taxi & Limousine Commission: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- Kaggle Uber datasets: https://www.kaggle.com/datasets
- FiveThirtyEight Uber data: https://github.com/fivethirtyeight/uber-tlc-foil-response

---

## Step-by-Step Implementation

### Step 1: Data Loading and Exploration

```python
import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv('uber_nyc_data.csv')

# Initial exploration
print(df.head())
print(df.info())
print(df.describe())
print(f"Dataset shape: {df.shape}")
print(f"Missing values:\n{df.isnull().sum()}")
```

### Step 2: Timestamp Conversion and Feature Engineering

```python
# Convert to datetime
df['START_DATE'] = pd.to_datetime(df['START_DATE'])
df['END_DATE'] = pd.to_datetime(df['END_DATE'])

# Extract temporal features
df['pickup_hour'] = df['START_DATE'].dt.hour
df['pickup_day'] = df['START_DATE'].dt.day
df['pickup_month'] = df['START_DATE'].dt.month
df['pickup_year'] = df['START_DATE'].dt.year
df['pickup_dayofweek'] = df['START_DATE'].dt.dayofweek  # 0=Monday, 6=Sunday
df['pickup_weekday_name'] = df['START_DATE'].dt.day_name()
df['pickup_date'] = df['START_DATE'].dt.date

# Calculate trip duration
df['trip_duration_minutes'] = (df['END_DATE'] - df['START_DATE']).dt.total_seconds() / 60

# Create time period categories
def categorize_time(hour):
    if 6 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 17:
        return 'Afternoon'
    elif 17 <= hour < 21:
        return 'Evening'
    else:
        return 'Night'

df['time_period'] = df['pickup_hour'].apply(categorize_time)

# Weekday vs Weekend
df['is_weekend'] = df['pickup_dayofweek'].isin([5, 6]).astype(int)
```

### Step 3: Hourly Demand Analysis

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (14, 6)

# Hourly demand
hourly_demand = df.groupby('pickup_hour').size().reset_index(name='ride_count')

plt.figure(figsize=(14, 6))
plt.bar(hourly_demand['pickup_hour'], hourly_demand['ride_count'], 
        color='#1f77b4', alpha=0.8)
plt.xlabel('Hour of Day', fontsize=12)
plt.ylabel('Number of Rides', fontsize=12)
plt.title('Uber Ride Demand by Hour of Day', fontsize=14, fontweight='bold')
plt.xticks(range(0, 24))
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.show()

# Peak hours identification
peak_hours = hourly_demand.nlargest(5, 'ride_count')
print("\nTop 5 Peak Hours:")
print(peak_hours)
```

### Step 4: Weekly Pattern Analysis

```python
# Day of week analysis
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
             'Friday', 'Saturday', 'Sunday']
weekly_demand = df.groupby('pickup_weekday_name').size().reindex(day_order)

plt.figure(figsize=(12, 6))
weekly_demand.plot(kind='bar', color='#2ca02c', alpha=0.8)
plt.xlabel('Day of Week', fontsize=12)
plt.ylabel('Number of Rides', fontsize=12)
plt.title('Uber Ride Demand by Day of Week', fontsize=14, fontweight='bold')
plt.xticks(rotation=45)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.show()
```

### Step 5: Weekday vs Weekend Comparison

```python
# Hourly patterns for weekdays vs weekends
weekday_hourly = df[df['is_weekend'] == 0].groupby('pickup_hour').size()
weekend_hourly = df[df['is_weekend'] == 1].groupby('pickup_hour').size()

plt.figure(figsize=(14, 6))
plt.plot(weekday_hourly.index, weekday_hourly.values, 
         marker='o', linewidth=2, label='Weekday', color='#1f77b4')
plt.plot(weekend_hourly.index, weekend_hourly.values, 
         marker='s', linewidth=2, label='Weekend', color='#ff7f0e')
plt.xlabel('Hour of Day', fontsize=12)
plt.ylabel('Number of Rides', fontsize=12)
plt.title('Weekday vs Weekend Demand Patterns', fontsize=14, fontweight='bold')
plt.legend(fontsize=11)
plt.xticks(range(0, 24))
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
```

### Step 6: Heatmap Analysis

```python
# Create hour x day heatmap
heatmap_data = df.pivot_table(
    values='START_DATE', 
    index='pickup_hour', 
    columns='pickup_weekday_name', 
    aggfunc='count'
)[day_order]

plt.figure(figsize=(12, 8))
sns.heatmap(heatmap_data, cmap='YlOrRd', annot=True, fmt='g', cbar_kws={'label': 'Ride Count'})
plt.xlabel('Day of Week', fontsize=12)
plt.ylabel('Hour of Day', fontsize=12)
plt.title('Ride Demand Heatmap: Hour vs Day of Week', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()
```

### Step 7: Spatial Analysis (Location-Based Demand)

```python
# Borough/area-based analysis (if you have borough data)
# If not, you can use coordinate clustering

# Simple coordinate-based hotspot identification
def get_area(lat, lon):
    """Simplified NYC area classification"""
    # Manhattan
    if 40.7 <= lat <= 40.8 and -74.0 <= lon <= -73.95:
        return 'Midtown Manhattan'
    elif 40.8 <= lat <= 40.88 and -73.97 <= lon <= -73.92:
        return 'Upper Manhattan'
    elif 40.70 <= lat <= 40.75 and -74.02 <= lon <= -73.97:
        return 'Downtown Manhattan'
    # Brooklyn
    elif 40.6 <= lat <= 40.72 and -74.0 <= lon <= -73.85:
        return 'Brooklyn'
    # Queens
    elif 40.68 <= lat <= 40.8 and -73.95 <= lon <= -73.7:
        return 'Queens'
    else:
        return 'Other'

df['pickup_area'] = df.apply(lambda row: get_area(row['START_LAT'], row['START_LON']), axis=1)

# Area demand analysis
area_demand = df.groupby('pickup_area').size().sort_values(ascending=False)

plt.figure(figsize=(10, 6))
area_demand.plot(kind='barh', color='#9467bd', alpha=0.8)
plt.xlabel('Number of Rides', fontsize=12)
plt.ylabel('Area', fontsize=12)
plt.title('Ride Demand by Area', fontsize=14, fontweight='bold')
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.show()
```

### Step 8: Business Insights Generation

```python
# Peak demand analysis
print("=" * 60)
print("BUSINESS INSIGHTS SUMMARY")
print("=" * 60)

# 1. Peak hours
peak_hours = hourly_demand.nlargest(3, 'ride_count')
print("\n1. TOP PEAK HOURS:")
for idx, row in peak_hours.iterrows():
    print(f"   {row['pickup_hour']}:00 - {row['ride_count']:,} rides")

# 2. Weekday vs Weekend
weekday_avg = df[df['is_weekend'] == 0].groupby('pickup_date').size().mean()
weekend_avg = df[df['is_weekend'] == 1].groupby('pickup_date').size().mean()
print(f"\n2. DAILY AVERAGES:")
print(f"   Weekday: {weekday_avg:.0f} rides/day")
print(f"   Weekend: {weekend_avg:.0f} rides/day")
print(f"   Difference: {((weekend_avg - weekday_avg) / weekday_avg * 100):+.1f}%")

# 3. Time period distribution
time_period_dist = df['time_period'].value_counts()
print(f"\n3. DEMAND BY TIME PERIOD:")
for period, count in time_period_dist.items():
    print(f"   {period}: {count:,} rides ({count/len(df)*100:.1f}%)")

# 4. Top areas
print(f"\n4. TOP PICKUP AREAS:")
for area, count in area_demand.head(5).items():
    print(f"   {area}: {count:,} rides")

# 5. Low demand periods (opportunities)
low_demand_hours = hourly_demand.nsmallest(5, 'ride_count')
print(f"\n5. LOW DEMAND HOURS (Marketing Opportunity):")
for idx, row in low_demand_hours.iterrows():
    print(f"   {row['pickup_hour']}:00 - {row['ride_count']:,} rides")
```

### Step 9: Advanced Visualizations (Optional)

```python
import plotly.express as px
import plotly.graph_objects as go

# Interactive hourly demand by day
pivot_data = df.pivot_table(
    values='START_DATE',
    index='pickup_hour',
    columns='pickup_weekday_name',
    aggfunc='count'
)[day_order]

fig = go.Figure()
for day in day_order:
    fig.add_trace(go.Scatter(
        x=pivot_data.index,
        y=pivot_data[day],
        mode='lines+markers',
        name=day
    ))

fig.update_layout(
    title='Interactive Hourly Demand by Day of Week',
    xaxis_title='Hour of Day',
    yaxis_title='Number of Rides',
    hovermode='x unified',
    height=500
)
fig.show()
```

### Step 10: Export Results

```python
# Create summary report
summary_stats = {
    'Total Rides': len(df),
    'Date Range': f"{df['START_DATE'].min()} to {df['START_DATE'].max()}",
    'Peak Hour': hourly_demand.loc[hourly_demand['ride_count'].idxmax(), 'pickup_hour'],
    'Busiest Day': weekly_demand.idxmax(),
    'Average Daily Rides': df.groupby('pickup_date').size().mean(),
    'Weekend vs Weekday Ratio': weekend_avg / weekday_avg
}

# Save to CSV
summary_df = pd.DataFrame([summary_stats])
summary_df.to_csv('uber_analysis_summary.csv', index=False)

# Save processed data
df.to_csv('uber_processed_data.csv', index=False)

print("\nFiles saved:")
print("- uber_analysis_summary.csv")
print("- uber_processed_data.csv")
```

---

## Business Recommendations

Based on typical patterns found in such analyses:

### 1. **Fleet Optimization**
- Deploy 40% more drivers during 8-9 AM and 6-8 PM peak hours
- Reduce fleet by 30% during 2-5 AM low-demand periods
- Increase weekend staffing in downtown/entertainment districts by 25%

### 2. **Surge Pricing Strategy**
- Implement dynamic pricing during identified peak hours
- Consider location-based surge multipliers for high-demand areas
- Use predictive models to pre-position drivers before surge events

### 3. **Driver Incentives**
- Offer bonuses for drivers working early morning shifts (3-6 AM)
- Create weekend incentive programs for suburban areas
- Implement heat maps in driver apps showing predicted high-demand zones

### 4. **Marketing & Growth**
- Target promotional campaigns during low-demand hours (10 AM - 3 PM)
- Focus customer acquisition in underserved areas identified in spatial analysis
- Launch corporate partnership programs for morning commute hours

---

## Next Steps for Enhancement

1. **Add weather data** - Correlate demand with weather conditions
2. **Event integration** - Factor in concerts, sports events, holidays
3. **Predictive modeling** - Build ML models to forecast demand
4. **Real-time dashboard** - Create interactive Streamlit/Dash app
5. **Competitive analysis** - Compare with public transit data

---

## Common Issues & Solutions

**Issue**: DateTime parsing errors
- **Solution**: Use `pd.to_datetime(df['column'], errors='coerce')`

**Issue**: Memory errors with large datasets
- **Solution**: Process data in chunks using `chunksize` parameter

**Issue**: Missing coordinate data
- **Solution**: Filter out nulls or use median imputation for small gaps

**Issue**: Timezone inconsistencies
- **Solution**: Standardize to UTC: `df['START_DATE'].dt.tz_localize('UTC')`

---

## Project Deliverables Checklist

- [ ] Clean, processed dataset with temporal features
- [ ] Hourly demand visualization
- [ ] Weekly pattern analysis
- [ ] Weekday vs weekend comparison
- [ ] Heatmap showing hour x day patterns
- [ ] Spatial demand analysis by area
- [ ] Business insights summary document
- [ ] Peak hours and low-demand identification
- [ ] Recommendations for fleet optimization
- [ ] Recommendations for surge pricing

---

## Sample GitHub Repository Structure

```
uber-nyc-demand-analysis/
│
├── data/
│   ├── raw/
│   │   └── uber_nyc_raw.csv
│   └── processed/
│       └── uber_processed.csv
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_temporal_analysis.ipynb
│   └── 03_spatial_analysis.ipynb
│
├── src/
│   ├── data_processing.py
│   ├── visualizations.py
│   └── insights.py
│
├── outputs/
│   ├── figures/
│   └── reports/
│
├── requirements.txt
├── README.md
└── LICENSE
```

---

**Good luck with your project! 🚗📊**
