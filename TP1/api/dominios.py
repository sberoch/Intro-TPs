from flask import abort, make_response
import dns.resolver

from utils import *

# Data to serve with our API
domains = {
    'fi.uba.ar': {
        'domain': 'fi.uba.ar',
        'ips': ['12.12.12.12'],
        'lastAccesedIP': 0,
        'custom': True
    },
}

def obtener_uno(domain):
    """
    Esta funcion maneja el request GET /api/domains/{dominio}

     :domain body:  nombre del dominio a obtener su ip
    :return:        200 dominio e ip, 404 dominio no encontrado
    """

    found_domain = domains.get(domain)

    if found_domain:
        return remove_extra_ips(found_domain)

    # lanza NXDOMAIN si no existe
    try:
        result = dns.resolver.query(domain)
    except dns.resolver.NXDOMAIN:
        return make_response({"error": "domain not found"},404)

    ips = []
    for ip in result:
        ips.append((ip.to_text()))

    domains[domain] = new_domain(domain, ips, is_custom=False)

    return remove_extra_ips(domains[domain])


def crear(**kwargs):
    """
    Esta funcion maneja el request POST /api/custom-domains

     :param body:  dominio a crear en la lista de domains
    :return:        201 dominio creado, 400 custom domain already exists
    """
    body = kwargs.get('body')
    domain = body.get('domain')
    ip = body.get('ip')

    if not domain or not ip:
        return make_response({"error": "custom domain already exists"}, 400)
    if domain in domains:
        if domains[domain]['custom'] == True:
            return make_response({"error": "custom domain already exists"}, 400)

    body['custom'] = True
    domains[domain] = new_domain(domain, [ip], is_custom=True)

    return make_response(body, 201)

def actualizar(domain, **kwargs):
    """
    Esta funcion maneja el request PUT /api/custom-domains

     :param body:  dominio a actualizar en la lista de domains
    :return:        200 dominio actualizado, 404 dominio no encontrado, 400 cuerpo invalido
    """
    body = kwargs.get('body')
    new_domain_name = body.get('domain')
    ip = body.get('ip')

    if not new_domain_name or not ip:
        return make_response({"error":"payload is invalid"}, 400)

    if domain not in domains:
        return make_response({"error": "domain not found"}, 404)

    body['custom'] = True
    domains[domain] = new_domain(new_domain_name, [ip], is_custom=True)

    return make_response(body, 200)



def buscar_custom(q=''):
    """
    Esta funcion maneja el request GET /api/custom-domains?q=<string>

     :param q:  filtro a aplicar sobre los nombres custom encontrados
    :return:        200 lista de dominios custom hallados
    """

    matching_custom = [remove_extra_ips(c) for c in domains.values() if c['custom'] and q in c['domain']]

    return make_response({'items':matching_custom}, 200)



def borrar(domain):
    """
    Esta funcion maneja el request DELETE /api/domains/{dominio}

    :domain body: dominio que se quiere borrar
    :return:        200 dominio, 404 dominio no encontrado
    """

    if domain not in domains or domains[domain]['custom'] == False:
        return make_response({"error": "domain not found"},404)

    del domains[domain]

    return make_response({"domain": domain}, 200)
