# Shopify Product Monitor

A Python-based tool designed to monitor Shopify stores for product availability and restocks. It sends real-time notifications via Discord Webhooks.

## Features

- **Real-time Monitoring:** Tracks Shopify stores for product availability based on specified keywords.
- **Keyword Filtering:** Supports `+` for inclusion and `-` for exclusion of keywords.
- **Discord Notifications:** Sends detailed notifications on new products or restocks, including price and variants.
- **Proxy Support:** Handles session management using proxies for enhanced performance.
- **Persistent Tracking:** Remembers previously tracked products to avoid duplicate notifications.

## Requirements

- Python 3.8 or higher
- `tls_client`
- `discord-webhook`
- `python-dotenv`

## Setup Instructions

1. Clone the repository and navigate to the project directory.
2. Create a `.env` file in the project directory and add the following environment variables:
   ```env
   webhook_url=<Your Discord Webhook URL>
   ```
3. Optionally, provide a proxy list:
   - Create a `proxies.txt` file.
   - Add proxies in the format `IP:PORT:USER:PASS`, one per line.

## Usage

1. Configure the `sites` list with Shopify store URLs and keyword filters:
   ```python
   sites = [
       {"link": "https://example-shop.com", "keywords": "+keyword1, -keyword2"},
   ]
   ```
   - Use `+` before keywords to include products containing that term.
   - Use `-` before keywords to exclude products containing that term.
   - Leave the `keywords` field empty to monitor all products on the site.

2. Set the monitoring delay (in seconds):
   ```python
   delay = 15  # Adjust as needed
   ```

3. Start the monitoring script:
   ```bash
   python monitor.py
   ```

## Example Notification

Each Discord notification includes:
- Product name and URL
- Price
- Available variants and their stock status
- Direct cart addition links

## File Structure

- `proxies.txt`: (Optional) List of proxies for session management.
- `previous_availability.json`: Stores previously tracked product data.
- `.env`: Environment variables (including webhook URL).

## Notes

- Adjust the monitoring delay to control the frequency of checks.
- Ensure the webhook URL in the `.env` file is correct.
- Use proxies if monitoring multiple sites or to prevent IP bans.

## Disclaimer

This tool is intended for educational use only. Ensure compliance with the terms of service of any Shopify stores you monitor, and use the tool responsibly.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
