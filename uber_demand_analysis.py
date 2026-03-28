#!/usr/bin/env python3
"""
Uber NYC Temporal and Spatial Demand Analysis
Complete Implementation Script

Author: Data Analyst
Date: 2024
Purpose: Analyze Uber ride patterns to optimize fleet and pricing
"""

# ============================================================================
# PART 1: IMPORTS AND SETUP
# ============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set visualization parameters
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (14, 6)
plt.rcParams['font.size'] = 10

print("=" * 70)
print("UBER NYC DEMAND ANALYSIS - INITIALIZATION")
print("=" * 70)
print("\n✓ Libraries imported successfully")

# ============================================================================
# PART 2: DATA LOADING
# ============================================================================

def load_data(filepath):
    """
    Load Uber trip data from CSV file
    
    Expected columns:
    - START_DATE, END_DATE (timestamps)
    - START_LAT, START_LON (pickup coordinates)
    - END_LAT, END_LON (dropoff coordinates)
    """
    print("\n[LOADING DATA]")
    try:
        df = pd.read_csv(filepath)
        print(f"✓ Data loaded: {df.shape[0]:,} rows, {df.shape[1]} columns")
        return df
    except FileNotFoundError:
        print("✗ File not found. Creating sample dataset...")
        return create_sample_data()

def create_sample_data(n_samples=10000):
    """
    Create sample Uber trip data for demonstration
    """
    np.random.seed(42)
    
    # Generate dates over 30 days
    start_date = pd.Timestamp('2024-01-01')
    dates = pd.date_range(start_date, periods=n_samples, freq='5min')
    
    # Simulate realistic patterns
    hours = dates.hour
    days = dates.dayofweek
    
    # More rides during peak hours and weekdays
    weights = 1 + 0.5 * np.sin((hours - 6) * np.pi / 12)
    weights *= (1 + 0.2 * (days < 5))  # weekday boost
    
    # Sample dates based on weights
    indices = np.random.choice(len(dates), n_samples, p=weights/weights.sum())
    sampled_dates = dates[indices]
    
    df = pd.DataFrame({
        'START_DATE': sampled_dates,
        'END_DATE': sampled_dates + pd.Timedelta(minutes=np.random.randint(5, 45, n_samples)),
        'START_LAT': np.random.uniform(40.70, 40.85, n_samples),
        'START_LON': np.random.uniform(-74.02, -73.92, n_samples),
        'END_LAT': np.random.uniform(40.70, 40.85, n_samples),
        'END_LON': np.random.uniform(-74.02, -73.92, n_samples)
    })
    
    print(f"✓ Sample dataset created: {n_samples:,} rides")
    return df

# ============================================================================
# PART 3: DATA PREPROCESSING
# ============================================================================

def preprocess_data(df):
    """
    Convert timestamps and extract temporal features
    """
    print("\n[PREPROCESSING DATA]")
    
    # Convert to datetime
    df['START_DATE'] = pd.to_datetime(df['START_DATE'], errors='coerce')
    df['END_DATE'] = pd.to_datetime(df['END_DATE'], errors='coerce')
    print("✓ Timestamps converted to datetime")
    
    # Extract temporal features
    df['pickup_hour'] = df['START_DATE'].dt.hour
    df['pickup_day'] = df['START_DATE'].dt.day
    df['pickup_month'] = df['START_DATE'].dt.month
    df['pickup_year'] = df['START_DATE'].dt.year
    df['pickup_dayofweek'] = df['START_DATE'].dt.dayofweek  # 0=Monday
    df['pickup_weekday_name'] = df['START_DATE'].dt.day_name()
    df['pickup_date'] = df['START_DATE'].dt.date
    print("✓ Temporal features extracted")
    
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
    df['day_type'] = df['is_weekend'].map({0: 'Weekday', 1: 'Weekend'})
    print("✓ Time categories created")
    
    # Classify pickup areas
    def get_area(lat, lon):
        """Simplified NYC area classification"""
        if pd.isna(lat) or pd.isna(lon):
            return 'Unknown'
        if 40.75 <= lat <= 40.80 and -74.00 <= lon <= -73.95:
            return 'Midtown Manhattan'
        elif 40.80 < lat <= 40.88 and -73.97 <= lon <= -73.92:
            return 'Upper Manhattan'
        elif 40.70 <= lat < 40.75 and -74.02 <= lon <= -73.97:
            return 'Downtown Manhattan'
        elif 40.60 <= lat < 40.72 and -74.02 <= lon <= -73.85:
            return 'Brooklyn'
        elif 40.68 <= lat <= 40.80 and -73.95 <= lon <= -73.70:
            return 'Queens'
        else:
            return 'Other NYC'
    
    df['pickup_area'] = df.apply(lambda row: get_area(row['START_LAT'], row['START_LON']), axis=1)
    print("✓ Geographic areas classified")
    
    # Remove any null values
    initial_count = len(df)
    df = df.dropna(subset=['START_DATE', 'pickup_hour'])
    final_count = len(df)
    print(f"✓ Data cleaned: {initial_count - final_count} rows removed")
    
    return df

