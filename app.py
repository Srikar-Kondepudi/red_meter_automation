#!/usr/bin/env python3
"""
FLASK APP FOR DASHBOARD HOSTING
===============================

A Flask application to host the dashboard on web platforms.
Compatible with Heroku, Railway, Render, and other hosting services.

Usage:
    python app.py
"""

from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import io
import base64
from sklearn.linear_model import LinearRegression
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
        
        # Train model
        X = df[['Pressure', 'Temperature']]
        y = df['DV']
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Calculate residuals
        df['DV_predicted'] = model.predict(X)
        df['Residual'] = df['DV'] - df['DV_predicted']
        residual_std = df['Residual'].std()
        
        return df, model, residual_std
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None, None

def detect_troubles(df, residual_std):
    """Detect troubles in the data"""
    troubles = []
    
    for _, row in df.iterrows():
        # Detect trouble indicators
        pressure = row['Pressure']
        temperature = row['Temperature']
        dv = row['DV']
        residual = row['Residual']
        
        # Check for trouble
        has_trouble = False
        trouble_type = "NORMAL"
        
        # High residual
        if abs(residual) > 2 * residual_std:
            has_trouble = True
            trouble_type = "HIGH_ANOMALY"
        
        # Pressure issues
        elif pressure < 0.1:
            has_trouble = True
            trouble_type = "LOW_PRESSURE"
        elif pressure > 20:
            has_trouble = True
            trouble_type = "HIGH_PRESSURE"
        
        # Temperature issues
        elif temperature < 20:
            has_trouble = True
            trouble_type = "LOW_TEMPERATURE"
        elif temperature > 35:
            has_trouble = True
            trouble_type = "HIGH_TEMPERATURE"
        
        # DV range issues
        elif dv < -500 or dv > 500:
            has_trouble = True
            trouble_type = "EXTREME_DV"
        
        if has_trouble:
            troubles.append({
                'timestamp': row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'pressure': pressure,
                'temperature': temperature,
                'dv': dv,
                'trouble_type': trouble_type
            })
    
    return troubles

