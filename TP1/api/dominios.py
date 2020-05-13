from flask import abort, make_response

# Data to serve with our API
domains = {
    1: {
        'id':1,
        'domain': 'fi.uba.ar',
        'ips': ['12.12.12.12'],
        'lastAccesedIP': 0,
        'custom': False
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

# Create a handler for our read (GET) people
def obtener_todos():
    """
    Esta funcion maneja el request GET /api/domains

    :return:        200 lista ordenada alfabeticamente de domains de la materia
    """
    # Create the list of people from our data
    return [remove_extra_ips(d) for d in domains.values()]

def obtener_uno(id_alumno):
    """
    Esta funcion maneja el request GET /api/domains/{id_alumno}

     :id_alumno body:  id del alumno que se quiere obtener
    :return:        200 alumno, 404 alumno no encontrado
    """
    if id_alumno not in domains:
        return abort(404, 'El alumno no fue encontrado')

    return domains.get(id_alumno)

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
