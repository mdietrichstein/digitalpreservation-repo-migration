import requests
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

ckan_root = config.get('ckan', 'RootUrl')
ckan_rest_url = ckan_root + config.get('ckan', 'RestUrl')


def fetch_ckan_contents():
    collections = {}

    groups = requests.get(ckan_rest_url + 'group_list').json()['result']

    for g in groups:
        jg = requests.get(ckan_rest_url + 'group_show',
                          {'id': g}).json()['result']

        collections[jg['id']] = {
            'id': jg['id'],
            'title': jg['title'],
            'description': jg['description'],
            'packages': []
        }

    packages = requests.get(ckan_rest_url + 'package_list').json()['result']

    for p in packages:
        jp = requests.get(ckan_rest_url + 'package_show',
                          {'id': p}).json()['result']

        metadata = []
        package = {
            'id': jp['id'],
            'title': jp['title'],
            'author': jp['author'],
            'license_title': jp['license_title'],
            'license_url': jp['license_url'],
            'resources': jp['resources'],
            'metadata': metadata
        }

        for e in jp['extras']:
            metadata.append({'key': e['key'], 'value': e['value']})

        for g in jp['groups']:
            collections[g['id']]['packages'].append(package)

    return list(collections.values())
