import click
import logging

from .sempv2_defs import SEMPV2_BASE_PATH, init_object_definitions
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

    init_object_definitions(BROKER_OPTIONS)

@cli.group()
def vpn():
    """Backing Up and Restoring Solace PubSub+ VPN"""
    pass

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


if __name__ == '__main__':
    cli()