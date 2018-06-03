import requests
from urllib.request import urlopen
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

dspace_root = config.get('dspace', 'RootUrl')
dspace_rest_url = dspace_root + config.get('dspace', 'RestUrl')

HEADER_JSESSIONID = 'JSESSIONID'


def fetch_dspace_contents():
    json_collections = requests.get(dspace_rest_url + 'collections').json()

    collections = []

    for jc in json_collections:
        collections.append({
            'id': jc['uuid'],
            'name': jc['name'],
            'description': jc['shortDescription'],
            'license': jc['license'],
            'items': []
        })

    for c in collections:
        json_items = requests.get(dspace_rest_url + 'collections/' + c['id'] + '/items').json()

        for ji in json_items:
            item = {
                'id': ji['uuid'],
                'name': ji['name'],
                'metadata': [],
                'bitstreams': [],
            }

            c['items'].append(item)

            json_bitstreams = requests.get(dspace_rest_url + 'items/' + item['id'] + '/bitstreams').json()
            for jb in json_bitstreams:
                item['bitstreams'].append({
                    'mimeType': jb['mimeType'],
                    'format': jb['format'],
                    'description': jb['description'],
                    'name': jb['name']
                })

            json_meta = requests.get(dspace_rest_url + 'items/' + item['id'] + '/metadata').json()

            for jm in json_meta:
                item['metadata'].append({
                    'key': jm['key'],
                    'value': jm['value']
                })

    return collections


def dspace_auth(email, password):
    data = {'email': email, 'password': password}
    r = requests.post(dspace_rest_url + 'login', data=data)
    return r.cookies[HEADER_JSESSIONID]


def dspace_get_communities():
    return requests.get(dspace_rest_url + 'communities').json()


def dspace_create_collection(session_id, community_id, name):

    if not community_id:
        communities = dspace_get_communities()

        if not communities:
            raise ValueError('No communities found. Please create at least one dspace community to proceed.')

        first_community = communities[0]

        print('Community id not specified, using first community: {} ({})'.format(
              first_community['name'], first_community['uuid']))

        community_id = first_community['uuid']

    result = requests.post(dspace_rest_url + 'communities/' + community_id + '/collections',
                           json={'name': name},
                           headers={'accept': 'application/json'},
                           cookies={HEADER_JSESSIONID: session_id})

    if result.status_code is not 200:
        raise ValueError('Unable to create collection. Check your dspace configuration in config.ini and make sure that your credentials are correct and that at least on community exists')
    
    return result.json()


def dspace_create_item(session_id, collection_id, name):
    result = requests.post(dspace_rest_url + 'collections/' + collection_id + '/items',
                           json={'name': name},
                           headers={'accept': 'application/json'},
                           cookies={HEADER_JSESSIONID: session_id})

    return result.json()


def dspace_set_metadata(session_id, item_id, metadata):
    result = requests.post(dspace_rest_url + 'items/' + item_id + '/metadata',
                           json=metadata,
                           headers={'accept': 'application/json'},
                           cookies={HEADER_JSESSIONID: session_id})

    return result


def dspace_post_file(session_id, item_id, filepath, name, description,
                     mimeType, file_format):
    response = requests.post(dspace_rest_url + 'items/' + item_id + '/bitstreams',
                             files={'file': urlopen(filepath)},
                             params={'name': name, 'description': description,
                                     'mimeType': mimeType, 'format': file_format},
                             headers={'accept': 'application/json'},
                             cookies={HEADER_JSESSIONID: session_id})

    return response


def dspace_create_schema(session_id, namespace, prefix):
    result = requests.post(dspace_rest_url + 'registries/schema',
                           json={'namespace': namespace, 'prefix': prefix},
                           headers={'accept': 'application/json'},
                           cookies={HEADER_JSESSIONID: session_id})

    return result


def dspace_set_schema_field(session_id, schema_prefix, fields):
    result = requests.post(dspace_rest_url + 'registries/schema/' + schema_prefix + '/metadata-fields',
                           json=fields,
                           headers={'accept': 'application/json'},
                           cookies={HEADER_JSESSIONID: session_id})

    return result
