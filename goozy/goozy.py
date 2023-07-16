import asyncio
import click
from bleak import BleakScanner, BleakClient
from functools import wraps

LIGHTS_CHARACTERISTIC = "0000ffe1-0000-1000-8000-00805f9b34fb"
COLORS = {
    'white':'FFFFFF',
    'silver':'C0C0C0',
    'gray':'808080',
    'black':'000000',
    'red':'FF0000',
    'maroon':'800000',
    'yellow':'FFFF00',
    'olive':'808000',
    'lime':'00FF00',
    'green':'008000',
    'aqua':'00FFFF',
    'teal':'008080',
    'blue':'0000FF',
    'navy':'000080',
    'fuchsia':'FF00FF',
    'purple':'800080'
}

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

@cli.command()
@click.option('--address', required=True)
@click.option('--on', default=False, is_flag=True, flag_value=True)
@click.option('--off', default=False, is_flag=True, flag_value=True)
@click.option('--color')
@coro
async def control(address, on, off, color):
    
    client = BleakClient(address)
    try:
        await client.connect()
        if on:
            await client.write_gatt_char(LIGHTS_CHARACTERISTIC, bytes.fromhex("A06904FFFFFFFF"))
        elif off:
            await client.write_gatt_char(LIGHTS_CHARACTERISTIC, bytes.fromhex("A06904000000FF"))
        elif color:
            if color in COLORS.keys():                
                hexcolor = "A06904{}FF".format(COLORS[color])
                await client.write_gatt_char(LIGHTS_CHARACTERISTIC, bytes.fromhex(hexcolor))

        await asyncio.sleep(2)
    finally:
        await client.disconnect()

if __name__ == '__main__':
    cli()