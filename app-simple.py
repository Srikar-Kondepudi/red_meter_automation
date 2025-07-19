#!/usr/bin/env python3
"""
SIMPLE FLASK APP FOR VERCEL DEPLOYMENT
======================================

A simplified Flask application to test Vercel deployment.
"""

from flask import Flask, render_template, jsonify
import pandas as pd
import numpy as np
import json
from datetime import datetime
import warnings
import os
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Global variables to store dashboard data
dashboard_data = {
    'status': 'NORMAL',
    'trouble_count': 0,
    'total_count': 0,
    'trouble_rate': 0.0,
    'alerts': [],
    'recommendations': []
}

def load_and_process_data():
    """Load and process the data for the dashboard"""
    try:
        # Load data
        df = pd.read_csv('June18-21_data.csv', parse_dates=['Timestamp'])
        df = df.dropna()
        
        # Simple trouble detection without ML
        troubles = []
        for _, row in df.iterrows():
            pressure = row['Pressure']
            temperature = row['Temperature']
            dv = row['DV']
            
            # Simple threshold-based trouble detection
            if pressure < 0.1 or pressure > 20:
                troubles.append({
                    'timestamp': row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'pressure': pressure,
                    'temperature': temperature,
                    'dv': dv,
                    'trouble_type': 'PRESSURE_ISSUE'
                })
            elif temperature < 20 or temperature > 35:
                troubles.append({
                    'timestamp': row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'pressure': pressure,
                    'temperature': temperature,
                    'dv': dv,
                    'trouble_type': 'TEMPERATURE_ISSUE'
                })
            elif dv < -500 or dv > 500:
                troubles.append({
                    'timestamp': row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'pressure': pressure,
                    'temperature': temperature,
                    'dv': dv,
                    'trouble_type': 'DV_EXTREME'
                })
        
        return df, troubles
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, []

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/dashboard-data')
def get_dashboard_data():
    """API endpoint to get dashboard data"""
    try:
        # Load and process data
        df, troubles = load_and_process_data()
        
        if df is None:
            return jsonify({'error': 'Failed to load data'}), 500
        
        # Calculate statistics
        trouble_count = len(troubles)
        total_count = len(df)
        trouble_rate = (trouble_count / total_count * 100) if total_count > 0 else 0
        
        # Determine status
        if trouble_count == 0:
            status = "NORMAL"
        elif trouble_count <= 50:
            status = "ATTENTION"
        else:
            status = "TROUBLE"
        
        # Update global data
        dashboard_data.update({
            'status': status,
            'trouble_count': trouble_count,
            'total_count': total_count,
            'trouble_rate': trouble_rate,
            'alerts': troubles[:10],  # Show first 10 alerts
            'plot_url': None  # No plot for simple version
        })
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

# For Vercel deployment
app.debug = True 