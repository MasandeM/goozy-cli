import asyncio
import click
import os
import colorsys
from configparser import ConfigParser
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
@click.option('--brightness')
@coro
async def control(address, on, off, color, brightness):
    
    client = BleakClient(address)
    try:
        await client.connect()
        config_file_path = 'config.ini'
        config = ConfigParser()

        if os.path.isfile(config_file_path):
            config.read(config_file_path)
        else:
            config.add_section(address)

        if on:
            await client.write_gatt_char(LIGHTS_CHARACTERISTIC, bytes.fromhex("A06904FFFFFFFF"))

        elif off:
            await client.write_gatt_char(LIGHTS_CHARACTERISTIC, bytes.fromhex("A06904000000FF"))

        if color:
            if color in COLORS.keys():                
                hexcolor = COLORS[color]
                ble_command = "A06904{}FF".format(hexcolor)

                await client.write_gatt_char(LIGHTS_CHARACTERISTIC, bytes.fromhex(ble_command))
                config.set(address, 'hexcolor',  hexcolor)

        if brightness:
            hexcolor = config.get(address, 'hexcolor')
            value = str(adjust_brightness(hexcolor, int(brightness)/100))
            ble_command = "A06904{}FF".format(value)
            await client.write_gatt_char(LIGHTS_CHARACTERISTIC, bytes.fromhex(ble_command))

        await asyncio.sleep(2)
    finally:
        await client.disconnect()
        with open(config_file_path, 'w') as f:
            print(config)
            config.write(f)

def adjust_brightness(hex_color, brightness):

    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    hsb = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)

    adjusted_hsb = tuple([hsb[0], hsb[1], hsb[2] * brightness])
    adjusted_rgb = colorsys.hsv_to_rgb(adjusted_hsb[0], adjusted_hsb[1], adjusted_hsb[2])

    return '{:02x}{:02x}{:02x}'.format(int(adjusted_rgb[0]*255), int(adjusted_rgb[1]*255), int(adjusted_rgb[2]*255))

if __name__ == '__main__':
    cli()