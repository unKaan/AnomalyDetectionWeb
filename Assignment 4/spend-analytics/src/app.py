from kafka import KafkaConsumer
import json
import duckdb
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import matplotlib.pyplot as plt
import io
import sys

sys.path.append('../../src')
from src import AnomalyDetect


app = Flask(__name__)
CORS(app)
consumer = KafkaConsumer('spend_data', bootstrap_servers='localhost:9092',api_version=(3,7,1), value_deserializer=lambda m: json.loads(m.decode('utf-8')),    metadata_max_age_ms=30000,
                         request_timeout_ms=30000)


duckdb.sql('''
CREATE TABLE IF NOT EXISTS spend_data (
    Key INT PRIMARY KEY,
    Changed_On DATE,
    PO_Quantity FLOAT,
    Net_Value FLOAT,
    Category VARCHAR,
    Net_Price FLOAT,
    risk_flag BOOLEAN
)
''')
duckdb.sql("CREATE SEQUENCE IF NOT EXISTS purchase START 1")

# Delete  afterwards
# def AnomalyDetect(data):
#     return data['Net_Value'] > 10000

@app.route('/submit', methods=['POST'])
def submit_data():
    data = request.json
    try:
        net_value = float(data['Net_Value'])
        po_quantity = float(data['PO_Quantity'])
        data['Net_Price'] = net_value / po_quantity

    except ValueError as e:
        return jsonify({"status": "error", "message": "Invalid input type for numeric fields."}), 400

    risk_flag = AnomalyDetect(data)
    data['risk_flag'] = risk_flag

    query = f"""
    INSERT INTO spend_data (Key, Changed_On, PO_Quantity, Net_Value, Category, Net_Price, risk_flag)
    VALUES (nextval('purchase'), '{data['Changed_On']}', {data['PO_Quantity']}, {data['Net_Value']}, '{data['Category']}', {data['Net_Price']}, {data['risk_flag']})
    """
    duckdb.sql(query)

    return jsonify({"status": "success", "risk_flag": risk_flag})


@app.route('/plot')
def plot_data():
    duckdb_path = 'spend_data.duckdb'
    con = duckdb.connect(database=duckdb_path, read_only=False)

    df = con.execute("SELECT Net_Value, PO_Quantity, risk_flag FROM spend_data")
    con.close

    fig, ax = plt.subplots()
    ax.scatter(df['Net_Value'], df['PO_Quantity'], c=df['risk_flag'].map({0: 'blue', 1: 'red'}), label='Data Points')
    ax.set_xlabel('Net Value')
    ax.set_ylabel('PO Quantity')
    ax.set_title('Anomaly Detection Scatter Plot')
    ax.legend()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return send_file(img, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)

