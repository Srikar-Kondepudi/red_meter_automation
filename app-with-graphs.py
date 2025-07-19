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
            # Use more data points for better wave visualization
            sample_size = min(500, len(df))
            sample_df = df.tail(sample_size).sort_values('Timestamp')
            
            # Create proper timestamps for x-axis
            timestamps = sample_df['Timestamp']
            dv_values = sample_df['DV'].values
            
            # Create smooth wave-like visualization with proper time labels
            ax2.plot(timestamps, dv_values, color=colors['primary'], 
                    label='DV', linewidth=2, alpha=0.9)
            
            # Anomaly detection and highlighting
            if len(troubles) > 0:
                # Find anomalies in the current sample
                anomaly_timestamps = []
                anomaly_values = []
                
                for trouble in troubles[:100]:  # Check more troubles
                    trouble_time = pd.to_datetime(trouble['timestamp'])
                    # Find if this trouble is in our sample
                    time_diff = abs(sample_df['Timestamp'] - trouble_time)
                    if time_diff.min() < pd.Timedelta(minutes=10):  # Within 10 minutes
                        closest_idx = time_diff.idxmin()
                        if closest_idx in sample_df.index:
                            anomaly_timestamps.append(sample_df.loc[closest_idx, 'Timestamp'])
                            anomaly_values.append(trouble['dv'])
                
                # Also detect statistical anomalies
                mean_dv = np.mean(dv_values)
                std_dv = np.std(dv_values)
                statistical_anomalies = np.where(np.abs(dv_values - mean_dv) > 2 * std_dv)[0]
                
                # Add statistical anomalies
                for idx in statistical_anomalies:
                    if idx < len(timestamps):
                        anomaly_timestamps.append(timestamps.iloc[idx])
                        anomaly_values.append(dv_values[idx])
                
                # Plot anomalies with proper timestamps
                if anomaly_timestamps and anomaly_values:
                    ax2.scatter(anomaly_timestamps, anomaly_values, 
                              color=colors['danger'], s=100, label='Anomaly', 
                              alpha=0.9, zorder=5, edgecolors='white', linewidth=1.5)
            
            # Improve graph styling for time series visualization
            ax2.set_title('DV Time Series with Anomalies', fontsize=14, fontweight='bold', pad=20)
            ax2.set_xlabel('Timestamp', fontsize=12, fontweight='bold')
            ax2.set_ylabel('DV', fontsize=12, fontweight='bold')
            ax2.legend(loc='upper right', framealpha=0.9)
            ax2.grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
            
            # Format x-axis timestamps
            ax2.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d %H'))
            plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
            
            # Set better y-axis limits for wave visualization
            y_min, y_max = dv_values.min(), dv_values.max()
            y_range = y_max - y_min
            ax2.set_ylim(y_min - y_range*0.15, y_max + y_range*0.15)
            
            # Add anomaly statistics with timing information
            if len(troubles) > 0:
                anomaly_count = len(anomaly_timestamps) if 'anomaly_timestamps' in locals() else 0
                # Find first and last anomaly times
                if anomaly_timestamps:
                    first_anomaly = min(anomaly_timestamps).strftime('%m-%d %H:%M')
                    last_anomaly = max(anomaly_timestamps).strftime('%m-%d %H:%M')
                    stats_text = f'Anomalies: {anomaly_count}\nFirst: {first_anomaly}\nLast: {last_anomaly}'
                else:
                    stats_text = f'Anomalies: {anomaly_count}\nNo timing data'
            else:
                stats_text = f'Anomalies: 0\nNo issues detected'
            
            ax2.text(0.02, 0.98, stats_text, transform=ax2.transAxes, 
                    fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        # 3. Pressure & Temperature Graph
        if len(df) > 0:
            ax3_twin = ax3.twinx()
            
            # Use the same sample data as DV graph for consistency
            pressure_values = sample_df['Pressure'].values
            temperature_values = sample_df['Temperature'].values
            
            # Create wave-like visualizations with proper timestamps
            line1 = ax3.plot(timestamps, pressure_values, 
                            color=colors['primary'], label='Pressure', 
                            linewidth=2, alpha=0.9)
            line2 = ax3_twin.plot(timestamps, temperature_values, 
                                 color=colors['danger'], label='Temperature', 
                                 linewidth=2, alpha=0.9)
            
            # Anomaly detection for pressure and temperature
            if len(troubles) > 0:
                p_anomaly_timestamps = []
                t_anomaly_timestamps = []
                
                for trouble in troubles[:100]:
                    if trouble['trouble_type'] in ['PRESSURE_ISSUE', 'TEMPERATURE_ISSUE']:
                        trouble_time = pd.to_datetime(trouble['timestamp'])
                        time_diff = abs(sample_df['Timestamp'] - trouble_time)
                        if time_diff.min() < pd.Timedelta(minutes=10):
                            closest_idx = time_diff.idxmin()
                            if closest_idx in sample_df.index:
                                if trouble['trouble_type'] == 'PRESSURE_ISSUE':
                                    p_anomaly_timestamps.append(sample_df.loc[closest_idx, 'Timestamp'])
                                else:
                                    t_anomaly_timestamps.append(sample_df.loc[closest_idx, 'Timestamp'])
                
                # Also detect statistical anomalies
                p_mean, p_std = np.mean(pressure_values), np.std(pressure_values)
                t_mean, t_std = np.mean(temperature_values), np.std(temperature_values)
                
                p_statistical = np.where(np.abs(pressure_values - p_mean) > 2 * p_std)[0]
                t_statistical = np.where(np.abs(temperature_values - t_mean) > 2 * t_std)[0]
                
                # Add statistical anomalies
                for idx in p_statistical:
                    if idx < len(timestamps):
                        p_anomaly_timestamps.append(timestamps.iloc[idx])
                
                for idx in t_statistical:
                    if idx < len(timestamps):
                        t_anomaly_timestamps.append(timestamps.iloc[idx])
                
                # Plot anomalies with proper timestamps
                if p_anomaly_timestamps:
                    p_anomaly_values = [pressure_values[timestamps == ts].iloc[0] if len(pressure_values[timestamps == ts]) > 0 else 0 
                                       for ts in p_anomaly_timestamps]
                    ax3.scatter(p_anomaly_timestamps, p_anomaly_values, 
                              color=colors['danger'], s=120, alpha=0.9, zorder=5,
                              edgecolors='white', linewidth=1.5)
                
                if t_anomaly_timestamps:
                    t_anomaly_values = [temperature_values[timestamps == ts].iloc[0] if len(temperature_values[timestamps == ts]) > 0 else 0 
                                       for ts in t_anomaly_timestamps]
                    ax3_twin.scatter(t_anomaly_timestamps, t_anomaly_values, 
                                   color=colors['danger'], s=120, alpha=0.9, zorder=5,
                                   edgecolors='white', linewidth=1.5)
            
            # Improve axis styling
            ax3.set_ylabel('Pressure', color=colors['primary'], fontweight='bold', fontsize=12)
            ax3_twin.set_ylabel('Temperature (°C)', color=colors['danger'], fontweight='bold', fontsize=12)
            ax3.tick_params(axis='y', labelcolor=colors['primary'])
            ax3_twin.tick_params(axis='y', labelcolor=colors['danger'])
            
            # Improve title and styling
            ax3.set_title('Pressure & Temperature Time Series', fontsize=14, fontweight='bold', pad=20)
            ax3.set_xlabel('Timestamp', fontsize=12, fontweight='bold')
            ax3.grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
            
            # Format x-axis timestamps
            ax3.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d %H'))
            plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')
            
            # Set better y-axis limits for wave visualization
            p_min, p_max = pressure_values.min(), pressure_values.max()
            p_range = p_max - p_min
            ax3.set_ylim(p_min - p_range*0.15, p_max + p_range*0.15)
            
            t_min, t_max = temperature_values.min(), temperature_values.max()
            t_range = t_max - t_min
            ax3_twin.set_ylim(t_min - t_range*0.15, t_max + t_range*0.15)
            
            # Combine legends
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax3.legend(lines, labels, loc='upper right', framealpha=0.9)
            
            # Add anomaly statistics with timing information
            p_anomaly_count = len(p_anomaly_timestamps) if 'p_anomaly_timestamps' in locals() else 0
            t_anomaly_count = len(t_anomaly_timestamps) if 't_anomaly_timestamps' in locals() else 0
            
            # Find first and last anomaly times
            if p_anomaly_timestamps:
                p_first = min(p_anomaly_timestamps).strftime('%m-%d %H:%M')
                p_last = max(p_anomaly_timestamps).strftime('%m-%d %H:%M')
                p_timing = f'P: {p_first} to {p_last}'
            else:
                p_timing = 'P: No anomalies'
            
            if t_anomaly_timestamps:
                t_first = min(t_anomaly_timestamps).strftime('%m-%d %H:%M')
                t_last = max(t_anomaly_timestamps).strftime('%m-%d %H:%M')
                t_timing = f'T: {t_first} to {t_last}'
            else:
                t_timing = 'T: No anomalies'
            
            stats_text = f'P Anomalies: {p_anomaly_count}\nT Anomalies: {t_anomaly_count}\n{p_timing}\n{t_timing}'
            ax3.text(0.02, 0.98, stats_text, transform=ax3.transAxes, 
                    fontsize=9, verticalalignment='top',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
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