from flask import abort, make_response
import dns.resolver


# Data to serve with our API
domains = {
    'fi.uba.ar': {
        'domain': 'fi.uba.ar',
        'ips': ['12.12.12.12'],
        'lastAccesedIP': 0,
        'custom': True
    },
}

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


# CODIGO DE TEMPLATE:

def crear(**kwargs):
    """
    Esta funcion maneja el request POST /api/domains

     :param body:  alumno a crear en la lista de domains
    :return:        201 alumno creado, 400 dni o padron duplicado
    """
    alumno = kwargs.get('body')
    dni = alumno.get('dni')
    padron = alumno.get('padron')
    nombre = alumno.get('nombre')
    if not dni or not padron or not nombre:
        return abort(400, 'Faltan datos para crear un alumno')

    dup = False
    for alumno_existente in domains.values():
        dup = dni == alumno_existente.get('dni') or padron == alumno_existente.get('padron')
        if dup: break

    if dup:
        return abort(400, 'DNI o Padron ya existentes')

    new_id = max(domains.keys()) + 1
    alumno['id'] = new_id
    domains[new_id] = alumno

    return make_response(alumno, 201)

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
