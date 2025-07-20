from flask import Flask, render_template, jsonify
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import base64
import io
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Production configuration
app.config['ENV'] = 'production'
app.config['DEBUG'] = False
app.config['TESTING'] = False

# Color scheme for professional dashboard
colors = {
    'primary': '#2E86AB',
    'secondary': '#A23B72', 
    'success': '#F18F01',
    'danger': '#C73E1D',
    'warning': '#F4A261',
    'info': '#264653',
    'light': '#F8F9FA',
    'dark': '#212529'
}

def load_data():
    """Load and process data for the dashboard"""
    try:
        # Load main data
        df = pd.read_csv('June18-21_data.csv')
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        return df, pd.DataFrame()
    except Exception as e:
        print(f"Error loading data: {e}")
        # Return sample data if files not found
        dates = pd.date_range(start='2024-06-18', end='2024-06-21', freq='H')
        sample_data = {
            'Timestamp': dates,
            'DV': np.random.normal(0, 100, len(dates)),
            'Pressure': np.random.normal(50, 10, len(dates)),
            'Temperature': np.random.normal(30, 2, len(dates))
        }
        df = pd.DataFrame(sample_data)
        return df, pd.DataFrame()

def generate_troubles():
    """Generate realistic trouble data for demonstration"""
    troubles = []
    base_time = datetime.now() - timedelta(hours=24)
    
    # Generate various types of troubles
    trouble_types = ['DV_ANOMALY', 'PRESSURE_ISSUE', 'TEMPERATURE_ISSUE', 'SYSTEM_ERROR']
    
    for i in range(15):
        trouble_time = base_time + timedelta(hours=i*1.5)
        trouble_type = trouble_types[i % len(trouble_types)]
        
        if trouble_type == 'DV_ANOMALY':
            dv_value = np.random.uniform(-300, 300)
        elif trouble_type == 'PRESSURE_ISSUE':
            dv_value = np.random.uniform(50, 150)
        elif trouble_type == 'TEMPERATURE_ISSUE':
            dv_value = np.random.uniform(20, 80)
        else:
            dv_value = np.random.uniform(-200, 200)
        
        troubles.append({
            'timestamp': trouble_time.strftime('%Y-%m-%d %H:%M:%S'),
            'trouble_type': trouble_type,
            'dv': dv_value,
            'severity': np.random.choice(['LOW', 'MEDIUM', 'HIGH'])
        })
    
    return troubles

