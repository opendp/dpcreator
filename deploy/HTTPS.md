# Cloudflare configuration

- Login to Cloudflare and click "+ Add Site"
- Enter the domain name that will be used to host the site
- Choose a plan
- You will see a set of DNS records taken from the current registrar. Check these records against the registrar and make sure all the entries are there. Add any that are missing. 
- Click continue
- Select "Full encryption"
- Scroll down and activate the switch that says "Always use HTTPS"


## DNS configuration 

For each subdomain, we need to decide if CloudFlare should route its traffic. A row for the domain dev.dpcreator.org should look like: 

| Type      | Name    | Content        | Proxy Status | TTL |
|-----------|---------|----------------|----------|---------|
| A         |   dev   |   (ip address) | Proxied  |   auto  |

For any subdomains which should not be routed through CloudFlare, they should be left as "DNS only" like so:

| Type      | Name    | Content        | Proxy Status | TTL     |
|-----------|---------|----------------|--------------|---------|
| A         |   demo  |  (ip address)  | DNS only     |   auto  |
