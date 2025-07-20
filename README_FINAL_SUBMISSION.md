# 🚀 Real-Time System Monitoring Dashboard - FINAL SUBMISSION

## 📋 Project Overview

This is a **production-ready real-time monitoring dashboard** for Red Meters automation system. The dashboard provides live monitoring of system parameters with advanced anomaly detection and wave pattern visualization.

## ✨ Key Features

### 🎯 **Core Functionality**
- **Real-time Data Visualization**: Live monitoring of DV, Pressure, and Temperature
- **Anomaly Detection**: Advanced statistical and rule-based anomaly detection
- **Wave Pattern Analysis**: Professional time-series graphs with proper timestamps
- **Error Timing Information**: Shows when anomalies started and ended
- **Auto-refresh**: Dashboard updates every 30 seconds automatically

### 📊 **Dashboard Components**
1. **System Status Overview**: Pie chart showing operational status
2. **DV Time Series with Anomalies**: Wave graph with proper timestamps (MM-DD HH format)
3. **Pressure & Temperature Time Series**: Dual-axis wave visualization
4. **Recent Troubles Table**: Color-coded severity indicators

### 🎨 **Visual Design**
- **Google Colab Style**: Matches professional data visualization standards
- **Proper Timestamps**: X-axis shows actual dates like "06-18 12" to "06-23 00"
- **Anomaly Highlighting**: Red dots marking detected issues
- **Professional Color Scheme**: Blue for data, red for alerts, green for success

## 🚀 **Deployment Status**

### ✅ **Local Production Server**
- **Port**: 127 (as requested)
- **Status**: ✅ **RUNNING**
- **URL**: http://127.0.0.1:127
- **Environment**: Production mode with error handling

### ✅ **Vercel Deployment**
- **Status**: ✅ **READY FOR DEPLOYMENT**
- **Configuration**: Updated `vercel.json` for production app
- **Entry Point**: `production-app.py`

## 📁 **File Structure**

```
red meters/
├── production-app.py          # 🎯 FINAL PRODUCTION VERSION
├── app-with-graphs.py        # Enhanced version with Google Colab style
├── vercel.json               # Vercel deployment configuration
├── requirements.txt           # Python dependencies
├── templates/
│   └── dashboard.html        # Dashboard UI template
├── June18-21_data.csv        # Main data file
├── pressure_to_dv_correlation.csv
└── README_FINAL_SUBMISSION.md # This file
```

## 🛠️ **Installation & Setup**

### **Local Development**
```bash
# 1. Clone the repository
git clone https://github.com/Srikar-Kondepudi/red_meter_automation.git
cd red_meter_automation

# 2. Create virtual environment
python3 -m venv dashboard_env
source dashboard_env/bin/activate  # On macOS/Linux
# or
dashboard_env\Scripts\activate     # On Windows

# 3. Install dependencies
pip install flask pandas numpy matplotlib

# 4. Run the production server
python3 production-app.py
```

### **Access the Dashboard**
- **Local URL**: http://127.0.0.1:127
- **Network URL**: http://10.119.185.113:127

## 🌐 **Vercel Deployment**

### **Automatic Deployment**
The project is configured for automatic deployment on Vercel:

1. **Connect GitHub**: Link your GitHub repository to Vercel
2. **Auto-deploy**: Every push to `main` branch triggers deployment
3. **Production URL**: Will be provided by Vercel after deployment

### **Manual Deployment**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from project directory
vercel --prod
```

## 📊 **Dashboard Features**

### **Real-Time Monitoring**
- **Auto-refresh**: Every 30 seconds
- **Live Updates**: Shows last update time and countdown
- **Error Handling**: Graceful fallback for missing data

### **Anomaly Detection**
- **Statistical Analysis**: 2-sigma deviation detection
- **Rule-based Detection**: Pressure and temperature thresholds
- **Timing Information**: Shows when errors started and ended

### **Data Visualization**
- **Wave Patterns**: Smooth time-series visualization
- **Proper Timestamps**: MM-DD HH format on X-axis
- **Anomaly Markers**: Red dots highlighting issues
- **Professional Styling**: Clean, modern interface

## 🔧 **Technical Specifications**

### **Backend (Flask)**
- **Framework**: Flask 3.1.1
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib with Agg backend
- **API Endpoints**: `/` (dashboard), `/api/dashboard-data` (JSON data)

### **Frontend (HTML/CSS/JavaScript)**
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: JavaScript fetch API
- **Professional UI**: Modern gradient background
- **Auto-refresh**: 30-second intervals

### **Data Sources**
- **Primary**: `June18-21_data.csv` (real sensor data)
- **Correlation**: `pressure_to_dv_correlation.csv`
- **Fallback**: Generated sample data if files missing

## 📈 **Performance Metrics**

### **System Status**
- **Total Data Points**: 129,530+ readings
- **Troubles Detected**: Real-time anomaly count
- **Trouble Rate**: Percentage of anomalies
- **System Status**: Operational/Warning/Critical

### **Anomaly Detection**
- **DV Anomalies**: Statistical and rule-based detection
- **Pressure Issues**: High-pressure alerts
- **Temperature Issues**: Temperature threshold violations
- **Timing Information**: First and last anomaly times

## 🎯 **Submission Ready**

### ✅ **What's Complete**
1. **Production Server**: Running on port 127 ✅
2. **Google Colab Style**: Proper timestamps and wave graphs ✅
3. **Anomaly Detection**: Statistical and timing information ✅
4. **Error Handling**: Graceful fallbacks for missing data ✅
5. **Vercel Deployment**: Configuration ready ✅
6. **Documentation**: Comprehensive README ✅

### 🚀 **Ready for Submission**
- **Local Testing**: ✅ Working on http://127.0.0.1:127
- **GitHub Repository**: ✅ Updated with final version
- **Deployment Files**: ✅ All configuration files ready
- **Documentation**: ✅ Complete setup and usage guide

## 📞 **Support & Contact**

### **For Submission**
- **Repository**: https://github.com/Srikar-Kondepudi/red_meter_automation
- **Local Access**: http://127.0.0.1:127 (when running)
- **Vercel URL**: Will be provided after deployment

### **Technical Support**
- **Error Handling**: App includes comprehensive error handling
- **Data Fallback**: Generates sample data if files missing
- **Production Ready**: Configured for deployment

---

## 🎉 **FINAL STATUS: READY FOR SUBMISSION**

**✅ Production Dashboard Running on Port 127**  
**✅ Google Colab Style Wave Graphs with Timestamps**  
**✅ Advanced Anomaly Detection with Timing Information**  
**✅ Vercel Deployment Configuration Ready**  
**✅ Comprehensive Documentation Complete**

**🚀 Your Real-Time System Monitoring Dashboard is ready for submission today!** 