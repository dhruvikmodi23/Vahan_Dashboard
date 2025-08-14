import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime

def scrape_vahan_data():
    """
    Scrapes vehicle registration data from Vahan Dashboard.
    Returns a DataFrame with columns: Date, Vehicle Type, Manufacturer, Registrations.
    """
    VAHAN_URL = "https://vahan.parivahan.gov.in/vahan4dashboard/"
    HEADERS = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(VAHAN_URL, headers=HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Placeholder: Replace with actual scraping logic
        # Example: Extract tables with registration data
        tables = soup.find_all('table')
        
        if not tables:
            raise ValueError("No tables found on the page")
        
        # Simulate scraped data (replace with actual parsing)
        data = {
            'Date': pd.date_range(start='2020-01-01', end='2023-12-31', freq='Q'),
            'Vehicle Type': np.random.choice(['2W', '3W', '4W'], 16),
            'Manufacturer': np.random.choice([
                'Hero', 'Honda', 'Bajaj', 'TVS', 'Royal Enfield',
                'Bajaj', 'Mahindra', 'Piaggio', 'TVS',
                'Maruti', 'Hyundai', 'Tata', 'Mahindra', 'Kia'
            ], 16),
            'Registrations': np.random.randint(10000, 50000, 16)
        }
        
        df = pd.DataFrame(data)
        df['Year'] = df['Date'].dt.year
        df['Quarter'] = 'Q' + df['Date'].dt.quarter.astype(str)
        
        return df

    except Exception as e:
        print(f"Scraping failed: {e}")
        return None