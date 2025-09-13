# QRIS Telegram Bot

A Telegram bot for generating dynamic QRIS (Quick Response Code Indonesian Standard) payments. This bot allows users to generate dynamic QRIS codes for receiving payments, with support for custom amounts and service fees.

## Features

### User Features
- 🏦 **Generate QRIS**: Create dynamic QRIS codes with custom amounts and service fees
- 📋 **Transaction History**: View all your past transactions
- ℹ️ **Help**: Get assistance with using the bot

### Admin Features
- 👔 **Multiple Admins**: Support for multiple administrators
- 🏪 **Merchant Management**: Add and manage QRIS merchants
- 🔄 **Toggle Merchant Status**: Enable/disable merchants as needed
- 📊 **Transaction Monitoring**: View all transactions in the system
- 📢 **Broadcast Messages**: Send announcements to all users
- 🧪 **Payment Simulation**: Simulate payment success/failure for testing

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
   - `/toggle_merchant <merchant_id>`: Enable/disable a merchant
   - `/add_admin <user_id>`: Add a new administrator (Super Admin only)
   - `/broadcast`: Send a message to all users
   - `/simulate_payment_success <transaction_id>`: Simulate a successful payment (for testing)
   - `/simulate_payment_failed <transaction_id>`: Simulate a failed payment (for testing)

## Running the Bot

```bash
python main.py
```

The bot will start and display "🤖 QRIS Payment Bot is running..."

## Auto Deployment

For easier deployment, you can use the provided deployment script:

1. Copy the `deploy.sh` script to the `/root` directory:
   ```bash
   # As root user
   cp /home/mardommah/Documents/project/qris-tele-bot/auto-deploy.sh /root/deploy.sh
   chmod +x /root/deploy.sh
   ```

2. Run the deployment script:
   ```bash
   /root/deploy.sh
   ```

This script will:
1. Remove the existing qris-tele-bot folder
2. Clone the latest version from the repository
3. Create a virtual environment
4. Install all dependencies
5. Copy environment variables using `/root/copy-env.sh`
6. Restart the systemd service

### Prerequisites for Auto Deployment

1. Ensure you have a `/root/copy-env.sh` script that copies your environment variables to the project directory
2. Make sure the systemd service `pythonapp.service` is configured
3. The deployment script should be run from the `/root` directory

### Setting up copy-env.sh

Create a script at `/root/copy-env.sh` with the following content:

```bash
#!/bin/bash
# Script to copy environment variables
cp /root/.env /root/qris-tele-bot/.env
```

Make it executable:
```bash
chmod +x /root/copy-env.sh
```

### Setting up systemd service

Create a service file at `/etc/systemd/system/pythonapp.service` with the following content:

```ini
[Unit]
Description=QRIS Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/qris-tele-bot
ExecStart=/root/qris-tele-bot/env/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable pythonapp.service
sudo systemctl start pythonapp.service
```

## Database Recovery

The bot includes a script to recover the SQLite database from backups:

```bash
# Interactive mode - will show available backups and prompt for selection
./recover_db.sh

# Direct mode - restore from a specific backup file
./recover_db.sh qris_bot_backup_20250913_111658.sql
```

This script will:
1. Show available backup files
2. Create a backup of the current database before restoration
3. Restore the database from the selected backup

### Prerequisites for Database Recovery

- Python 3.x must be installed on your system
- The backup files must be present in the `backups/` directory

### Recovery Process

When you run the recovery script:
1. It will list all available backup files
2. You can select which backup to restore from
3. Before restoration, it automatically creates a backup of the current database
4. The selected backup is then restored to the database

### Automated Recovery

You can also run the recovery process directly with a specific backup file:

```bash
python3 recovery_script.py qris_bot_backup_20250913_111658.sql
```

## Auto Backup to Supabase

The bot includes a script to automatically backup the SQLite database to Supabase:

```bash
./auto-backup-supabase.sh
```

This script will:
1. Export the SQLite database to a SQL file
2. Upload the backup to Supabase Storage

### Prerequisites for Auto Backup

1. Set up a Supabase account and project
2. Add your Supabase credentials to the `.env` file:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase API key (service role key recommended for backups)
3. Ensure `curl` and `sqlite3` are installed on your system
4. The backup script should be run from the project directory

### Setting up automated backups

You can set up automated backups using cron:

```bash
# Add to crontab to run daily at 2 AM
0 2 * * * /root/qris-tele-bot/auto-backup-supabase.sh >> /root/qris-tele-bot/logs/backup.log 2>&1
```

### Testing the backup script

To test the script with your own Supabase credentials:

1. Update the `.env` file with your actual Supabase URL and service role key
2. Run the script manually:
   ```bash
   ./auto-backup-supabase.sh
   ```

3. Check the `backups/` directory for the exported SQL file
4. Verify the backup appears in your Supabase Storage bucket

Note: For testing purposes, you can use dummy credentials, but the script will fail at the upload stage if invalid credentials are used.

## Security
```

Enable and start the service:
```bash
sudo systemctl enable pythonapp.service
sudo systemctl start pythonapp.service

## How It Works

1. **QRIS Generation**:
   - Users provide a payment amount
   - The bot modifies the static QRIS code to create a dynamic one with the specified amount
   - A new QR code image is generated and sent to the user

2. **Transaction Tracking**:
   - All transactions are stored in a SQLite database
   - Users can view their transaction history
   - Admins can monitor all transactions

## Database Structure

The bot uses SQLite with three main tables:
- `merchants`: Store merchant information and static QRIS codes
- `transactions`: Track all payment transactions
- `admins`: Manage administrator accounts

### Merchants Table
- `id`: Unique merchant identifier
- `name`: Merchant name
- `qris_static`: Static QRIS code data
- `qris_image_path`: Path to QRIS image file
- `owner_telegram_id`: Telegram ID of the merchant owner
- `is_active`: Status of the merchant (1 = active, 0 = inactive)
- `created_at`: Timestamp of when the merchant was created

## Merchant Management

Merchants can now be enabled or disabled by administrators using the `/toggle_merchant` command. This allows for better control over which merchants are available for QRIS generation. When a merchant is disabled, users will not be able to generate QRIS codes using that merchant until it is re-enabled.

For testing purposes, administrators can simulate payment success or failure using the `/simulate_payment_success` and `/simulate_payment_failed` commands followed by a transaction ID.

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