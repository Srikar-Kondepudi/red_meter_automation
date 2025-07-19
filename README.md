# Real-Time System Monitoring Dashboard

A powerful, real-time dashboard for monitoring system parameters with automated anomaly detection and trouble identification.

## 🚀 Features

- **Real-time Monitoring**: Live updates every 30 seconds with visual indicators
- **Wave Graph Visualization**: Beautiful charts showing DV values, pressure, and temperature trends
- **Automated Anomaly Detection**: Machine learning-based trouble detection
- **Professional Interface**: Modern, responsive design with status indicators
- **Live Alerts**: Real-time trouble alerts with actionable recommendations
- **Auto-refresh**: Continuous monitoring with countdown timers

## 📊 Dashboard Components

### Status Monitoring
- **System Status**: Green/Yellow/Red indicators with animated status bar
- **Live Updates**: Real-time countdown timer and update timestamps
- **Trouble Detection**: Automated detection of anomalies and system issues

### Data Visualization
- **DV Wave Graph**: Shows actual vs expected DV values with trouble points highlighted
- **Pressure & Temperature Graph**: Dual-axis visualization of system parameters
- **Status Panel**: Real-time system status with trouble counts and rates
- **Alerts Panel**: Live trouble alerts with specific recommendations

### Anomaly Detection
- **High Residual Detection**: Identifies data points exceeding ±2 standard deviations
- **Pressure Monitoring**: Detects low (<0.1) and high (>20) pressure values
- **Temperature Monitoring**: Identifies temperature outside 20-35°C range
- **DV Range Monitoring**: Flags extreme DV values (<-500 or >500)

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-learn (Linear Regression)
- **Visualization**: Matplotlib
- **Frontend**: HTML5, CSS3, JavaScript
- **Real-time Updates**: AJAX with JSON API

## 📁 Project Structure

```
red meters/
├── app.py                          # Main Flask application
├── templates/
│   └── dashboard.html             # Dashboard HTML template
├── requirements.txt               # Python dependencies
├── Procfile                      # Heroku deployment configuration
├── runtime.txt                   # Python version specification
├── June18-21_data.csv           # Sample data file
├── pressure_to_dv_correlation.csv # Correlation data
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd red-meters
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv dashboard_env
   source dashboard_env/bin/activate  # On Windows: dashboard_env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the dashboard**
   ```bash
   python3 app.py
   ```

5. **Access the dashboard**
   - Open your browser
   - Go to: `http://localhost:5000` (or the port shown in terminal)

## 🌐 Hosting Deployment

### Heroku Deployment
1. Create a Heroku account
2. Install Heroku CLI
3. Run these commands:
   ```bash
   heroku create your-app-name
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```

### Railway Deployment
1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Flask app
3. Deploy with one click

### Render Deployment
1. Connect your GitHub repository to Render
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `python app.py`

## 📈 Dashboard Features

### Real-time Monitoring
- **Live Status Bar**: Animated indicator showing active monitoring
- **Countdown Timer**: Shows time until next update
- **Blinking Indicators**: Visual cues for live activity
- **Auto-refresh**: Updates every 30 seconds automatically

### Data Analysis
- **Linear Regression Model**: Predicts expected DV values based on pressure and temperature
- **Residual Analysis**: Identifies anomalies using statistical methods
- **Threshold Monitoring**: Checks parameters against operational limits
- **Trend Visualization**: Shows historical patterns and current trends

### Alert System
- **Real-time Alerts**: Immediate notification of system issues
- **Categorized Troubles**: Different types of issues (pressure, temperature, DV, anomalies)
- **Actionable Recommendations**: Specific steps to resolve issues
- **Priority Indicators**: Color-coded alert severity

## 🔧 Configuration

### Environment Variables
- `PORT`: Server port (default: 5000)
- `FLASK_ENV`: Environment mode (development/production)

### Data Files
- Place your CSV data files in the project root
- Ensure columns: `Timestamp`, `Pressure`, `Temperature`, `DV`
- Data should be in chronological order

### Customization
- Modify threshold values in `app.py` for different sensitivity
- Adjust update frequency in `dashboard.html` JavaScript
- Customize colors and styling in the CSS section

## 📊 Data Requirements

### CSV Format
```csv
Timestamp,Pressure,Temperature,DV
2025-06-18 16:20:18,58.979,25.619,221.0
2025-06-18 16:20:19,50.408,25.625,161.0
```

### Data Quality
- Timestamps should be in ISO format
- Numerical values should be clean (no missing data)
- Sufficient data points for reliable analysis (recommended: 1000+ points)

## 🎯 Use Cases

### Industrial Monitoring
- Monitor manufacturing equipment parameters
- Detect equipment malfunctions early
- Track system performance over time

### Environmental Monitoring
- Track environmental sensor data
- Monitor climate control systems
- Detect environmental anomalies

### Quality Control
- Monitor production line parameters
- Detect quality issues in real-time
- Track process consistency

## 🔍 Troubleshooting

### Common Issues

**Dashboard not loading**
- Check if Flask app is running on correct port
- Verify all dependencies are installed
- Check browser console for JavaScript errors

**No data displayed**
- Ensure CSV file is in correct location
- Verify CSV format matches requirements
- Check file permissions

**Auto-refresh not working**
- Ensure JavaScript is enabled in browser
- Check browser console for errors
- Verify API endpoint is responding

### Performance Optimization
- Reduce update frequency for large datasets
- Implement data sampling for visualization
- Use production WSGI server for deployment

## 📝 API Endpoints

### GET /
- Main dashboard page
- Returns HTML dashboard interface

### GET /api/dashboard-data
- Returns JSON with dashboard data
- Includes plot image, status, and alerts
- Used for real-time updates

### GET /health
- Health check endpoint
- Returns system status and timestamp

## 🎨 Customization

### Styling
- Modify CSS in `templates/dashboard.html`
- Adjust colors, fonts, and layout
- Add custom animations and effects

### Functionality
- Add new anomaly detection rules in `app.py`
- Modify update frequency in JavaScript
- Add new visualization types

### Data Sources
- Connect to databases instead of CSV files
- Add real-time data streaming
- Implement data validation and cleaning

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the code comments
3. Test with sample data first
4. Verify all dependencies are installed

## 🔄 Updates

The dashboard automatically:
- Refreshes data every 30 seconds
- Updates visualizations in real-time
- Detects new anomalies continuously
- Provides live status indicators

---

**Real-Time System Monitoring Dashboard** - Professional monitoring solution with automated anomaly detection and live updates. 