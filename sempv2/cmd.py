import click
import os

from sempv2.SEMP import SEMPv2

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
    """Backing Up and Restoring Solace PubSub+ VPN Configs with SEMPv2 protocol"""

    # Create a sempv2 object and remember it as as the context object.  From
    # this point onwards other commands can refer to it by using the
    # @pass_sempv2 decorator.

    ctx.obj = SEMPv2(host, admin_user, admin_password)
    ctx.obj.verbose = verbose

@cli.command()
@click.argument('vpn')
@pass_sempv2
def backup(sempv2, vpn):
    """Fetchs the whole configuration of a VPN"""
    sempv2.backup_vpn(vpn)

@cli.command()
@click.confirmation_option()
@click.argument('vpn')
@click.option('-c', '--curl-command', default=False, show_default=True, is_flag=True,
    help='Output curl commands only')
@pass_sempv2
def delete(sempv2, vpn, curl_command):
    """Delete the VPN"""
    sempv2.delete_vpn(vpn, curl_command)

@cli.command()
@click.argument('config-file', type=click.Path(exists=True))
@click.option('-c', '--curl-command', default=False, show_default=True, is_flag=True,
    help='Output curl commands only')
@pass_sempv2
def restore(sempv2, config_file, curl_command):
    """Restore the VPN with the configuration file"""
    sempv2.restore(config_file, curl_command)

@cli.command()
@click.argument('config-file', type=click.Path(exists=True))
@pass_sempv2
def update(sempv2, config_file):
    """Update the VPN with the configuration file"""
    sempv2.update(config_file)


if __name__ == '__main__':
    cli()