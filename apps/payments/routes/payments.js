// routes/payments.js
const express = require('express');
const { createPayment } = require('../services/asaas');
const router = express.Router();

router.post('/create', async (req, res) => {
  const dto = req.body;
  const payload = {
    customer: dto.customerAsaasId,
    dueDate: dto.dueDate, // "YYYY-MM-DD"
    value: dto.amount,
    description: dto.description,
    billingType: "BOLETO"
  };
  const asaasResp = await createPayment(payload);
  // salvar no DB: asaasResp.id, status...
  res.json(asaasResp);
});

module.exports = router;
