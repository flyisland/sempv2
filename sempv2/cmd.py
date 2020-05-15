import click
import os

from sempv2.SEMP import SEMPv2
from .sempv2_defs import SEMPV2_BASE_PATH
from .util import BROKER_OPTIONS
from .backup import backup_vpn
from .delete import delete_vpn

pass_sempv2 = click.make_pass_decorator(SEMPv2)

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
    ctx.obj = SEMPv2(host, admin_user, admin_password)
    ctx.obj.verbose = verbose

@cli.group()
@click.pass_context
def vpn(ctx):
    """Backing Up and Restoring Solace PubSub+ VPN"""
    pass

@vpn.command()
@click.argument('vpn_name')
def backup(vpn_name):
    """Fetches the whole configuration of a VPN"""
    backup_vpn(vpn_name)

@vpn.command()
@click.confirmation_option()
@click.argument('vpn_name')
@click.option('-c', '--curl-command', default=False, show_default=True, is_flag=True,
    help='Output curl commands only')
def delete(vpn_name, curl_command):
    """Delete the VPN"""
    delete_vpn(vpn_name, curl_command)



@vpn.command()
@click.argument('vpn_name')
@pass_sempv2
def backupVPN(sempv2, vpn_name):
    """Fetches the whole configuration of a VPN"""
    sempv2.backup_vpn(vpn_name)

@vpn.command()
@click.confirmation_option()
@click.argument('vpn_name')
@click.option('-c', '--curl-command', default=False, show_default=True, is_flag=True,
    help='Output curl commands only')
@pass_sempv2
def deleteVPN(sempv2, vpn_name, curl_command):
    """Delete the VPN"""
    sempv2.delete_vpn(vpn_name, curl_command)

@vpn.command()
@click.argument('config-file', type=click.Path(exists=True))
@click.option('-c', '--curl-command', default=False, show_default=True, is_flag=True,
    help='Output curl commands only')
@pass_sempv2
def restoreVPN(sempv2, config_file, curl_command):
    """Restore the VPN with the configuration file"""
    sempv2.restore(config_file, curl_command)

@vpn.command()
@click.argument('config-file', type=click.Path(exists=True))
@click.option('-c', '--curl-command', default=False, show_default=True, is_flag=True,
    help='Output curl commands only')
@click.option('-u', '--update-password', default=False, show_default=True, is_flag=True,
    help='Whether to update passwords')
@pass_sempv2
def updateVPN(sempv2, config_file, curl_command, update_password):
    """Update the VPN with the configuration file"""
    sempv2.update(config_file, curl_command, update_password)


if __name__ == '__main__':
    cli()