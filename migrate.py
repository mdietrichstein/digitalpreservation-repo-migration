import argparse
from api_dspace import *
from api_ckan import *


def list_ckan_contents():
    collections = fetch_ckan_contents()

    if not collections:
        print('Repository is empty')

    for c in collections:
        print(c['title'])

        for p in c['packages']:
            print('\t{}'.format(p['title']))

            resource = p['resources'][0]

            print('\t\tMimeType: {}'.format(resource['mimetype']))
            print('\t\tFilename: {}'.format(resource['name']))
            print('\t\tDescription: {}'.format(resource['description']))

            for m in p['metadata']:
                print('\t\t{}: {}'.format(m['key'], m['value']))


def list_dspace_contents():
    collections = fetch_dspace_contents()

    if not collections:
        print('Repository is empty')

    for c in collections:
        print(c['name'])

        for i in c['items']:
            print('\t{}'.format(i['name']))

            if i['bitstreams']:
                bitstream = i['bitstreams'][0]

                print('\t\tMimeType: {}'.format(bitstream['mimeType']))
                print('\t\tFilename: {}'.format(bitstream['name']))
                print('\t\tDescription: {}'.format(bitstream['description']))

            for m in i['metadata']:
                print('\t\t{}:{}'.format(m['key'], m['value']))


def migrate_ckan_to_dspace(email, password, community_id):
    session_id = dspace_auth(email, password)

    print('Got dspace session id', session_id)

    print('Registering metadata schema in dspace')
    dspace_create_schema(session_id, 'http://local/namespace/ti', 'ti')
    dspace_set_schema_field(session_id, 'ti',
    {
        'description': 'Track bitrate',
        'element': 'bitrate',
        'name': 'ti.bitrate',
    })
    dspace_set_schema_field(session_id, 'ti',
    {
        'description': 'Track duration',
        'element': 'duration',
        'name': 'ti.duration',
    })

    print('Fetching data from ckan')
    ckan_collection = fetch_ckan_contents()

    for cc in ckan_collection:
        print('Migrating collection "{}"'.format(cc['title']))

        dc = dspace_create_collection(session_id, community_id,
                                      cc['title'])

        collection_id = dc['uuid']

        for package in cc['packages']:
            print('Migrating package "{}"'.format(package['title']))

            item = dspace_create_item(session_id, collection_id,
                                      package['title'])
            item_id = item['uuid']

            print('Migrating metadata')
            metadata = [
                { 'key': 'dc.title', 'value': package['title'], 'language': None },
                { 'key': 'dc.contributor.author', 'value': package['author'], 'language': None }
            ]

            for m in package['metadata']:
                metadata.append({
                    'key': m['key'], 'value': m['value'], 'language': None
                })

            dspace_set_metadata(session_id, item_id, metadata)

            print('Migrating file data')

            resource = package['resources'][0]

            dspace_post_file(session_id, item_id,
                             resource['url'], resource['name'],
                             resource['description'], resource['mimetype'],
                             resource['format'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command',
                        help='list-ckan, list-dspace, migrate-ckan-to-dspace')
    args = parser.parse_args()

    if args.command == 'list-ckan':
        list_ckan_contents()
    elif args.command == 'list-dspace':
        list_dspace_contents()
    elif args.command == 'migrate-ckan-to-dspace':
        import configparser
        config = configparser.ConfigParser()
        config.read('config.ini')

        email = config.get('dspace', 'UserEmail')
        password = config.get('dspace', 'UserPassword')

        community_id = None

        if config.has_option('dspace', 'CommunityId'):
            community_id = config.get('dspace', 'CommunityId')

        try:
            migrate_ckan_to_dspace(email, password, community_id)
        except ValueError as e:
            print('ERROR', e)
    else:
        print('Unknown command', args.command)
