# Copyright 2015 VMware, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
NSX data models.

This module defines data models used by the VMware NSX plugin family.

"""

import sqlalchemy as sa

from sqlalchemy import orm

from neutron.db import model_base
from neutron.db import models_v2


class NetworkConnection(model_base.BASEV2, models_v2.HasTenant):
    """Defines a connection between a network gateway and a network."""
    # We use port_id as the primary key as one can connect a gateway
    # to a network in multiple ways (and we cannot use the same port form
    # more than a single gateway)
    network_gateway_id = sa.Column(sa.String(36),
                                   sa.ForeignKey('networkgateways.id',
                                                 ondelete='CASCADE'))
    network_id = sa.Column(sa.String(36),
                           sa.ForeignKey('networks.id', ondelete='CASCADE'))
    segmentation_type = sa.Column(
        sa.Enum('flat', 'vlan',
                name='networkconnections_segmentation_type'))
    segmentation_id = sa.Column(sa.Integer)
    __table_args__ = (sa.UniqueConstraint(network_gateway_id,
                                          segmentation_type,
                                          segmentation_id),
                      model_base.BASEV2.__table_args__)
    # Also, storing port id comes back useful when disconnecting a network
    # from a gateway
    port_id = sa.Column(sa.String(36),
                        sa.ForeignKey('ports.id', ondelete='CASCADE'),
                        primary_key=True)


class NetworkGatewayDeviceReference(model_base.BASEV2):
    id = sa.Column(sa.String(36), primary_key=True)
    network_gateway_id = sa.Column(sa.String(36),
                                   sa.ForeignKey('networkgateways.id',
                                                 ondelete='CASCADE'),
                                   primary_key=True)
    interface_name = sa.Column(sa.String(64), primary_key=True)


class NetworkGatewayDevice(model_base.BASEV2, models_v2.HasId,
                           models_v2.HasTenant):
    nsx_id = sa.Column(sa.String(36))
    # Optional name for the gateway device
    name = sa.Column(sa.String(255))
    # Transport connector type. Not using enum as range of
    # connector types might vary with backend version
    connector_type = sa.Column(sa.String(10))
    # Transport connector IP Address
    connector_ip = sa.Column(sa.String(64))
    # operational status
    status = sa.Column(sa.String(16))


class NetworkGateway(model_base.BASEV2, models_v2.HasId,
                     models_v2.HasTenant):
    """Defines the data model for a network gateway."""
    name = sa.Column(sa.String(255))
    # Tenant id is nullable for this resource
    tenant_id = sa.Column(sa.String(36))
    default = sa.Column(sa.Boolean())
    devices = orm.relationship(NetworkGatewayDeviceReference,
                               backref='networkgateways',
                               cascade='all,delete')
    network_connections = orm.relationship(NetworkConnection, lazy='joined')


class MacLearningState(model_base.BASEV2):

    port_id = sa.Column(sa.String(36),
                        sa.ForeignKey('ports.id', ondelete="CASCADE"),
                        primary_key=True)
    mac_learning_enabled = sa.Column(sa.Boolean(), nullable=False)

    # Add a relationship to the Port model using the backref attribute.
    # This will instruct SQLAlchemy to eagerly load this association.
    port = orm.relationship(
        models_v2.Port,
        backref=orm.backref("mac_learning_state", lazy='joined',
                            uselist=False, cascade='delete'))


class LsnPort(models_v2.model_base.BASEV2):

    __tablename__ = 'lsn_port'

    lsn_port_id = sa.Column(sa.String(36), primary_key=True)

    lsn_id = sa.Column(sa.String(36),
                       sa.ForeignKey('lsn.lsn_id', ondelete="CASCADE"),
                       nullable=False)
    sub_id = sa.Column(sa.String(36), nullable=False, unique=True)
    mac_addr = sa.Column(sa.String(32), nullable=False, unique=True)

    def __init__(self, lsn_port_id, subnet_id, mac_address, lsn_id):
        self.lsn_port_id = lsn_port_id
        self.lsn_id = lsn_id
        self.sub_id = subnet_id
        self.mac_addr = mac_address


class Lsn(models_v2.model_base.BASEV2):
    __tablename__ = 'lsn'

    lsn_id = sa.Column(sa.String(36), primary_key=True)
    net_id = sa.Column(sa.String(36), nullable=False)

    def __init__(self, net_id, lsn_id):
        self.net_id = net_id
        self.lsn_id = lsn_id
