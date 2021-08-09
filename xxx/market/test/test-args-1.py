#!/usr/bin/env python
import click
import json

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--option', help='Whatever')
def do_stuff(option):
    try:
        option = json.loads(option)
        # option = str(option)  # this also works
    except ValueError:
        pass

    option = option[1:-1]  # trim '[' and ']'

    options = option.split(',')
    # for opt in options:
        

    for i, value in enumerate(options):
        # catch integers
        try:
            int(value)
        except ValueError:
            options[i] = value
        else:
            options[i] = int(value)

    for option in options:
        print(option)
    # Here use options as you need

# do stuff
if __name__ == '__main__':
    do_stuff()