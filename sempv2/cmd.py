import click
import os

from sempv2.SEMP import SEMPv2

@click.group()
@click.option('-u', '--admin-user', default='admin', show_default=True,
    help='The username of the management user')
@click.option('-p', '--admin-password', default='admin', show_default=True,
    envvar='SOL_ADMIN_PWD', help='The password of the management user, could be set by env variable [SOL_ADMIN_PWD]')
@click.option('-h', '--host', default='http://localhost:8080', show_default=True,
    help='URL to access the management endpoint of the broker')
@click.pass_context
def cli(ctx, admin_user, admin_password, host):
    """Backing Up and Restoring Solace PubSub+ VPN Configs with SEMPv2 protocol"""
    ctx.ensure_object(dict)

    ctx.obj['admin_user'] = admin_user
    ctx.obj['password'] = admin_password
    ctx.obj['host'] = host

@cli.command()
@click.argument('vpn')
@click.pass_context
def backup(ctx, vpn):
    """Fetch the whole configuration of a VPN"""
    s2 = SEMPv2(ctx.obj['host'], ctx.obj['admin_user'], ctx.obj['password'])
    s2.backup_vpn(vpn)

@cli.command()
@click.argument('config-file', type=click.Path(exists=True))
@click.pass_context
def restore(ctx, config_file):
    """Restore the VPN with the configuration file"""
    s2 = SEMPv2(ctx.obj['host'], ctx.obj['admin_user'], ctx.obj['password'])
    s2.restore(config_file)

if __name__ == '__main__':
    cli()