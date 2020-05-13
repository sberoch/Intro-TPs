import dns.resolver

# Resolve www.yahoo.com
result = dns.resolver.query('yahoo.com')
for answer in result:
    print(answer.to_text())
