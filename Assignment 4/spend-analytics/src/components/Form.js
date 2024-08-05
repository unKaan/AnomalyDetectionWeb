import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Form = () => {
  const [data, setData] = useState({
    Changed_On: '',
    PO_Quantity: '',
    Net_Value: '',
    Category: ''
  });
  const [message, setMessage] = useState('');
  const [plotUrl, setPlotUrl] = useState('');

  const handleChange = (e) => {
    setData({ ...data, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5000/submit', data);
      const { risk_flag } = response.data;
      if (risk_flag) {
        setMessage('Anomaly detected! Negative popup');
      } else {
        setMessage('No anomalies detected! Positive popup');
      }
      setData({
        Changed_On: '',
        PO_Quantity: '',
        Net_Value: '',
        Category: ''
      });

      // Refresh plot
      fetchPlot();

    } catch (error) {
      console.error(error);
    }
  };

  const fetchPlot = async () => {
    try {
      const response = await axios.get('http://localhost:5000/plot', { responseType: 'blob' });
      setPlotUrl(URL.createObjectURL(response.data));
    } catch (error) {
      console.error('Error fetching the plot:', error);
    }
  };

  useEffect(() => {
    fetchPlot();
  }, []);

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input type="date" name="Changed_On" placeholder="Changed On" onChange={handleChange} value={data.Changed_On} required />
        <input type="number" name="PO_Quantity" placeholder="PO Quantity" onChange={handleChange} value={data.PO_Quantity} required />
        <input type="number" name="Net_Value" placeholder="Net Value" onChange={handleChange} value={data.Net_Value} required />
        <input type="text" name="Category" placeholder="Category" onChange={handleChange} required />
        <button type="submit">Submit</button>
      </form>
      {message && <div className="popup">{message}</div>}
      {plotUrl && <img src={plotUrl} alt="Anomaly Plot" style={{ marginTop: '20px', width: '80%' }} />}
    </div>
  );
};

export default Form;
