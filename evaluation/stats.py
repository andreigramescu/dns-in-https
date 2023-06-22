import csv
import pickle
import time
import matplotlib.pyplot as plt
import numpy as np
import requests
import json

from selenium import webdriver

N = 10_000

def top_domains():
    with open('top-1m.csv', 'r') as file:
        reader = csv.reader(file)
        return [row[1] for row in reader]

def save_data(data, path):
    with open(path, 'wb') as backup_file:
        pickle.dump(data, backup_file)

def get_data(path):
    with open(path, 'rb') as backup_file:
        return pickle.load(backup_file)

def get_domain(url):
    tokens = url.split('/')
    if len(tokens) < 3:
        return None
    # Also need to split by : since you can have eg google.com:80
    domain = tokens[2]
    domain = domain.split(':')[0]
    return domain

def get_unique_domains(alldata):
    res = {}
    for (top_level_domain, entries) in alldata.items():
        resources = filter(lambda x: x['entryType'] == 'resource', entries)
        domains = map(lambda x: get_domain(x['name']), resources)
        domains = filter(lambda x: x is not None and len(x) > 0, domains)

        res[top_level_domain] = set(domains)
    return res

def get_num_domains(alldata):
    unique_domains = get_unique_domains(alldata)
    return dict((k, len(v)) for (k, v) in unique_domains.items())

def get_num_dns_cache_hits(alldata):
    num_hits, num_misses = 0, 0
    for (top_level_domain, entries) in alldata.items():
        resources = filter(lambda x: x['entryType'] == 'resource', entries)
        for resource in resources:
            domain = get_domain(resource['name'])
            time = resource['domainLookupEnd'] - resource['domainLookupStart']
            num_hits += time == 0
            num_misses += time != 0

    return num_hits, num_misses

def plot(data, bins, name, path, left_right=None, color='skyblue', log=False):
    median = np.median(data)
    p85 = np.percentile(data, 85)
    mean = np.mean(data)

    median, p85, mean = round(median, 2), round(p85, 2), round(mean, 2)

    if left_right is not None:
        left, right = left_right
        mask = (left <= data) & (data <= right)
        data = data[mask]

    plt.rcParams.update({'font.size': 16})
    plt.subplots(figsize=(8,6))
    plt.hist(data, bins=bins, edgecolor='black', linewidth=1, color=color)

    plt.axvline(mean, color='orange', linestyle='--', linewidth=2, alpha=1, label=f'Mean = {mean}')
    plt.axvline(median, color='red', linestyle='--', linewidth=2, alpha=1, label=f'Median = {median}')
    plt.axvline(p85, color='green', linestyle='--', linewidth=2, alpha=1, label=f'P85 = {p85}')

    plt.xlabel(name)
    plt.ylabel('Frequency')
    plt.legend()

    if log:
        plt.yscale('log')

    if path is None:
        plt.show()
    else:
        plt.savefig(path)

    plt.close()

def compute(TOP_DOMAINS, name):
    alldata = {}
    for pair in enumerate(TOP_DOMAINS):
        if len(alldata) == N:
            break

        _, top_level_domain = pair

        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = '/home/ag1319/andrei/crom/src/out/myrelease/chrome'
        chrome_options.add_argument('--incognito') # cache cleared
        driver = webdriver.Chrome(options=chrome_options)

        try:
            driver.get(f"https://{top_level_domain}")

            print(f"Current domain {pair}")

            entries = driver.execute_script("return window.performance.getEntries();")
        except Exception:
            print(f"Domain {pair} had issues")
            continue

        alldata[top_level_domain] = entries
        try:
            save_data(alldata, name)
        except:
            del alldata[top_level_domain]
            save_data(alldata, name)

        try:
            driver.close()
        except:
            pass

        try:
            driver.quit()
        except:
            pass

def dns_ttls(data, dnsq):
    res = {}
    for (i, (top_level_domain, domains)) in enumerate(data.items()):
        print(i, top_level_domain)

        rs = list(dnsq(domain) for domain in domains)
        rs = filter(lambda x: x is not None, rs)
        ttls = map(lambda x: x[2], rs)
        res[top_level_domain] = list(ttls)

    return res

def get_num_refreshes(ttls_map):
    def n_refreshes(ttls):
        ttls = filter(lambda x: x != 0, ttls)
        return sum(list(map(lambda x: 60 / x, ttls)))
    return dict((k, n_refreshes(v)) for (k, v) in ttls_map.items())

def get_cache_hit_rate(alldata):
    def dns_lookup_time(entry):
        return entry['domainLookupEnd'] - entry['domainLookupStart']

    res = {}
    for (top_level_domain, entries) in alldata.items():
        resources = filter(lambda x: x['entryType'] == 'resource', entries)
        lookup_times = map(dns_lookup_time, resources)
        hits_misses = list(map(lambda e: 0 if e else 1, lookup_times))
        total = len(hits_misses)
        hits = sum(hits_misses)

        res[top_level_domain] = round((hits / total) * 100, 2) if total else 100
    return res