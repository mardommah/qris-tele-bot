# QRIS Telegram Bot

A Telegram bot for generating dynamic QRIS (Quick Response Code Indonesian Standard) payments. This bot allows users to generate dynamic QRIS codes for receiving payments, with support for custom amounts and service fees.

## Features

### User Features
- 🏦 **Generate QRIS**: Create dynamic QRIS codes with custom amounts and service fees
- 📋 **Transaction History**: View all your past transactions
- 🔔 **Payment Notifications**: Receive instant notifications when payments are processed
- ℹ️ **Help**: Get assistance with using the bot

### Admin Features
- 👔 **Multiple Admins**: Support for multiple administrators
- 🏪 **Merchant Management**: Add and manage QRIS merchants
- 📊 **Transaction Monitoring**: View all transactions in the system
- 📢 **Broadcast Messages**: Send announcements to all users

## Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))
- SQLite (included with Python)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/qris-tele-bot.git
   cd qris-tele-bot
   ```

2. Create a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file and add your:
   - `TELEGRAM_BOT_TOKEN`: Your bot token from BotFather
   - `ADMIN_USER_ID`: Your Telegram user ID (get from [@userinfobot](https://t.me/userinfobot))

## Setup

1. Create your first merchant:
   - Start a chat with your bot
   - Send `/add_merchant` command
   - Follow the prompts to add a merchant name and upload a QRIS image
   - Confirm the merchant details

2. Configure your QRIS static code:
   - The bot requires a static QRIS code image to generate dynamic codes
   - Upload a clear image of your static QRIS code during merchant setup

## Usage

### For Users

1. Start the bot by sending `/start`
2. Choose from the menu options:
   - **Generate QRIS**: Create a new dynamic QRIS code
     1. Enter payment amount
     2. Specify if there's a service fee
     3. Receive a dynamic QRIS code with your specified amount
   - **Riwayat Transaksi**: View your transaction history
   - **Bantuan**: Get help with using the bot

### For Admins

1. Access admin features by sending `/admin`
2. Available admin commands:
   - `/add_merchant`: Add a new merchant for yourself
   - `/add_merchant_for_user <user_id>`: Add a merchant for another user
   - `/list_merchants`: View all registered merchants
   - `/add_admin <user_id>`: Add a new administrator (Super Admin only)
   - `/broadcast`: Send a message to all users

## Running the Bot

```bash
python main.py
```

The bot will start and display "🤖 QRIS Payment Bot is running..."

## Running Tests

To run the tests, you'll need to install the testing dependencies:

```bash
pip install pytest pytest-asyncio
```

Then run the tests:

```bash
# Run all tests
python -m pytest

# Run a specific test file
python -m pytest test_bot.py

# Run tests with verbose output
python -m pytest -v
```

## Resource Monitoring

To monitor the resource usage (RAM & CPU) of your bot:

### Using the built-in monitoring script:
```bash
# Get system overview only
python monitor_bot.py --overview

# Continuous monitoring (updates every 5 seconds)
python monitor_bot.py

# Custom update interval (e.g., every 2 seconds)
python monitor_bot.py --interval 2
```

### Using system tools:
```bash
# Real-time monitoring with top
top -p $(pgrep -f python)

# Monitor specific processes
ps aux | grep python

# System-wide resource usage
vmstat 5
```

## Payment Notifications

The bot now supports automatic payment notifications when users complete transactions:

1. **Webhook Server**: A separate webhook server receives payment notifications from payment gateways
2. **Automatic Status Updates**: Transaction statuses are automatically updated in the database
3. **User Notifications**: Users receive instant notifications when their payments are processed

To run the webhook server:
```bash
python webhook_server.py
```

The webhook server will start on port 5000 and listen for payment notifications at `/webhook/payment`.

For testing purposes, you can manually trigger payment notifications using the `/webhook <transaction_id> <status>` command in Telegram.

For detailed instructions on integrating with payment gateways, see [PAYMENT_INTEGRATION.md](PAYMENT_INTEGRATION.md).

## How It Works

1. **QRIS Generation**:
   - Users provide a payment amount
   - The bot modifies the static QRIS code to create a dynamic one with the specified amount
   - A new QR code image is generated and sent to the user

2. **Transaction Tracking**:
   - All transactions are stored in a SQLite database
   - Users can view their transaction history
   - Admins can monitor all transactions

3. **Payment Notifications**:
   - When a user scans and pays the QRIS code, the payment gateway sends a webhook notification
   - The webhook server receives the notification and updates the transaction status
   - Users receive instant notifications about their payment status via Telegram

## Database Structure

The bot uses SQLite with three main tables:
- `merchants`: Store merchant information and static QRIS codes
- `transactions`: Track all payment transactions
- `admins`: Manage administrator accounts

The `transactions` table has been updated to include a `chat_id` column for sending payment notifications to users.

## Security

- Only authorized admins can access admin features
- All data is stored locally in SQLite
- Telegram tokens are stored in environment variables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, contact the bot administrator or open an issue on GitHub.