#!/usr/bin/env python3
"""
FLASK APP WITH GRAPHS FOR VERCEL DEPLOYMENT
===========================================

A Flask application with beautiful wave graphs that works on Vercel.
"""

from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
import json
from datetime import datetime
import warnings
import os
warnings.filterwarnings('ignore')

# Set matplotlib config for serverless environment
os.environ['MPLCONFIGDIR'] = '/tmp'
plt.rcParams['figure.figsize'] = (16, 10)
plt.rcParams['font.size'] = 10

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
        
        # Simple trouble detection
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

def create_dashboard_plot(df, troubles):
    """Create the dashboard plot with beautiful wave graphs"""
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
            
            ax2.plot(timestamps, dv_values, color=colors['primary'], 
                    label='DV Values', linewidth=2, alpha=0.9)
            
            # Highlight trouble points
            if len(troubles) > 0:
                trouble_dvs = [t['dv'] for t in troubles[:20]]
                ax2.scatter(range(len(trouble_dvs)), trouble_dvs, color=colors['danger'], 
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
                if trouble['trouble_type'] == 'PRESSURE_ISSUE':
                    alert_text += f"🔴 Pressure issue: {trouble['pressure']:.2f}\n"
                elif trouble['trouble_type'] == 'TEMPERATURE_ISSUE':
                    alert_text += f"🟡 Temperature issue: {trouble['temperature']:.1f}°C\n"
                elif trouble['trouble_type'] == 'DV_EXTREME':
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
        df, troubles = load_and_process_data()
        
        if df is None:
            return jsonify({'error': 'Failed to load data'}), 500
        
        # Create dashboard plot
        plot_url, status, trouble_count, trouble_rate = create_dashboard_plot(df, troubles)
        
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