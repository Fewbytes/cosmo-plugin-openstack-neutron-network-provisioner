__author__ = 'elip'

import setuptools
setuptools.setup(
    zip_safe=True,
    name='cosmo-plugin-openstack-neutron-network-provisioner',
    version='0.1',
    author='Ilya Sher',
    author_email='ilya@fewbytes.com',
    packages=['openstack_neutron_network_provisioner'],
    license='LICENSE',
    description='Plugin for provisioning OpensTack Neutron network',
    install_requires=[
        "celery",
        "python-keystoneclient",
		"python-neutronclient",
    ]
)
