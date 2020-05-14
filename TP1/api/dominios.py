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
        return abort(404, {"error": "domain not found"})

    ips = []
    for ip in result:
        ips.append((ip.to_text()))

    domains[domain] = new_domain(domain, ips, is_custom=False)

    return remove_extra_ips(domains[domain])


def crear(**kwargs):
    """
    Esta funcion maneja el request POST /api/domains

     :param body:  dominio a crear en la lista de domains
    :return:        201 dominio creado, 400 custom domain already exists
    """
    body = kwargs.get('body')
    domain = body.get('domain')
    ip = body.get('ip')

    if domain in domains:
        if domains[domain]['custom'] == True:
            return abort(400, {"error": "custom domain already exists"})

    body['custom'] = True
    domains[domain] = {'domain': domain, 'ips': [ip], 'lastAccesedIP': 0, 'custom': True}

    return make_response(body, 201)

def actualizar(**kwargs):
    """
    Esta funcion maneja el request PUT /api/domains

     :param body:  dominio a actualizar en la lista de domains
    :return:        200 dominio actualizado, 404 dominio no encontrado, 400 cuerpo invalido
    """
    body = kwargs.get('body')
    domain = body.get('domain')
    ip = body.get('ip')

    if not domain or not ip:
        return abort(400, "payload is invalid")

    if domain not in domains:
        return abort(404, {"error": "domain not found"})

    body['custom'] = True
    domains[domain] = {'domain': domain, 'ips': [ip], 'lastAccesedIP': 0, 'custom': True}

    return make_response(body, 200)

# CODIGO DE TEMPLATE:

def borrar(id_alumno):
    """
    Esta funcion maneja el request DELETE /api/domains/{id_alumno}

    :id_alumno body:  id del alumno que se quiere borrar
    :return:        200 alumno, 404 alumno no encontrado
    """
    if id_alumno not in domains:
        return abort(404, 'El alumno no fue encontrado')

    del domains[id_alumno]

    return make_response('', 204)
