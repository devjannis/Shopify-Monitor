# Shopify Product Monitor

A Python-based tool for monitoring Shopify stores for product availability and restocks. Notifications are sent via Discord Webhooks.

## Features

- Monitors Shopify stores for product availability based on keywords.
- Supports keyword modifiers (`+` for inclusion, `-` for exclusion).
- Sends detailed Discord notifications for new products or restocks.
- Proxy support for session management.
- Persistent product availability tracking.

## Requirements

- Python 3.8 or higher
- `tls_client`
- `discord-webhook`
- `python-dotenv`

## Setup

1. Clone the repository and navigate to the project directory.
2. Create a `.env` file in the project directory with the following variables:
   ```env
   webhook_url=<Your Discord Webhook URL>
   ```
4. Ensure you have a proxy list (optional):
   - Create a file `proxies.txt`.
   - Add proxies in the format `IP:PORT:USER:PASS`, one per line.

## Usage

1. Define the `sites` list with the Shopify store links and keyword filters:
   ```python
   sites = [
       {"link": "https://example-shop.com", "keywords": "+keyword1, -keyword2"},
   ]
   ```
   - Use `+` before keywords to include products with that term.
   - Use `-` before keywords to exclude products with that term.

2. Set the monitoring delay (in seconds):
   ```python
   delay = 15  # Adjust as needed
   ```

3. Run the script:
   ```bash
   python monitor.py
   ```

## Example Notification

A Discord notification includes:
- Product name and URL
- Price
- Variants and their availability
- Links for direct cart addition

## File Structure

- `roxies.txt`: Optional proxy list.
- `previous_availability.json`: Stores previously tracked product data.
- `.env`: Environment variables.

## Notes

- Adjust the delay to control how frequently the tool checks for updates.
- Ensure the webhook URL in the `.env` file is valid.
- Use proxies if monitoring multiple sites or to avoid IP bans.

## Disclaimer

This tool is for educational purposes only. Use responsibly and ensure compliance with the terms of service of Shopify stores you monitor.
