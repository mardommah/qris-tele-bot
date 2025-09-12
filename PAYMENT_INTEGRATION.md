# PAYMENT_INTEGRATION.md
# Payment Gateway Integration Guide

This document explains how to integrate the QRIS Telegram Bot with real payment gateways that support webhook notifications.

## Supported Payment Gateways

The bot can work with any payment gateway that supports webhook notifications. Some popular options in Indonesia include:

1. **Midtrans**
2. **Xendit**
3. **Duitku**
4. **iPaymu**

## Webhook Endpoint

The bot provides a webhook endpoint at:
```
[YOUR_SERVER_URL]/webhook/payment
```

This endpoint expects a POST request with JSON data in the following format:

```json
{
  "transaction_id": 123,
  "status": "success",
  "amount": "10000"
}
```

### Required Fields

- `transaction_id`: The ID of the transaction in your bot's database
- `status`: The payment status ("success" or "failed")
- `amount`: The payment amount (optional, for logging purposes)

## Integration Examples

### Midtrans Integration

If you're using Midtrans as your payment gateway, you can configure the webhook URL in your Midtrans dashboard:

1. Login to your Midtrans account
2. Go to Settings > Configuration
3. Set the "Payment Notification URL" to your webhook endpoint:
   ```
   [YOUR_SERVER_URL]/webhook/payment
   ```

### Xendit Integration

For Xendit integration:

1. Login to your Xendit dashboard
2. Go to Settings > Webhooks
3. Add a new webhook with:
   - URL: `[YOUR_SERVER_URL]/webhook/payment`
   - Events: `payment_status`
   
## Testing Webhooks

You can test the webhook functionality using the test script:

```bash
python test_payment_notification.py
```

Or manually using curl:

```bash
curl -X POST \
  http://localhost:5000/webhook/payment \
  -H 'Content-Type: application/json' \
  -d '{
    "transaction_id": 1,
    "status": "success",
    "amount": "10000"
  }'
```

## Security Considerations

1. **HTTPS**: In production, always use HTTPS for your webhook endpoints
2. **Authentication**: Consider adding authentication to your webhook endpoints
3. **Validation**: Always validate incoming webhook data
4. **Rate Limiting**: Implement rate limiting to prevent abuse

## Custom Integration

If your payment gateway requires a different data format, you can modify the webhook handler in `webhook_server.py` to parse the incoming data according to your payment gateway's specifications.

## Troubleshooting

### Webhook Not Received

1. Check that your server is accessible from the internet
2. Verify the webhook URL in your payment gateway settings
3. Check server logs for errors

### Notifications Not Sent to Users

1. Ensure the transaction ID exists in the database
2. Verify that the user's chat_id is correctly stored
3. Check Telegram bot permissions

### Database Issues

1. Make sure the database schema is up to date
2. Verify that the chat_id column exists in the transactions table