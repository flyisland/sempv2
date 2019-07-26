import click
import os

@click.group()
@click.option('-u', '--admin-user', default='admin', show_default=True,
    help='The username of the management user')
@click.option('-p', '--password', prompt="Admin Password", hide_input=True,
    envvar='SOL_ADMIN_PWD', help='The password of the management user, could be set by env variable [SOL_ADMIN_PWD]')
@click.option('-h', '--host', required=True,
    help='URL to access the management endpoint of the broker')
@click.pass_context
def cli(ctx, admin_user, password, host):
    """Backing Up and Restoring Solace PubSub+ VPN Configs with SEMPv2 protocol"""
    ctx.ensure_object(dict)

    ctx.obj['admin_user'] = admin_user
    ctx.obj['password'] = password
    ctx.obj['host'] = host

@cli.command()
@click.argument('vpn')
@click.pass_context
def backup(ctx, vpn):
    """Fetch the whole configuration of a VPN"""
    click.echo('Accessing %s:%s@%s' % (ctx.obj['admin_user'], ctx.obj['password'], ctx.obj['host']))
    click.echo('vpn is :%s' % vpn)

@cli.command()
@click.argument('config-file', type=click.Path(exists=True))
def restore(config_file):
    """Restore the VPN with the configuration file"""
    click.echo(click.format_filename(config_file))