def create_dashboard_graphs():
    """Create professional dashboard graphs with proper timestamps"""
    df, correlation_df = load_data()
    troubles = generate_troubles()
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Red Meters Real-Time Monitoring Dashboard', fontsize=20, fontweight='bold', y=0.95)
    
    # 1. System Status Overview
    status_data = {
        'Operational': len([t for t in troubles if t['severity'] == 'LOW']),
        'Warning': len([t for t in troubles if t['severity'] == 'MEDIUM']),
        'Critical': len([t for t in troubles if t['severity'] == 'HIGH'])
    }
    
    colors_status = [colors['success'], colors['warning'], colors['danger']]
    wedges, texts, autotexts = ax1.pie(status_data.values(), labels=status_data.keys(), 
                                       colors=colors_status, autopct='%1.1f%%', startangle=90)
    ax1.set_title('System Status Overview', fontsize=14, fontweight='bold', pad=20)
    
    # 2. DV Time Series with Anomalies
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
        
        # Simple anomaly detection without complex indexing
        if len(troubles) > 0:
            # Find anomalies in the current sample
            anomaly_timestamps = []
            anomaly_values = []
            
            for trouble in troubles[:20]:  # Check fewer troubles
                trouble_time = pd.to_datetime(trouble['timestamp'])
                # Find if this trouble is in our sample
                time_diff = abs(sample_df['Timestamp'] - trouble_time)
                if time_diff.min() < pd.Timedelta(minutes=10):  # Within 10 minutes
                    closest_idx = time_diff.idxmin()
                    if closest_idx in sample_df.index:
                        anomaly_timestamps.append(sample_df.loc[closest_idx, 'Timestamp'])
                        anomaly_values.append(trouble['dv'])
            
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
        
        # Simple anomaly detection for pressure and temperature
        if len(troubles) > 0:
            p_anomaly_timestamps = []
            t_anomaly_timestamps = []
            
            for trouble in troubles[:20]:
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
            
            # Plot anomalies with proper timestamps
            if p_anomaly_timestamps:
                # Simple approach - just use the first few anomalies
                p_anomaly_values = [pressure_values[0]] * len(p_anomaly_timestamps)
                ax3.scatter(p_anomaly_timestamps, p_anomaly_values, 
                          color=colors['danger'], s=120, alpha=0.9, zorder=5,
                          edgecolors='white', linewidth=1.5)
            
            if t_anomaly_timestamps:
                # Simple approach - just use the first few anomalies
                t_anomaly_values = [temperature_values[0]] * len(t_anomaly_timestamps)
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
    
    # 4. Recent Troubles Table
    if len(troubles) > 0:
        recent_troubles = troubles[-10:]  # Last 10 troubles
        
        # Create table data
        table_data = []
        for trouble in recent_troubles:
            table_data.append([
                trouble['timestamp'][:16],  # Format: YYYY-MM-DD HH:MM
                trouble['trouble_type'],
                f"{trouble['dv']:.1f}",
                trouble['severity']
            ])
        
        # Create table
        table = ax4.table(cellText=table_data,
                         colLabels=['Time', 'Type', 'DV Value', 'Severity'],
                         cellLoc='center',
                         loc='center',
                         bbox=[0, 0, 1, 1])
        
        # Style the table
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Color code severity
        for i, row in enumerate(table_data):
            severity = row[3]
            if severity == 'HIGH':
                color = colors['danger']
            elif severity == 'MEDIUM':
                color = colors['warning']
            else:
                color = colors['success']
            
            for j in range(4):
                table[(i+1, j)].set_facecolor(color)
                table[(i+1, j)].set_text_props(weight='bold', color='white')
        
        # Style header
        for j in range(4):
            table[(0, j)].set_facecolor(colors['dark'])
            table[(0, j)].set_text_props(weight='bold', color='white')
        
        ax4.set_title('Recent Troubles', fontsize=14, fontweight='bold', pad=20)
        ax4.axis('off')
    
    # Adjust layout
    plt.tight_layout()
    
    # Convert to base64
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    img_buffer.seek(0)
    img_data = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()
    
    return img_data

@app.route('/')
def dashboard():
    """Main dashboard route"""
    return render_template('dashboard.html')

@app.route('/api/dashboard-data')
def dashboard_data():
    """API endpoint for dashboard data"""
    try:
        df, correlation_df = load_data()
        troubles = generate_troubles()
        
        # Generate graphs
        graph_data = create_dashboard_graphs()
        
        # Calculate statistics
        if len(df) > 0:
            total_readings = len(df)
            avg_dv = df['DV'].mean()
            avg_pressure = df['Pressure'].mean()
            avg_temperature = df['Temperature'].mean()
            
            # Count troubles by type
            trouble_counts = {}
            for trouble in troubles:
                trouble_type = trouble['trouble_type']
                trouble_counts[trouble_type] = trouble_counts.get(trouble_type, 0) + 1
        else:
            total_readings = 0
            avg_dv = 0
            avg_pressure = 0
            avg_temperature = 0
            trouble_counts = {}
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_readings': total_readings,
                'avg_dv': round(avg_dv, 2),
                'avg_pressure': round(avg_pressure, 2),
                'avg_temperature': round(avg_temperature, 2),
                'trouble_counts': trouble_counts,
                'recent_troubles': troubles[-5:],  # Last 5 troubles
                'graph_data': graph_data
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=127, debug=False) 