import pandas as pd

def calculate_growth_metrics(df, group_cols):
    """
    Calculates YoY and QoQ growth metrics.
    Args:
        df: DataFrame with registration data
        group_cols: Columns to group by (e.g., ['Vehicle Type'])
    Returns:
        DataFrame with added 'YoY Growth' and 'QoQ Growth' columns
    """
    df = df.sort_values(['Date'] + group_cols)
    
    # YoY Growth: Current quarter vs. same quarter last year
    df['YoY Growth'] = df.groupby(group_cols)['Registrations'].pct_change(periods=4) * 100
    
    # QoQ Growth: Current quarter vs. previous quarter
    df['QoQ Growth'] = df.groupby(group_cols)['Registrations'].pct_change() * 100
    
    return df

def filter_data(df, date_range, vehicle_types, manufacturers):
    """
    Applies filters to the dataset.
    """
    filtered = df[
        (df['Date'].dt.date >= date_range[0]) & 
        (df['Date'].dt.date <= date_range[1]) &
        (df['Vehicle Type'].isin(vehicle_types)) &
        (df['Manufacturer'].isin(manufacturers))
    ]
    return filtered