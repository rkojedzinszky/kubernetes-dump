#!/usr/bin/env python

import argparse
import requests
import yaml
import os
import re
from pathlib import Path

NAMESPACE_FIELD = 'namespace'


def processItems(itemlist):

    for item in itemlist:
        item.pop('status', None)
        kind = item['kind'].lower()
        metadata = item['metadata']
        if NAMESPACE_FIELD in metadata:
            ddir = 'namespaces/{}/{}'.format(metadata[NAMESPACE_FIELD],
                                             kind)
        else:
            ddir = 'cluster/{}'.format(kind)

        p = Path(ddir)
        if not p.exists():
            p.mkdir(parents=True)

        fpath = p.joinpath('{}.yml'.format(metadata['name']))

        with fpath.open('w') as yfh:
            yfh.write(yaml.dump(item))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Dump configuration from k8s cluster')

    parser.add_argument('-c', '--config', default='config.yml',
                        help='Config file')

    options = parser.parse_args()

    with open(options.config, 'r') as fh:
        config = yaml.safe_load(fh.read())

    session = requests.Session()
    if 'ca' in config:
        session.verify = config['ca']

    session.headers.update({
        'Authorization': 'bearer {}'.format(config['token']),
        })

    allitems = []

    for r in config['resources']:
        components = r.split('/')
        clen = len(components)
        if clen == 2:  # [core]/ver/resource
            uri = 'api/{}'.format(r)
        elif clen == 3:  # group/ver/resource
            uri = 'apis/{}'.format(r)
        else:
            raise RuntimeError('Unrecognized resource: {}'.format(r))

        url = '{}/{}'.format(config['server'], uri)
        # print('Fetching {}'.format(url))
        response = session.get(url)

        resultList = response.json()
        for i in resultList['items']:
            sl = i['metadata']['selfLink']
            itemresp = session.get('{}{}'.format(config['server'], sl))
            if itemresp.status_code != 200:
                raise RuntimeError('Error getting {}'.format(sl))

            allitems.append(itemresp.json())

    if 'dest' in config:
        os.chdir(config['dest'])

    processItems(allitems)