# ============================================================================
# PART 4: EXPLORATORY DATA ANALYSIS
# ============================================================================

def display_summary_statistics(df):
    """
    Display key summary statistics
    """
    print("\n" + "=" * 70)
    print("DATA SUMMARY STATISTICS")
    print("=" * 70)
    
    print(f"\nDataset Overview:")
    print(f"  Total Rides: {len(df):,}")
    print(f"  Date Range: {df['START_DATE'].min()} to {df['START_DATE'].max()}")
    print(f"  Time Span: {(df['START_DATE'].max() - df['START_DATE'].min()).days} days")
    
    print(f"\nTrip Duration Statistics:")
    print(f"  Mean: {df['trip_duration_minutes'].mean():.2f} minutes")
    print(f"  Median: {df['trip_duration_minutes'].median():.2f} minutes")
    print(f"  Min: {df['trip_duration_minutes'].min():.2f} minutes")
    print(f"  Max: {df['trip_duration_minutes'].max():.2f} minutes")
    
    print(f"\nDemand Distribution:")
    for period, count in df['time_period'].value_counts().items():
        pct = count / len(df) * 100
        print(f"  {period:12s}: {count:6,} rides ({pct:5.2f}%)")
    
    print(f"\nWeekday vs Weekend:")
    for day_type, count in df['day_type'].value_counts().items():
        pct = count / len(df) * 100
        print(f"  {day_type:10s}: {count:6,} rides ({pct:5.2f}%)")

# ============================================================================
# PART 5: TEMPORAL ANALYSIS
# ============================================================================

