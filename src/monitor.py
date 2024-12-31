import tls_client, json, time, threading, random, os, datetime
from discord_webhook import DiscordWebhook, DiscordEmbed
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

class Shopify():
    def __init__(self, site, keywords, delay, json_file_lock, code_lock, webhook_url):
        self.json_file_lock = json_file_lock
        self.code_lock = code_lock
        self.webhook_url = webhook_url
        self.delay = delay
        self.keywords = keywords
        self.link = site
        parsed_url = urlparse(site)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/"
        self.base_url = base_url
        self.session = tls_client.Session(client_identifier="chome_120", random_tls_extension_order=True)
        self.product_json = {}
        self.data = {}
        if os.path.getsize("proxies.txt") == 0:
            self.proxies = None
        else:
            with open("proxies.txt","r") as f:
                self.proxies = f.read().splitlines()
        self.get_product_json()
    
    def process_product(self, product):
        keyword_matched = False
        
        if self.keywords:
            product_title = str(product['title']).lower()
            
            for keyword in self.keywords:
                keyword = keyword.strip().lower()
                
                # Check if keyword has a "+" modifier
                if keyword.startswith("+"):
                    keyword = keyword[1:]
                    if keyword in product_title:
                        keyword_matched = True
                        
                # Check if keyword has a "-" modifier
                elif keyword.startswith("-"):
                    keyword = keyword[1:]
                    if keyword in product_title:
                        keyword_matched = False
                        break
                    
                # Normal keyword match
                else:
                    if keyword in product_title:
                        keyword_matched = True
                        break

        # If keyword matched, proceed with processing the product
        if keyword_matched:
            self.logging(f"Monitoring {product['title']} | {self.base_url}")
            notification_dict = {}
            product_id = str(product["id"])
            
            # Check if the link exists in data, if not, add it
            if self.link not in self.data:
                self.data[self.link] = {}
            
            # Check if product exists in the link data, if not, add it
            if product_id not in self.data[self.link]:
                self.data[self.link][product_id] = {
                    'title': product['title'],
                    'handle': product['handle'],
                    'image': product['images'][0]['src'],
                    'price': product['variants'][0]['price'] if 'variants' in product and product['variants'] else "N/A",
                    'variants': []
                }
            
            # Loop through variants of the product
            for variant in product['variants']:
                availability = variant.get('available', "N/A")
                variant_id = variant['id']
                
                # If variant not already in data, add it
                if variant_id not in (item['id'] for item in self.data[self.link][product_id]['variants']):
                    self.data[self.link][product_id]['variants'].append({
                        'id': variant_id,
                        'size': variant['title'],
                        'available': availability
                    })
                    
                    # If this is the first time adding, create a notification
                    if product_id not in notification_dict:
                        notification_dict[product_id] = {}
                    notification_dict[product_id][variant_id] = {
                        'size': variant['title'],
                        'availability': f"~~None~~ -> {availability}",
                        'id': variant_id,
                        'type': 'New add'
                    }
                    
                # If variant already exists, check for availability change
                else:
                    for pdvar in self.data[self.link][product_id]['variants']:
                        if pdvar['id'] == variant_id and pdvar['available'] != availability:
                            pdvar['available'] = availability
                            
                            # Create notification for availability change
                            if product_id not in notification_dict:
                                notification_dict[product_id] = {}
                            notification_dict[product_id][variant_id] = {
                                'size': variant['title'],
                                'availability': f"~~{pdvar['available']}~~ -> {availability}",
                                'id': variant_id,
                                'type': 'Restock'
                            }
                            
            # Send notifications if any
            if notification_dict:
                self.send_notification(notification_dict)
            self.save_previous_availability(self.data)

    def get_product_json(self):
        while True:
            with self.code_lock:
                self.session.cookies.clear()
                self.setupProxie()
                self.load_previous_availability()
                response = self.session.get(url=f"{self.link}/products.json?limit=10")
                try:
                    data = response.json()['products']
                except:
                    data = response.json()

                if len(data) == 1:
                    product = data['product']
                    self.process_product(product=product)
                else:
                    for product in data:
                        self.process_product(product=product)
                time.sleep(self.delay / 1000)

    def send_notification(self, notification_dict):
        self.webhook = DiscordWebhook(url=self.webhook_url, rate_limit_retry=True)
        pid = next(iter(notification_dict))
        name = self.data[self.link][pid]['title']
        handle = self.data[self.link][pid]['handle']
        image = self.data[self.link][pid]['image']
        price = self.data[self.link][pid]['price']
        url = f"{self.link}/products/{handle}"
        embed = DiscordEmbed(title=name, url=url, color=0xf75c02)
        embed.set_author(name=self.link, url=self.link)
        embed.add_embed_field(name=f"**PID**", value=pid, inline=False)
        embed.add_embed_field(name=f"**Price**", value=f"{price}€", inline=False)
        size_values = [entry['size'] for entry in notification_dict[pid].values()]
        type_ids = [str(entry['id']) for entry in notification_dict[pid].values()]
        links = [f"[{size}]({self.base_url}/cart/{type_id}:1?payment=shop_pay)" for size, type_id in zip(size_values, type_ids)]
        availability_values = [str(entry['availability']) for entry in notification_dict[pid].values()]
        type_values = [entry['type'] for entry in notification_dict[pid].values()]

        max_length_per_split = 1024

        # Check if any of the fields exceeds the max length per split
        total_length = sum(len(link) for link in links)
        num_splits = (total_length + max_length_per_split - 1) // max_length_per_split

        print(num_splits, total_length)
        if num_splits == 1:
            # Join the fields as before
            links = '\n'.join(links)
            availability_values = '\n'.join(availability_values)
            type_values = '\n'.join(type_values)
            embed.add_embed_field(name="Size", value=links, inline=True)
            embed.add_embed_field(name="Status", value=availability_values, inline=True)
            embed.add_embed_field(name="Type", value=type_values, inline=True)
        else:
            split_length = total_length // num_splits
            split_links = []
            split_availability_values = []
            split_type_values = []
            current_length = 0
            current_links = []
            current_availability_values = []
            current_type_values = []
            
            for link, availability, type_value in zip(links, availability_values, type_values):
                link_length = len(link)
                if current_length + link_length <= split_length:
                    current_links.append(link)
                    current_availability_values.append(availability)
                    current_type_values.append(type_value)
                    current_length += link_length
                else:
                    split_links.append(current_links)
                    split_availability_values.append(current_availability_values)
                    split_type_values.append(current_type_values)
                    current_links = [link]
                    current_availability_values = [availability]
                    current_type_values = [type_value]
                    current_length = link_length
            
            # Append the last batch
            if current_links:
                split_links.append(current_links)
                split_availability_values.append(current_availability_values)
                split_type_values.append(current_type_values)
            
            # Add embed fields
            for i, (links_part, skus_part, levels_part) in enumerate(zip(split_links, split_availability_values, split_type_values)):
                if i == 0:
                    embed.add_embed_field(name="Size", value='\n'.join(links_part), inline=True)
                    embed.add_embed_field(name="Status", value='\n'.join(skus_part), inline=True)
                    embed.add_embed_field(name="Type", value='\n'.join(levels_part), inline=True)
                else:
                    embed.add_embed_field(name="", value='\n'.join(links_part), inline=True)
                    embed.add_embed_field(name="", value='\n'.join(skus_part), inline=True)
                    embed.add_embed_field(name="", value='\n'.join(levels_part), inline=True)

        embed.set_thumbnail(url=image)
        embed.set_timestamp()
        self.webhook.add_embed(embed)
        self.webhook.execute()

    def load_previous_availability(self):
        try:
            with self.json_file_lock:
                with open("previous_availability.json", "r") as file:
                    try:
                        self.data = json.load(file)
                    except:
                        self.data = {}
        except FileNotFoundError:
            self.data = {}

    def save_previous_availability(self, previous_availability):
        with self.json_file_lock:
            with open("previous_availability.json", "w") as file:
                json.dump(previous_availability, file)

    def setupProxie(self):
        if self.proxies:
            try:
                proxy = random.choice(self.proxies)
                splitted = proxy.split(':')
                proxy = {
                    'http': 'http://{}:{}@{}:{}'.format(splitted[2], splitted[3], splitted[0],splitted[1]),
                    'https': 'http://{}:{}@{}:{}'.format(splitted[2], splitted[3], splitted[0],splitted[1]),
                    }
            except:
                proxy  = {"http": "","https": ""}
        
            self.session.proxies.update(proxy)

    def logging(self, text):
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {text}")

sites = [
    {"link": "https://example.com/", "keywords": "+Example, -Example"},
]

delay = 15
json_file_lock = threading.Lock()
code_lock = threading.Lock()

webhook_url = os.getenv("webhook_url")

if __name__ == "__main__":
    for site in sites:
        keywords = site['keywords']
        if len(keywords) == 0:
            keyword_list = None
        else:
            if "," in keywords:
                keyword_list = keywords.split(", ")
            else:
                keyword_list = []
                keyword_list.append(keywords)
        threading.Thread(target=Shopify,args=(site['link'], keyword_list, delay, json_file_lock, code_lock)).start()
