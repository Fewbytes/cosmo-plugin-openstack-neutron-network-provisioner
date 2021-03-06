# vim: ts=4 sw=4 et

# Standard
import json
import os

# Celery
from celery import task

# OpenStack
import keystoneclient.v2_0.client as ksclient
from neutronclient.neutron import client

# Cosmo
from cosmo.events import send_event, get_cosmo_properties

@task
def provision(__cloudify_id, network, **kwargs):
    neutron_client = _init_client()
    if _get_network_by_name(neutron_client, network['name']):
        raise RuntimeError("Can not provision network with name '{0}' because network with such name already exists"
                           .format(network['name']))

    neutron_client.create_network({
        'network': {
            'name': network['name'],
            'admin_state_up': True
        }
    })
    # XXX: not really a host, signifies event origin name for riemann
    host = get_cosmo_properties()['ip']
    # TODO: change host to "network-NAME"
    send_event(__cloudify_id, host, "network status", "state", "running")

@task
def start(network, **kwargs):
    neutron_client = _init_client()
    net = _get_network_by_name(neutron_client, network['name'])
    neutron_client.update_network(net['id'], {
        'network': {
            'admin_state_up': True
        }
    })

@task
def stop(network, **kwargs):
    neutron_client = _init_client()
    net = _get_network_by_name(neutron_client, network['name'])
    neutron_client.update_network(net['id'], {
        'network': {
            'admin_state_up': False
        }
    })


@task
def terminate(network, **kwargs):
    neutron_client = _init_client()
    net = _get_network_by_name(neutron_client, network['name'])
    neutron_client.delete_network(net['id'])


# TODO: cache the token, cache client
def _init_client():
    config_path = os.getenv('NEUTRON_CONFIG_PATH', os.path.expanduser('~/neutron_config.json'))
    with open(config_path) as f:
        neutron_config = json.loads(f.read())

    keystone_client = _init_keystone_client()

    neutron_client = client.Client('2.0', endpoint_url=neutron_config['url'], token=keystone_client.auth_token)
    neutron_client.format = 'json'
    return neutron_client


def _init_keystone_client():
    config_path = os.getenv('KEYSTONE_CONFIG_PATH', os.path.expanduser('~/keystone_config.json'))
    with open(config_path) as f:
        cfg = json.loads(f.read())
    # Not the same config as nova client. Same parameters, different names.
    args = {field: cfg[field] for field in ('username', 'password', 'tenant_name', 'auth_url')}
    return ksclient.Client(**args)


def _get_network_by_name(neutron_client, name):
    # TODO: check whether neutron_client can get networks only named `name`
    matching_networks = neutron_client.list_networks(name=name)['networks']

    if len(matching_networks) == 0:
        return None
    if len(matching_networks) == 1:
        return matching_networks[0]
    raise RuntimeError("Lookup of network by name failed. There are {0} networks named '{1}'"
                       .format(len(matching_networks), name))


def _get_network_by_name_or_fail(neutron_client, name):
    network = _get_network_by_name(neutron_client, name)
    if network:
        return network
    raise ValueError("Lookup of network by name failed. Could not find a network with name {0}".format(name))


if __name__ == '__main__':
    neutron_client = _init_client()
    json.dumps(neutron_client.list_networks(), indent=4, sort_keys=True)
