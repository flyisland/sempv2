import click
import logging

from .sempv2_defs import *
from .util import BROKER_OPTIONS
from .backup import backup
from .delete import delete
from .restore import restore
from .update import update


logging.basicConfig(level=logging.INFO)

@click.group()
@click.version_option()
@click.option('-u', '--admin-user', default='admin', show_default=True,
    help='The username of the management user')
@click.option('-p', '--admin-password', default='admin', show_default=True,
    envvar='SOL_ADMIN_PWD', help='The password of the management user, could be set by env variable [SOL_ADMIN_PWD]')
@click.option('-h', '--host', default='http://localhost:8080', show_default=True,
    help='URL to access the management endpoint of the broker')
@click.option('--curl-only', default=False, show_default=True, is_flag=True,
    help='Output curl commands only, no effect on BACKUP command')
@click.option("--verbose", "-v", is_flag=True, help="Enables verbose mode.")
@click.pass_context
def cli(ctx, admin_user, admin_password, host, curl_only, verbose):
    """Backing Up and Restoring Solace PubSub+ Configs with SEMPv2 protocol"""

    # Create a sempv2 object and remember it as as the context object.  From
    # this point onwards other commands can refer to it by using the
    # @pass_sempv2 decorator.

    global BROKER_OPTIONS

    if host[-1]=='/':
        host=host[:-1]

    BROKER_OPTIONS["host"] = host
    BROKER_OPTIONS["config_url"] = host + SEMPV2_BASE_PATH
    BROKER_OPTIONS["admin_user"] = admin_user
    BROKER_OPTIONS["password"] = admin_password
    BROKER_OPTIONS["verbose"] = verbose
    BROKER_OPTIONS["curl_only"] = curl_only

    init_object_definitions(BROKER_OPTIONS)

@cli.group()
def vpn():
    """Back up and Restore the Setting of PubSub+ VPN"""
    pass

@cli.group()
def cluster():
    """Back up and Restore the Setting of PubSub+ DMR Cluster"""
    pass

# ------------- sub commands of vpn -------------

@vpn.command(name="backup")
@click.argument('vpn_name')
@click.option('--remove-default-value', default=False, show_default=True, is_flag=True,
    help='Remove the attributes with default value to make the result JSON more concise')
@click.option('--reserve-deprecated', default=False, show_default=True, is_flag=True,
    help='Reserve the deprecated attributes for possible backward compatibility')
def backup_vpn(vpn_name, remove_default_value, reserve_deprecated):
    """Fetches the whole configuration of a VPN"""
    backup("msgVpns", vpn_name, remove_default_value, reserve_deprecated)

@vpn.command(name="delete")
@click.confirmation_option()
@click.argument('vpn_name')
def delete_vpn(vpn_name):
    """Delete the VPN"""
    delete("msgVpns", vpn_name)

@vpn.command(name="restore")
@click.argument('config-file', type=click.Path(exists=True))
def restore_vpn( config_file):
    """Restore the VPN with the configuration file"""
    restore("msgVpns", config_file)

@vpn.command(name="update")
@click.argument('config-file', type=click.Path(exists=True))
@click.option('--update-password', default=False, show_default=True, is_flag=True,
    help='Whether to update passwords')
def update_vpn(config_file, update_password):
    """Update the VPN with the configuration file"""
    update("msgVpns", config_file, update_password)

# ------------- sub commands of cluster -------------

@cluster.command(name="backup")
@click.option('--remove-default-value', default=False, show_default=True, is_flag=True,
    help='Remove the attributes with default value to make the result JSON more concise')
@click.option('--reserve-deprecated', default=False, show_default=True, is_flag=True,
    help='Reserve the deprecated attributes for possible backward compatibility')
def backup_cluster(remove_default_value, reserve_deprecated):
    """Fetches the whole configuration of a Cluster"""

    cluster_name = get_object_identifiers("dmrClusters")[0]
    backup("dmrClusters", cluster_name, remove_default_value, reserve_deprecated)

@cluster.command(name="delete")
@click.confirmation_option()
def delete_cluster():
    """Delete the Cluster"""
    cluster_name = get_object_identifiers("dmrClusters")[0]
    click.echo("Deleting cluster '{}'".format(cluster_name))
    delete("dmrClusters", cluster_name)

@cluster.command(name="restore")
@click.argument('config-file', type=click.Path(exists=True))
def restore_cluster( config_file):
    """Restore the Cluster with the configuration file"""
    restore("dmrClusters", config_file)

@cluster.command(name="update")
@click.argument('config-file', type=click.Path(exists=True))
@click.option('--update-password', default=False, show_default=True, is_flag=True,
    help='Whether to update passwords')
def update_cluster(config_file, update_password):
    """Update the Cluster with the configuration file"""
    update("dmrClusters", config_file, update_password)



if __name__ == '__main__':
    cli()