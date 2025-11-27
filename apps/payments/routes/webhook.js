// routes/webhook.js
const express = require('express');
const router = express.Router();

router.post('/asaas', async (req, res) => {
  const headerToken = req.headers['asaas-access-token'];
  if (headerToken !== process.env.ASAAS_WEBHOOK_TOKEN) {
    return res.status(401).send('invalid token');
  }

  const event = req.body; // payload do Asaas
  // estrutura: event.event, event.payment, etc.
  // trate eventos principais:
  if (event.event === 'PAYMENT_RECEIVED' || event.event === 'PAYMENT_UPDATED') {
    const asaasPayment = event.payment;
    // busque registro local pelo asaasPayment.id e atualize status, paidDate, etc.
    // exemplo: UPDATE FinancialPayments SET status = asaasPayment.status WHERE asaas_id = ...
  }

  // responda 200 rapidamente
  res.status(200).send('ok');
});
module.exports = router;
