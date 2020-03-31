from __future__ import print_function
import os,sys
sys.path.append(os.environ.get('PROJECT_DIR','..'))
import re
import click
import dl_exporter.exporter as exporter
import dl_exporter.config as c
import dl_exporter.gee as gee
#
# DEFAULTS
#
IS_DEV=c.get('is_dev')
NOISY=c.get('noisy')
LIMIT=c.get('limit')
CHECK_EXT=c.get('check_ext')

RUN_HELP='run export: `$dl_exporter run <geojson-file/tiles-pickle> (<config-file>)`'
ECHO_HELP='print config: `$dl_exporter echo <geojson-file/tiles-pickle> (<config-file>)`'
MANIFEST_HELP='generate gee-manifest: `$dl_exporter manifiest <manifiest-config-file> <uris-file> <destination>`'
CONFIG_HELP='generate config file: pass kwargs (ie $`dl_exporter config dev=true noisy=false)`'
DEV_HELP='<bool> run without performing export'
NOISE_HELP='<bool> be noisy'
LIMIT_HELP='<int> limit number of exports'
MANIFEST_LIMIT_HELP='<int> limit number of uris for dev'
CHECK_EXT_HELP='<bool> if true add `.yaml` if not included in config arg'
ARG_KWARGS_SETTINGS={
    'ignore_unknown_options': True,
    'allow_extra_args': True
}
PRETTY_HELP='<bool> if pretty indent json file'
PRETTY=False



#
# CLI INTERFACE
#
@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj={}


@click.command(
    help=RUN_HELP,
    context_settings=ARG_KWARGS_SETTINGS ) 
@click.argument('geometry',type=str)
@click.argument('config',type=str,required=False)
@click.option(
    '--dev',
    help=DEV_HELP,
    default=IS_DEV,
    type=bool)
@click.option(
    '--noisy',
    help=NOISE_HELP,
    default=NOISY,
    type=bool)
@click.option(
    '--limit',
    help=LIMIT_HELP,
    default=LIMIT,
    type=int)
@click.option(
    '--check_ext',
    help=CHECK_EXT_HELP,
    default=CHECK_EXT,
    type=bool)
@click.pass_context
def run(ctx,geometry,config,dev,noisy,limit,check_ext):
    exporter.run(
        geometry=geometry,
        config=config,
        dev=dev,
        noisy=noisy,
        limit=limit,
        check_ext=check_ext)




@click.command(
    help=MANIFEST_HELP,
    context_settings=ARG_KWARGS_SETTINGS ) 
@click.argument('config',type=str)
@click.argument('uris',type=str)
@click.argument('dest',type=str)
@click.option(
    '--pretty',
    help=PRETTY_HELP,
    default=PRETTY,
    type=bool)
@click.option(
    '--noisy',
    help=NOISE_HELP,
    default=NOISY,
    type=bool)
@click.option(
    '--limit',
    help=MANIFEST_LIMIT_HELP,
    default=LIMIT,
    type=int)
@click.pass_context
def manifest(ctx,config,uris,dest,pretty,noisy,limit):
    gee.generate_manifest(
        config=config,
        uris=uris,
        dest=dest,
        pretty=pretty,
        noisy=noisy,
        limit=limit)



@click.command(
    help=ECHO_HELP,
    context_settings=ARG_KWARGS_SETTINGS ) 
@click.argument('geometry',type=str)
@click.argument('config',type=str,required=False)
@click.option(
    '--check_ext',
    help=CHECK_EXT_HELP,
    default=CHECK_EXT,
    type=bool)
@click.pass_context
def echo(ctx,geometry,config,check_ext):
    exporter.echo(
        geometry=geometry,
        config=config,
        check_ext=check_ext)




@click.command(
    name='config',    
    help=CONFIG_HELP,
    context_settings=ARG_KWARGS_SETTINGS ) 
@click.option(
    '--info',
    '-i',
    is_flag=True,
    help='print current or default config',
    type=bool)
@click.option(
    '--force',
    '-f',
    default=False,
    help='if true overwrite existing config',
    type=bool)
@click.pass_context
def generate_config(ctx,info,force):
    if info:
        print("dl_exporter.config:")
        for key in c.CONFIG:
            print("\t{}: {}".format(key,c.CONFIG[key]))
    else:
        _,kwargs=_args_kwargs(ctx.args)
        c.generate( force=force, **kwargs )






#
# HELPERS
#
def _args_kwargs(ctx_args):
    args=[]
    kwargs={}
    for a in ctx_args:
        if re.search('=',a):
            k,v=a.split('=')
            kwargs[k]=v
        else:
            args.append(a)
    return args,kwargs


#
# MAIN
#
cli.add_command(run)
cli.add_command(echo)
cli.add_command(manifest)
cli.add_command(generate_config)
if __name__ == "__main__":
    cli()

