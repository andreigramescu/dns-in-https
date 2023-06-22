import stats
import dih.utils
import random
import numpy as np

SHOULD_RECOMPUTE = False

random.seed(42)
stats.N = 10_000
top_domains = stats.top_domains()

if SHOULD_RECOMPUTE:
    print('Reloading all data. This will take days...')
    stats.compute(top_domains, 'alldata-top.pickle')
    random.shuffle(top_domains)
    random.shuffle(top_domains)
    random.shuffle(top_domains)
    stats.compute(top_domains, 'alldata-random.pickle')

def perform(path, name, color, reload_ttls=False):

    print("Loading and preprocessing data...")
    alldata = stats.get_data(path)
    unique_domains = stats.get_unique_domains(alldata)
    num_domains = stats.get_num_domains(alldata)

    print("Number of Unique Domains...")
    data = np.array(list(num_domains.values()))
    stats.plot(data, 40,
               'Number of Unique Domains', f'numdoms-{name}.png',
               left_right=(0, 40), color=color)

    if reload_ttls:
        google_ttls = stats.dns_ttls(unique_domains, dih.utils.google_doh)
        cloudflare_ttls = stats.dns_ttls(unique_domains, dih.utils.cloudflare_doh)
        normal_ttls = stats.dns_ttls(unique_domains, dih.utils.dns_query)

        stats.save_data(google_ttls, f'google_ttls_{name}.pickle')
        stats.save_data(cloudflare_ttls, f'cloudflare_ttls_{name}.pickle')
        stats.save_data(normal_ttls, f'normal_ttls_{name}.pickle')
    else:
        google_ttls = stats.get_data(f'google_ttls_{name}.pickle')
        cloudflare_ttls = stats.get_data(f'cloudflare_ttls_{name}.pickle')
        normal_ttls = stats.get_data(f'normal_ttls_{name}.pickle')

    print("TTL Distributions...")
    google_ttls_arr = np.concatenate(list(google_ttls.values()))
    cloudflare_ttls_arr = np.concatenate(list(cloudflare_ttls.values()))
    normal_ttls_arr = np.concatenate(list(normal_ttls.values()))

    stats.plot(google_ttls_arr, 30,
               'Answer TTL Value (seconds)', f'ttls-google-{name}.png',
               log=True, left_right=(0,10800), color=color)
    stats.plot(cloudflare_ttls_arr, 30,
               'Answer TTL Value (seconds)', f'ttls-cloudflare-{name}.png',
               log=True, left_right=(0,10800), color=color)
    stats.plot(normal_ttls_arr, 30,
               'Answer TTL Value (seconds)', f'ttls-normal-{name}.png',
               log=True, left_right=(0,10800), color=color)

    print("Refresh distribution...")
    num_refreshes = stats.get_num_refreshes(normal_ttls)
    data = np.array(list(num_refreshes.values()))
    stats.plot(data, 40, 'Number of Refreshes Per Minute',
               f'refresh-{name}.png', left_right=(0,100), log=True, color=color)

    print("DNS cache hitrate...")
    cache_hitrate = stats.get_cache_hit_rate(alldata)
    data = np.array(list(cache_hitrate.values()))
    stats.plot(data, 20,
               'DNS Hit Rate On Page Load', f'dns-hitrate-{name}.png',
               left_right=(0,100), log=True, color=color)
