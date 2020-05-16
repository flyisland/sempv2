import click
import logging

from .sempv2_defs import SEMPV2_BASE_PATH
from .util import BROKER_OPTIONS
from .backup import backup
from .delete import delete
from .restore import restore
from .update import update


logging.basicConfig(level=logging.INFO)

@click.group()
@click.option('-u', '--admin-user', default='admin', show_default=True,
    help='The username of the management user')
@click.option('-p', '--admin-password', default='admin', show_default=True,
    envvar='SOL_ADMIN_PWD', help='The password of the management user, could be set by env variable [SOL_ADMIN_PWD]')
@click.option('-h', '--host', default='http://localhost:8080', show_default=True,
    help='URL to access the management endpoint of the broker')
@click.option("--verbose", "-v", is_flag=True, help="Enables verbose mode.")
@click.pass_context
def cli(ctx, admin_user, admin_password, host, verbose):
    """Backing Up and Restoring Solace PubSub+ Configs with SEMPv2 protocol"""

    # Create a sempv2 object and remember it as as the context object.  From
    # this point onwards other commands can refer to it by using the
    # @pass_sempv2 decorator.

    global BROKER_OPTIONS
    BROKER_OPTIONS["config_url"] = host + SEMPV2_BASE_PATH
    BROKER_OPTIONS["admin_user"] = admin_user
    BROKER_OPTIONS["password"] = admin_password
    BROKER_OPTIONS["verbose"] = verbose

@cli.group()
def vpn():
    """Backing Up and Restoring the Setting of PubSub+ VPN"""
    pass

@cli.group()
def cluster():
    """Backing Up and Restoring the Setting of PubSub+ DMR Cluster"""
    pass

# ------------- sub commands of vpn -------------

@vpn.command(name="backup")
@click.argument('vpn_name')
def backup_vpn(vpn_name):
    """Fetches the whole configuration of a VPN"""
    backup("msgVpns", vpn_name)

@vpn.command(name="delete")
@click.confirmation_option()
@click.argument('vpn_name')
@click.option('-c', '--curl-command', default=False, show_default=True, is_flag=True,
    help='Output curl commands only')
def delete_vpn(vpn_name, curl_command):
    """Delete the VPN"""
    delete("msgVpns", vpn_name, curl_command)

@vpn.command(name="restore")
@click.argument('config-file', type=click.Path(exists=True))
@click.option('-c', '--curl-command', default=False, show_default=True, is_flag=True,
    help='Output curl commands only')
def restore_vpn( config_file, curl_command):
    """Restore the VPN with the configuration file"""
    restore("msgVpns", config_file, curl_command)

@vpn.command(name="update")
@click.argument('config-file', type=click.Path(exists=True))
@click.option('-c', '--curl-command', default=False, show_default=True, is_flag=True,
    help='Output curl commands only')
@click.option('-u', '--update-password', default=False, show_default=True, is_flag=True,
    help='Whether to update passwords')
def update_vpn(config_file, curl_command, update_password):
    """Update the VPN with the configuration file"""
    update("msgVpns", config_file, curl_command, update_password)

# ------------- sub commands of cluster -------------

@cluster.command(name="backup")
@click.argument('cluster_name')
def backup_cluster(cluster_name):
    """Fetches the whole configuration of a Cluster"""
    backup("dmrClusters", cluster_name)

@cluster.command(name="delete")
@click.confirmation_option()
@click.argument('cluster_name')
@click.option('-c', '--curl-command', default=False, show_default=True, is_flag=True,
    help='Output curl commands only')
def delete_cluster(cluster_name, curl_command):
    """Delete the Cluster"""
    delete("dmrClusters", cluster_name, curl_command)

@cluster.command(name="restore")
@click.argument('config-file', type=click.Path(exists=True))
@click.option('-c', '--curl-command', default=False, show_default=True, is_flag=True,
    help='Output curl commands only')
def restore_cluster( config_file, curl_command):
    """Restore the Cluster with the configuration file"""
    restore("dmrClusters", config_file, curl_command)

@cluster.command(name="update")
@click.argument('config-file', type=click.Path(exists=True))
@click.option('-c', '--curl-command', default=False, show_default=True, is_flag=True,
    help='Output curl commands only')
@click.option('-u', '--update-password', default=False, show_default=True, is_flag=True,
    help='Whether to update passwords')
def update_cluster(config_file, curl_command, update_password):
    """Update the Cluster with the configuration file"""
    update("dmrClusters", config_file, curl_command, update_password)



if __name__ == '__main__':
    cli()