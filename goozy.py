import asyncio
import click
from bleak import BleakScanner
from functools import wraps

def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper

@click.group()
def cli():
    pass

@cli.command()
@coro
async def discover():

    click.echo("[+] Searching for nearby Goozy Light Bars...\n")
    devices = await BleakScanner.discover()

    light_bars = []
    for device in devices:
        if device.name == "Light Bar":
            light_bars.append(device)

    if len(light_bars):
        click.echo("Discovered light bars:")
        for bar in light_bars:
            click.echo("* {}".format(bar.address))

    else:
        click.echo("[-] No light bars discovered. Ensure light bar is on and is not paired with any BLE clients")

    
if __name__ == '__main__':
    cli()