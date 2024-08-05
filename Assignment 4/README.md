# Project Setup and Execution Guide

This guide provides step-by-step instructions for setting up and running the anomaly detection application, which consists of a Flask backend, a Kafka producer and consumer, and a React frontend. The application uses DuckDB for data storage and displays results and plots on a web interface.


## Prerequisites

Before you start, ensure you have the following installed:

* Python 3.x
* Node.js and npm
* Apache Kafka
* Required Python packages


## Step-by-Step Setup

### Step 1: Set Up Kafka

**Navigate to your Kafka installation directory and start ZooKeeper:**

bin/zookeeper-server-start.sh config/zookeeper.properties


**Start the Kafka Broker:**

bin/kafka-server-start.sh config/server.properties


**Create a Kafka topic named "spend_data":**

bin/kafka-topics.sh --create --topic spend_data --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1


### Step 2: Set Up Python Environment

**Navigate to the Project Directory:**

cd "path/to/Assignment"/src


**Install Python Dependencies:**

pip install Flask duckdb kafka-python pandas matplotlib keras_core scikit-learn joblib


### Step 3: Run Flask Backend

**Run the Flask Application:**

python app.py


### Step 4: Run Kafka Producer and Consumer

**Navigate to Producer Directory and Run:**

(assuming you are in the src directory under Assignment 4)
cd ../spend-analytics/src
python producer.py


**Navigate to Consumer Directory and Run:**

python consumer.py


### Step 5: Set Up React Frontend

**Install npm Dependencies:**

(assuming you are in the spend-analytics directory under Assignment 4)
npm install axios
npm start


### Step 6: Test the User Perspective

The application should now be running, and you can interact with it through the web interface, to perform an anomaly detection on the entered data and to then see the graph showcasing all the Anomalies, along with a popup that tells whether the entered data is an anomaly or not.

**Access the Application:**
Open your browser and navigate to http://localhost:3000


**Submit Data:**
Use the form to enter data, submit it, and observe the response. A popup should display whether the data is an anomaly


**View Plot:**
The page should display a plot showing the current dataset  with anomalies highlighted in red and normal data in blue.


## Troubleshooting

+ Kafka Errors: Ensure Kafka and ZooKeeper are running, and the topic is created correctly
+ Connection Issues: Check network settings if the application fails to connect between components
+ Dependency Errors: Ensure all dependencies are installed and up-to-date


## Notes

+ Model Training: The AnomalyDetect class is designed to train models using data from DuckDB each time the application is run
+ Model Loading: The model loading functionality is disabled for this assignment to focus on training from scratch. This can be re-enabled for future applications to improve efficiency, this has been cut off from the assignment since it shows less Database interaction
+ Data Plotting: The plot is dynamically updated based on the current dataset stored in DuckDB.
+ Multiple Screenshots showing the working of the application are provided in the screenshots folder
+ A video showcasing the working of the application is provided in the video folder
+ GitHub Repository has been updated with the updates I have done regarding the web application transformation of my work
+ The Database has been chosen for this project because of the speed and efficiency of an OLAP Database