def analyze_hourly_demand(df):
    """
    Analyze and visualize hourly demand patterns
    """
    print("\n[ANALYZING HOURLY DEMAND]")
    
    hourly_demand = df.groupby('pickup_hour').size().reset_index(name='ride_count')
    
    # Visualization
    fig, ax = plt.subplots(figsize=(14, 6))
    bars = ax.bar(hourly_demand['pickup_hour'], hourly_demand['ride_count'], 
                   color='steelblue', alpha=0.7, edgecolor='navy')
    
    # Highlight peak hours
    peak_threshold = hourly_demand['ride_count'].quantile(0.75)
    for i, (hour, count) in enumerate(zip(hourly_demand['pickup_hour'], 
                                           hourly_demand['ride_count'])):
        if count >= peak_threshold:
            bars[i].set_color('orangered')
            bars[i].set_alpha(0.8)
    
    ax.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Rides', fontsize=12, fontweight='bold')
    ax.set_title('Uber Ride Demand by Hour of Day\n(Red bars indicate peak hours)', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(range(0, 24))
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on top of bars
    for i, v in enumerate(hourly_demand['ride_count']):
        ax.text(i, v + max(hourly_demand['ride_count']) * 0.01, 
                f'{v:,}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('/home/claude/hourly_demand.png', dpi=300, bbox_inches='tight')
    print("✓ Hourly demand chart saved: hourly_demand.png")
    plt.show()
    
    # Identify peak hours
    peak_hours = hourly_demand.nlargest(5, 'ride_count')
    print("\n  Top 5 Peak Hours:")
    for _, row in peak_hours.iterrows():
        print(f"    {row['pickup_hour']:02d}:00 - {row['ride_count']:,} rides")
    
    return hourly_demand

def analyze_weekly_patterns(df):
    """
    Analyze and visualize weekly demand patterns
    """
    print("\n[ANALYZING WEEKLY PATTERNS]")
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                 'Friday', 'Saturday', 'Sunday']
    weekly_demand = df.groupby('pickup_weekday_name').size().reindex(day_order)
    
    # Visualization
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ['steelblue' if day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] 
              else 'coral' for day in day_order]
    bars = ax.bar(range(7), weekly_demand.values, color=colors, alpha=0.7, edgecolor='navy')
    
    ax.set_xlabel('Day of Week', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Rides', fontsize=12, fontweight='bold')
    ax.set_title('Uber Ride Demand by Day of Week\n(Blue: Weekday, Coral: Weekend)', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(range(7))
    ax.set_xticklabels(day_order, rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels
    for i, v in enumerate(weekly_demand.values):
        ax.text(i, v + max(weekly_demand.values) * 0.01, 
                f'{v:,}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('/home/claude/weekly_demand.png', dpi=300, bbox_inches='tight')
    print("✓ Weekly demand chart saved: weekly_demand.png")
    plt.show()
    
    busiest_day = weekly_demand.idxmax()
    print(f"\n  Busiest Day: {busiest_day} ({weekly_demand.max():,} rides)")
    
    return weekly_demand

def compare_weekday_weekend(df):
    """
    Compare demand patterns between weekdays and weekends
    """
    print("\n[COMPARING WEEKDAY VS WEEKEND]")
    
    weekday_hourly = df[df['is_weekend'] == 0].groupby('pickup_hour').size()
    weekend_hourly = df[df['is_weekend'] == 1].groupby('pickup_hour').size()
    
    # Visualization
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(weekday_hourly.index, weekday_hourly.values, 
            marker='o', linewidth=2.5, markersize=8, 
            label='Weekday', color='steelblue', alpha=0.8)
    ax.plot(weekend_hourly.index, weekend_hourly.values, 
            marker='s', linewidth=2.5, markersize=8, 
            label='Weekend', color='coral', alpha=0.8)
    
    ax.fill_between(weekday_hourly.index, weekday_hourly.values, alpha=0.2, color='steelblue')
    ax.fill_between(weekend_hourly.index, weekend_hourly.values, alpha=0.2, color='coral')
    
    ax.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Rides', fontsize=12, fontweight='bold')
    ax.set_title('Weekday vs Weekend Demand Patterns', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='upper left', framealpha=0.9)
    ax.set_xticks(range(0, 24))
    ax.grid(alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig('/home/claude/weekday_weekend_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Weekday/Weekend comparison saved: weekday_weekend_comparison.png")
    plt.show()
    
    # Statistics
    weekday_avg = df[df['is_weekend'] == 0].groupby('pickup_date').size().mean()
    weekend_avg = df[df['is_weekend'] == 1].groupby('pickup_date').size().mean()
    
    print(f"\n  Average Daily Rides:")
    print(f"    Weekday: {weekday_avg:.0f} rides/day")
    print(f"    Weekend: {weekend_avg:.0f} rides/day")
    print(f"    Difference: {((weekend_avg - weekday_avg) / weekday_avg * 100):+.1f}%")

def create_demand_heatmap(df):
    """
    Create heatmap showing demand by hour and day of week
    """
    print("\n[CREATING DEMAND HEATMAP]")
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                 'Friday', 'Saturday', 'Sunday']
    
    heatmap_data = df.pivot_table(
        values='START_DATE',
        index='pickup_hour',
        columns='pickup_weekday_name',
        aggfunc='count'
    )[day_order]
    
    # Visualization
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(heatmap_data, cmap='YlOrRd', annot=True, fmt='g', 
                cbar_kws={'label': 'Number of Rides'}, linewidths=0.5,
                linecolor='white', ax=ax)
    
    ax.set_xlabel('Day of Week', fontsize=12, fontweight='bold')
    ax.set_ylabel('Hour of Day', fontsize=12, fontweight='bold')
    ax.set_title('Ride Demand Heatmap: Hour vs Day of Week', 
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/claude/demand_heatmap.png', dpi=300, bbox_inches='tight')
    print("✓ Demand heatmap saved: demand_heatmap.png")
    plt.show()

# ============================================================================
# PART 6: SPATIAL ANALYSIS
# ============================================================================

def analyze_spatial_demand(df):
    """
    Analyze demand patterns by geographic area
    """
    print("\n[ANALYZING SPATIAL DEMAND]")
    
    area_demand = df.groupby('pickup_area').size().sort_values(ascending=True)
    
    # Visualization
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(area_demand)))
    bars = ax.barh(range(len(area_demand)), area_demand.values, color=colors, alpha=0.8)
    
    ax.set_yticks(range(len(area_demand)))
    ax.set_yticklabels(area_demand.index)
    ax.set_xlabel('Number of Rides', fontsize=12, fontweight='bold')
    ax.set_ylabel('Area', fontsize=12, fontweight='bold')
    ax.set_title('Ride Demand by Geographic Area', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Add value labels
    for i, v in enumerate(area_demand.values):
        ax.text(v + max(area_demand.values) * 0.01, i, 
                f'{v:,}', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('/home/claude/spatial_demand.png', dpi=300, bbox_inches='tight')
    print("✓ Spatial demand chart saved: spatial_demand.png")
    plt.show()
    
    print("\n  Top Pickup Areas:")
    for area, count in area_demand.sort_values(ascending=False).head(5).items():
        pct = count / len(df) * 100
        print(f"    {area:20s}: {count:6,} rides ({pct:5.2f}%)")
    
    return area_demand

# ============================================================================
# PART 7: BUSINESS INSIGHTS
# ============================================================================

def generate_business_insights(df, hourly_demand):
    """
    Generate actionable business insights
    """
    print("\n" + "=" * 70)
    print("BUSINESS INSIGHTS & RECOMMENDATIONS")
    print("=" * 70)
    
    # 1. Peak demand analysis
    print("\n1. PEAK DEMAND WINDOWS:")
    peak_hours = hourly_demand.nlargest(3, 'ride_count')
    for _, row in peak_hours.iterrows():
        hour = row['pickup_hour']
        count = row['ride_count']
        pct = count / len(df) * 100
        print(f"   • {hour:02d}:00-{hour+1:02d}:00: {count:,} rides ({pct:.1f}% of total)")
    
    print("\n   Recommendation:")
    print("   → Deploy 40% more drivers during these peak hours")
    print("   → Implement surge pricing (1.5x-2.0x multiplier)")
    print("   → Pre-position drivers 30 minutes before peak onset")
    
    # 2. Low demand opportunities
    print("\n2. LOW DEMAND PERIODS (Growth Opportunities):")
    low_hours = hourly_demand.nsmallest(3, 'ride_count')
    for _, row in low_hours.iterrows():
        hour = row['pickup_hour']
        count = row['ride_count']
        print(f"   • {hour:02d}:00-{hour+1:02d}:00: {count:,} rides")
    
    print("\n   Recommendation:")
    print("   → Launch promotional campaigns (20-30% discount)")
    print("   → Reduce fleet by 30% to optimize costs")
    print("   → Offer driver incentives for working these shifts")
    
    # 3. Weekday vs Weekend insights
    weekday_avg = df[df['is_weekend'] == 0].groupby('pickup_date').size().mean()
    weekend_avg = df[df['is_weekend'] == 1].groupby('pickup_date').size().mean()
    
    print(f"\n3. WEEKDAY VS WEEKEND PATTERNS:")
    print(f"   Weekday Average: {weekday_avg:.0f} rides/day")
    print(f"   Weekend Average: {weekend_avg:.0f} rides/day")
    
    if weekend_avg > weekday_avg:
        diff = (weekend_avg - weekday_avg) / weekday_avg * 100
        print(f"   Weekend demand is {diff:.1f}% higher")
        print("\n   Recommendation:")
        print("   → Increase weekend staffing, especially in entertainment districts")
        print("   → Partner with events/venues for exclusive pickup zones")
    else:
        diff = (weekday_avg - weekend_avg) / weekend_avg * 100
        print(f"   Weekday demand is {diff:.1f}% higher")
        print("\n   Recommendation:")
        print("   → Focus on corporate partnerships for weekday commuters")
        print("   → Offer subscription plans for regular business users")
    
    # 4. Geographic insights
    area_demand = df.groupby('pickup_area').size().sort_values(ascending=False)
    top_area = area_demand.index[0]
    top_count = area_demand.iloc[0]
    
    print(f"\n4. GEOGRAPHIC HOTSPOTS:")
    print(f"   Top Area: {top_area} ({top_count:,} rides)")
    
    print("\n   Recommendation:")
    print(f"   → Establish dedicated hub in {top_area}")
    print("   → Deploy 50% of fleet in top 3 areas during peak hours")
    print("   → Use heat maps for real-time driver positioning")
    
    # 5. Time period analysis
    time_period_dist = df['time_period'].value_counts()
    
    print(f"\n5. DEMAND BY TIME PERIOD:")
    for period in ['Morning', 'Afternoon', 'Evening', 'Night']:
        if period in time_period_dist:
            count = time_period_dist[period]
            pct = count / len(df) * 100
            print(f"   {period:12s}: {count:6,} rides ({pct:5.2f}%)")
    
    print("\n   Recommendation:")
    print("   → Tailor marketing messages by time period")
    print("   → Evening: Target entertainment/dining promotions")
    print("   → Morning: Focus on airport/business routes")
    
    # 6. Overall strategy
    print("\n6. STRATEGIC PRIORITIES:")
    print("   ✓ Implement predictive demand forecasting model")
    print("   ✓ Create dynamic pricing algorithm based on these patterns")
    print("   ✓ Develop driver app with real-time demand heat maps")
    print("   ✓ Launch A/B tests for promotional campaigns in low-demand periods")
    print("   ✓ Build partnerships with major employers in high-demand areas")

# ============================================================================
# PART 8: EXPORT RESULTS
# ============================================================================

def export_results(df, hourly_demand, weekly_demand, area_demand):
    """
    Export analysis results to CSV files
    """
    print("\n[EXPORTING RESULTS]")
    
    # Summary statistics
    summary_stats = {
        'Total_Rides': [len(df)],
        'Date_Range_Start': [df['START_DATE'].min()],
        'Date_Range_End': [df['START_DATE'].max()],
        'Peak_Hour': [hourly_demand.loc[hourly_demand['ride_count'].idxmax(), 'pickup_hour']],
        'Peak_Hour_Rides': [hourly_demand['ride_count'].max()],
        'Busiest_Day': [weekly_demand.idxmax()],
        'Avg_Daily_Rides': [df.groupby('pickup_date').size().mean()],
        'Avg_Trip_Duration_Min': [df['trip_duration_minutes'].mean()],
        'Top_Pickup_Area': [area_demand.index[0]],
        'Weekend_Avg_Daily': [df[df['is_weekend'] == 1].groupby('pickup_date').size().mean()],
        'Weekday_Avg_Daily': [df[df['is_weekend'] == 0].groupby('pickup_date').size().mean()]
    }
    
    summary_df = pd.DataFrame(summary_stats)
    summary_df.to_csv('/home/claude/analysis_summary.csv', index=False)
    print("✓ Summary statistics saved: analysis_summary.csv")
    
    # Hourly demand
    hourly_demand.to_csv('/home/claude/hourly_demand_data.csv', index=False)
    print("✓ Hourly demand data saved: hourly_demand_data.csv")
    
    # Weekly demand
    weekly_demand.to_frame('ride_count').to_csv('/home/claude/weekly_demand_data.csv')
    print("✓ Weekly demand data saved: weekly_demand_data.csv")
    
    # Area demand
    area_demand.to_frame('ride_count').to_csv('/home/claude/area_demand_data.csv')
    print("✓ Area demand data saved: area_demand_data.csv")
    
    # Processed dataset (sample)
    df.head(1000).to_csv('/home/claude/processed_sample_data.csv', index=False)
    print("✓ Processed sample data saved: processed_sample_data.csv")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function
    """
    print("\n" + "=" * 70)
    print("UBER NYC TEMPORAL AND SPATIAL DEMAND ANALYSIS")
    print("=" * 70)
    
    # Step 1: Load data
    # Replace 'uber_data.csv' with your actual file path
    df = load_data('uber_data.csv')
    
    # Step 2: Preprocess
    df = preprocess_data(df)
    
    # Step 3: Display summary
    display_summary_statistics(df)
    
    # Step 4: Temporal analysis
    hourly_demand = analyze_hourly_demand(df)
    weekly_demand = analyze_weekly_patterns(df)
    compare_weekday_weekend(df)
    create_demand_heatmap(df)
    
    # Step 5: Spatial analysis
    area_demand = analyze_spatial_demand(df)
    
    # Step 6: Generate insights
    generate_business_insights(df, hourly_demand)
    
    # Step 7: Export results
    export_results(df, hourly_demand, weekly_demand, area_demand)
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE!")
    print("=" * 70)
    print("\nGenerated Files:")
    print("  • hourly_demand.png")
    print("  • weekly_demand.png")
    print("  • weekday_weekend_comparison.png")
    print("  • demand_heatmap.png")
    print("  • spatial_demand.png")
    print("  • analysis_summary.csv")
    print("  • hourly_demand_data.csv")
    print("  • weekly_demand_data.csv")
    print("  • area_demand_data.csv")
    print("  • processed_sample_data.csv")
    print("\n✓ All analysis complete and files saved successfully!")

if __name__ == "__main__":
    main()
