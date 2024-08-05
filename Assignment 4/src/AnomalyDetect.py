import keras_core
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from keras_core.models import Model
from keras_core.layers import Input, Dense
from sklearn.model_selection import train_test_split
import joblib
import os
import duckdb
import warnings
warnings.filterwarnings('ignore')

class AnomalyDetect:
    def __init__(self, duckdb_path=None, model_path='anomaly_detector'):
        self.model_path = model_path
        if duckdb_path is not None:
            self.data = self._load_data_from_duckdb(duckdb_path)
            self._preprocess_data()
            self._train_models()
            self._save_models()
        # Commented out model loading to focus on training from scratch
        # else:
        #     self._load_models()

    def _load_data_from_duckdb(self, duckdb_path):
        con = duckdb.connect(database=duckdb_path, read_only=False)

        data = con.execute("SELECT * FROM spend_data")

        con.close()
        # print(f"Data loaded from DuckDB: {data.shape[0]} rows, {data.shape[1]} columns")
        # print(data.head())
        return data

    def _preprocess_data(self):
        self.data['Changed_On'] = pd.to_datetime(self.data['Changed_On'])

        self.data.set_index('Changed_On', inplace=True)
        self.monthly_data = self.data.resample('ME').sum()

        self.scaler = StandardScaler()
        self.scaled_data = self.scaler.fit_transform(self.monthly_data[['Net_Value', 'PO_Quantity']])

    def _train_models(self):
        # Increased the contamination for better accuracy
        self.iso_forest = IsolationForest(contamination=0.05, random_state=42)
        self.iso_forest.fit(self.scaled_data)
        self.monthly_data['anomaly_iso'] = self.iso_forest.predict(self.scaled_data)
        self.monthly_data['anomaly_iso'] = self.monthly_data['anomaly_iso'].map({1: 0, -1: 1})

        input_dim = self.scaled_data.shape[1]
        encoding_dim = 2
        input_layer = Input(shape=(input_dim,))
        encoder = Dense(encoding_dim, activation="relu")(input_layer)
        decoder = Dense(input_dim, activation="sigmoid")(encoder)
        self.autoencoder = Model(inputs=input_layer, outputs=decoder)
        self.autoencoder.compile(optimizer='adam', loss='mean_squared_error')

        X_train, X_test = train_test_split(self.scaled_data, test_size=0.2, random_state=42)
        self.autoencoder.fit(X_train, X_train, epochs=50, batch_size=256, shuffle=True, validation_data=(X_test, X_test), verbose=0)

        X_pred = self.autoencoder.predict(self.scaled_data)
        mse = np.mean(np.power(self.scaled_data - X_pred, 2), axis=1)
        self.threshold = np.percentile(mse, 95)
        self.monthly_data['anomaly_ae'] = [1 if e > self.threshold else 0 for e in mse]

        self.monthly_data['iso_forest_score'] = -self.iso_forest.decision_function(self.scaled_data)
        self.monthly_data['ae_score'] = mse

    def predict(self, json_data):
        new_data = pd.DataFrame([json_data])

        new_data['Changed_On'] = pd.to_datetime(new_data['Changed_On'])

        new_data.set_index('Changed_On', inplace=True)
        new_data = new_data.resample('ME').sum()

        new_data.columns = ['Net_Value', 'PO_Quantity', 'Category']

        print(new_data.head())

        scaled_new_data = self.scaler.transform(new_data[['Net_Value', 'PO_Quantity']])

        iso_forest_prediction = self.iso_forest.predict(scaled_new_data)
        iso_forest_score = -self.iso_forest.decision_function(scaled_new_data)

        new_data_pred = self.autoencoder.predict(scaled_new_data)
        mse_new_data = np.mean(np.power(scaled_new_data - new_data_pred, 2), axis=1)

        anomaly_iso = iso_forest_prediction[0] == -1
        anomaly_ae = mse_new_data[0] > self.threshold

        combined_score = (iso_forest_score[0] + mse_new_data[0]) / 2

        return {
            "is_anomaly": anomaly_iso or anomaly_ae,
            "confidence_score": combined_score
        }

    def _save_models(self):
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)

        joblib.dump(self.scaler, os.path.join(self.model_path, 'scaler.pkl'))
        joblib.dump(self.iso_forest, os.path.join(self.model_path, 'iso_forest.pkl'))
        self.autoencoder.save(os.path.join(self.model_path, 'autoencoder.h5'))
        with open(os.path.join(self.model_path, 'threshold.txt'), 'w') as f:
            f.write(str(self.threshold))

# Commented out to better focus on the training process instead of the loading process (better database functionality that way)
    # def _load_models(self):
    #     self.scaler = joblib.load(os.path.join(self.model_path, 'scaler.pkl'))
    #     self.iso_forest = joblib.load(os.path.join(self.model_path, 'iso_forest.pkl'))
    #     self.autoencoder = keras_core.models.load_model(os.path.join(self.model_path, 'autoencoder.h5'))
    #     with open(os.path.join(self.model_path, 'threshold.txt'), 'r') as f:
    #         self.threshold = float(f.read())

if __name__ == "__main__":
    duckdb_path = 'spend_data.duckdb'
    detector = AnomalyDetect(duckdb_path)

    json_data = {
        "Changed_On": "2021-06-01",
        "Net_Value": 50,
        "PO_Quantity": 100,
        "Category": "64"
    }

    result = detector.predict(json_data)
    print(result)