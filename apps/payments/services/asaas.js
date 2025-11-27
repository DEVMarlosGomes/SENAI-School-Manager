// services/asaas.js
const axios = require('axios');
const api = axios.create({
  baseURL: process.env.ASAAS_BASE_URL,
  headers: {
    'access_token': process.env.ASAAS_API_KEY,
    'Content-Type': 'application/json'
  }
});

async function createPayment(data) {
  const res = await api.post('/payments', data);
  return res.data;
}

module.exports = { createPayment };