def create_dashboard_plot(df, troubles):
    """Create the dashboard plot"""
    try:
        # Create figure
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle('REAL-TIME SYSTEM MONITORING DASHBOARD', 
                     fontsize=16, fontweight='bold')
        
        # Colors
        colors = {
            'normal': '#27ae60',
            'warning': '#f39c12', 
            'danger': '#e74c3c',
            'primary': '#3498db',
            'success': '#2ecc71'
        }
        
        # Determine status
        trouble_count = len(troubles)
        total_count = len(df)
        trouble_rate = (trouble_count / total_count * 100) if total_count > 0 else 0
        
        if trouble_count == 0:
            status = "NORMAL"
            status_color = colors['success']
            status_icon = "✅"
        elif trouble_count <= 50:
            status = "ATTENTION"
            status_color = colors['warning']
            status_icon = "⚠️"
        else:
            status = "TROUBLE"
            status_color = colors['danger']
            status_icon = "🚨"
        
        # 1. Status Panel
        ax1.set_facecolor(status_color)
        ax1.text(0.5, 0.5, f"{status_icon}\n{status}\nTroubles: {trouble_count}\nRate: {trouble_rate:.1f}%", 
                transform=ax1.transAxes, fontsize=16, fontweight='bold', 
                ha='center', va='center', color='white')
        ax1.set_title('SYSTEM STATUS', fontsize=14, fontweight='bold')
        ax1.axis('off')
        
        # 2. DV Wave Graph
        if len(df) > 0:
            # Sample data for visualization
            sample_size = min(200, len(df))
            sample_df = df.sample(n=sample_size, random_state=42).sort_values('Timestamp')
            
            timestamps = sample_df['Timestamp']
            dv_values = sample_df['DV']
            predicted_values = sample_df['DV_predicted']
            
            ax2.plot(timestamps, dv_values, color=colors['primary'], 
                    label='Actual DV', linewidth=2, alpha=0.9)
            ax2.plot(timestamps, predicted_values, color=colors['success'], 
                    label='Expected DV', linewidth=2, linestyle='--', alpha=0.8)
            
            # Highlight trouble points
            trouble_timestamps = [t['timestamp'] for t in troubles[:20]]  # Show first 20
            if trouble_timestamps:
                trouble_dvs = [t['dv'] for t in troubles[:20]]
                ax2.scatter(trouble_timestamps, trouble_dvs, color=colors['danger'], 
                          s=100, label='Trouble Detected', alpha=0.9, zorder=5)
            
            ax2.set_title('DV Values Wave Graph', fontsize=12, fontweight='bold')
            ax2.set_xlabel('Time')
            ax2.set_ylabel('DV Value')
            ax2.legend(loc='upper left')
            ax2.grid(True, alpha=0.3)
            plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
        
        # 3. Pressure & Temperature Graph
        if len(df) > 0:
            ax3_twin = ax3.twinx()
            
            line1 = ax3.plot(timestamps, sample_df['Pressure'], 
                            color=colors['primary'], label='Pressure', linewidth=2, alpha=0.9)
            line2 = ax3_twin.plot(timestamps, sample_df['Temperature'], 
                                 color=colors['danger'], label='Temperature', linewidth=2, alpha=0.9)
            
            ax3.set_ylabel('Pressure', color=colors['primary'], fontweight='bold')
            ax3_twin.set_ylabel('Temperature (°C)', color=colors['danger'], fontweight='bold')
            ax3.tick_params(axis='y', labelcolor=colors['primary'])
            ax3_twin.tick_params(axis='y', labelcolor=colors['danger'])
            
            ax3.set_title('Pressure & Temperature Wave Graph', fontsize=12, fontweight='bold')
            ax3.set_xlabel('Time')
            ax3.grid(True, alpha=0.3)
            
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax3.legend(lines, labels, loc='upper left')
            plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')
        
        # 4. Alerts Panel
        if trouble_count == 0:
            alert_text = "✅ NO ACTIVE ALERTS\n\nSystem operating normally"
        else:
            # Generate alerts
            alert_text = "🚨 ACTIVE ALERTS:\n\n"
            for trouble in troubles[:5]:  # Show first 5
                if trouble['trouble_type'] == 'HIGH_ANOMALY':
                    alert_text += f"🔴 DV anomaly detected\n"
                elif trouble['trouble_type'] == 'LOW_PRESSURE':
                    alert_text += f"🟡 Low pressure: {trouble['pressure']:.2f}\n"
                elif trouble['trouble_type'] == 'HIGH_PRESSURE':
                    alert_text += f"🔴 High pressure: {trouble['pressure']:.2f}\n"
                elif trouble['trouble_type'] == 'LOW_TEMPERATURE':
                    alert_text += f"🟡 Low temperature: {trouble['temperature']:.1f}°C\n"
                elif trouble['trouble_type'] == 'HIGH_TEMPERATURE':
                    alert_text += f"🔴 High temperature: {trouble['temperature']:.1f}°C\n"
                elif trouble['trouble_type'] == 'EXTREME_DV':
                    alert_text += f"🔴 Extreme DV value: {trouble['dv']:.1f}\n"
            
            # Add recommendations
            alert_text += "\n🔧 RECOMMENDED ACTIONS:\n"
            alert_text += "• Check sensor readings\n"
            alert_text += "• Monitor system parameters\n"
            alert_text += "• Review recent changes\n"
        
        ax4.text(0.05, 0.95, alert_text, transform=ax4.transAxes, fontsize=10,
                va='top', bbox=dict(boxstyle="round,pad=0.3", 
                facecolor=colors['danger'] if trouble_count > 0 else colors['success'], alpha=0.7))
        ax4.set_title('ALERTS & RECOMMENDATIONS', fontsize=12, fontweight='bold')
        ax4.axis('off')
        
        # Save plot to base64 string
        plt.tight_layout()
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=150, bbox_inches='tight')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close()
        
        return plot_url, status, trouble_count, trouble_rate
        
    except Exception as e:
        print(f"Error creating plot: {e}")
        return None, "ERROR", 0, 0.0

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/dashboard-data')
def get_dashboard_data():
    """API endpoint to get dashboard data"""
    try:
        # Load and process data
        df, model, residual_std = load_and_process_data()
        
        if df is None:
            return jsonify({'error': 'Failed to load data'}), 500
        
        # Detect troubles
        troubles = detect_troubles(df, residual_std)
        
        # Create dashboard plot
        plot_url, status, trouble_count, trouble_rate = create_dashboard_plot(df, troubles)
        
        if plot_url is None:
            return jsonify({'error': 'Failed to create plot'}), 500
        
        # Update global data
        dashboard_data.update({
            'status': status,
            'trouble_count': trouble_count,
            'total_count': len(df),
            'trouble_rate': trouble_rate,
            'alerts': troubles[:10],  # Show first 10 alerts
            'plot_url': plot_url
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