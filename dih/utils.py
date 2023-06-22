import dns.resolver
import requests

def dns_query(domain):
    try:
        answer = dns.resolver.resolve(domain, 'A')
    except Exception:
        return None

    ip, ttl = str(answer[0]), answer.ttl
    return domain, ip, ttl

def parse_doh_json(body):
    if 'Answer' not in body:
        return None

    for answer in body['Answer']:
        if answer['type'] == 1: # record of type A
            return answer['name'], answer['data'], int(answer['TTL'])

    return None

def google_doh(domain):
    try:
        url = "https://dns.google/resolve"
        params = { "name": domain, "type": "A" }
        response = requests.get(url, params=params)
    except:
        return None
    if response.status_code != 200:
        return None
    body = response.json()
    return parse_doh_json(body)

def cloudflare_doh(domain):
    try:
        url = f"https://cloudflare-dns.com/dns-query"
        params = { "name": domain, "type": "A" }
        headers = { "accept": "application/dns-json" }
        response = requests.get(url, params=params, headers=headers)
    except:
        return None
    if response.status_code != 200:
        return None
    body = response.json()
    return parse_doh_json(body)


def fmt(resolutions):
    SEP = '|'
    return ','.join([f"{h}{SEP}{ip}{SEP}{ttl}" for (h, ip, ttl) in resolutions])