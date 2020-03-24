from __future__ import print_function
import os,sys
sys.path.append(os.environ.get('PROJECT_DIR','..'))
import re
import click
import dl_exporter.exporter as exporter
import dl_exporter.config as c
#
# DEFAULTS
#
IS_DEV=c.get('is_dev')
NOISY=c.get('noisy')
LIMIT=c.get('limit')
CHECK_EXT=c.get('check_ext')

DEV_HELP='<bool> run without performing export'
NOISE_HELP='<bool> be noisy'
LIMIT_HELP='<int> limit number of exports'
CHECK_EXT_HELP='<bool> if true add `.yaml` if not included in config arg'
ARG_KWARGS_SETTINGS={
    'ignore_unknown_options': True,
    'allow_extra_args': True
}




#
# CLI INTERFACE
#
@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj={}


@click.command(
    help='run exoprt: `$dl_exporter run <export-job-config>`',
    context_settings=ARG_KWARGS_SETTINGS ) 
@click.argument('job',type=str)
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
def run(ctx,job,dev,noisy,limit,check_ext):
    exporter.run(
        job=job,
        dev=dev,
        noisy=noisy,
        limit=limit,
        check_ext=check_ext)




@click.command(
    help='print job: `$dl_exporter echo <export-job-config>`',
    context_settings=ARG_KWARGS_SETTINGS ) 
@click.argument('job',type=str)
@click.option(
    '--check_ext',
    help=CHECK_EXT_HELP,
    default=CHECK_EXT,
    type=bool)
@click.pass_context
def echo(ctx,job,check_ext):
    exporter.echo(
        job=job,
        check_ext=check_ext)




@click.command(
    name='config',    
    help='generate config file: pass kwargs (ie $`dl_exporter config dev=true noisy=false)`',
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
cli.add_command(generate_config)
if __name__ == "__main__":
    cli()

