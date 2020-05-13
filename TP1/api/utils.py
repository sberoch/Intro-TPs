# utililty functions for domain handling

def remove_extra_ips(domain):
	
	# apply round robin
	domain['lastAccesedIP'] += 1
	domain['lastAccesedIP'] %= len(domain['ips'])

	return {
		'domain': domain['domain'],
		'ip': domain['ips'][domain['lastAccesedIP']],
		'custom': domain['custom']
	}

def new_domain(domain_name, ips, is_custom):
    return {
        'domain': domain_name,
        'ips': ips,
        'lastAccesedIP': 0,
        'custom': is_custom
    }
