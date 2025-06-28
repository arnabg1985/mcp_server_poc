from flask import Flask, request, jsonify
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Load your log data
CSV_FILE = "financial_application_logs.csv"
df = pd.read_csv(CSV_FILE, parse_dates=['date'])

def filter_logs(params):
    filtered = df
    # Filter by application name
    if "app_name" in params:
        filtered = filtered[filtered['application_name'] == params["app_name"]]
    # Filter by log level
    if "log_level" in params:
        filtered = filtered[filtered['log_level'] == params["log_level"]]
    # Filter by server name
    if "server" in params:
        filtered = filtered[filtered['servernames'] == params["server"]]
    # Filter by severity
    if "severity" in params:
        filtered = filtered[filtered['severity'] == params["severity"]]
    # Filter by date range
    if "start_date" in params:
        filtered = filtered[filtered['date'] >= params["start_date"]]
    if "end_date" in params:
        filtered = filtered[filtered['date'] <= params["end_date"]]
    # Filter by time range (optional)
    if "start_time" in params:
        filtered = filtered[filtered['time_stamp'] >= params["start_time"]]
    if "end_time" in params:
        filtered = filtered[filtered['time_stamp'] <= params["end_time"]]
    return filtered

@app.route('/logs', methods=['GET'])
def query_logs():
    """
    Query params supported:
    app_name, log_level, server, severity, start_date, end_date, start_time, end_time, limit
    Dates in YYYY-MM-DD, time in HH:MM:SS
    Example: /logs?app_name=StockTraderPro&log_level=exception&start_date=2025-06-01&end_date=2025-06-10
    """
    params = {}
    for key in ['app_name', 'log_level', 'server', 'severity', 'start_date', 'end_date', 'start_time', 'end_time']:
        if key in request.args:
            params[key] = request.args.get(key)
    try:
        # Convert dates/times if present
        if 'start_date' in params:
            params['start_date'] = pd.to_datetime(params['start_date'])
        if 'end_date' in params:
            params['end_date'] = pd.to_datetime(params['end_date'])
    except Exception as e:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    filtered = filter_logs(params)
    # limit results if specified
    limit = int(request.args.get('limit', 100))
    result = filtered.head(limit).to_dict(orient="records")
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)