"""
Script Name:    xtreamPOC.py
Description:    Proof of Concept of Xtream Codes Portal using PyXtream.
                It loads a simple page to search and play your content.
Author:         Mario Montoya <marioSGHT500@gmail.com>
Date:           2024-06-12

Version History:
- v0.1 (2024-06-12): It uses pyXtream, mpv and nicegui.
- v0.2 (2024-09-15): Adds "Replay" switch to replay stream when it fails.
- v0.3 (2024-09-30): Supports multiple IPTV providers with default selection.
- v0.4 (2024-10-01): Fixes the 403 error when trying to get series info.
- v0.5 (2024-10-04): Fixes the "stream_type" missing key when searching series.
- v0.6 (2024-10-05): Adds the "Record" option.

Copyright 2024 Mario Montoya

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
from pyxtream import XTream
from pyxtream.pyxtream import Serie, Episode
import requests
import platform
import subprocess
from nicegui import ui
import random
import asyncio
import json
from pytimedinput import timedKey
from datetime import datetime
# TODO Remove duplicate streams, like movies.

# Open the "xtreamPOC.json" file and fill in:
#   * The path to the mpv.exe file in Windows
#   * The path so save streams in Windows
#   * The path so save streams in macOS or Linux
#   * Your Xtream Provider credentials.

def open_stream_url(url, count):
    # Builds the stream-record argument
    stream_record = ""
    if record.value:
        # Builds the file name:
        extension = url[url.rfind('.') + 1:]
        now = datetime.now()
        julian_date_time = now.strftime('%Y%j_%H%M_')
        short_julian_time = julian_date_time[-10:]
        filename = f"{short_julian_time}{count:03}.{extension}"
        if platform.system() == "Windows":
            stream_record = f"--stream-record={mpv_rec_win}{filename}"
        elif platform.system() == "Darwin" or platform.system() == "Linux":  # macOS or Linux
            stream_record = f"--stream-record={mpv_rec_linux}{filename}"
    # Specify the command-line arguments
    args = ['--slang=eng', '--alang=eng', '--fullscreen', stream_record, url]
    # Run the mpv command
    if platform.system() == "Windows":
        subprocess.run([mpv_path] + args)
    elif platform.system() == "Darwin" or platform.system() == "Linux":  # macOS or Linux
        subprocess.run(['mpv'] + args)
    else:
        raise OSError("Unsupported operating system")

def get_gerund_and_color_from_record_value():
    if record.value:
        gerund = "Recording"
        color="red"
    else:
        gerund = "Playing"
        color=""
    return (gerund, color)

async def play_stream_id(stream_id, streams):
    gerund, color = get_gerund_and_color_from_record_value()
    played = False
    for stream in streams:
        if stream_id == stream.get('stream_id', 0) and not played:
            print(f"{gerund} {stream['name']}")
            ui.notify(f"{gerund} {stream['name']}", color=color)
            count = 1
            while True:
                await asyncio.to_thread(open_stream_url, stream['url'], count)
                if not replay.value or not stream.get("stream_type", "") == "live":
                    break
                count = count + 1
            played = True

async def play_episode_id(episode_id, episodes):
    gerund, color = get_gerund_and_color_from_record_value()
    for episode_obj in episodes:
        if episode_obj.id == episode_id:
            print(f"{gerund} {episode_obj.title}")
            ui.notify(f"{gerund} {episode_obj.title}", color=color)
            await asyncio.to_thread(open_stream_url, episode_obj.url, 1)

def is_valid_image_url(url):
    try:
        response = requests.head(url, allow_redirects=True)
        # Check if the response is successful and the content type is an image
        if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
            return True
    except requests.RequestException:
        return False
    return False

def add_card(stream_type, stream_id, stream_name, stream_icon, streams):
    with channel_row:
        with ui.card().tight().style('width: 290px;height: 320px;') \
                .on("click", lambda: play_stream_id(stream_id, streams=streams)).classes('cursor-pointer'):
            if stream_icon and is_valid_image_url(stream_icon):
                image_url = stream_icon
            else:
                image_url = f'https://picsum.photos/360/540?random={random.randint(1, 100)}'
            ui.image(image_url)
            with ui.card_section():
                ui.label(f'{stream_name} - {stream_type}')

def add_label(episode_obj, episodes):
    ui.label(episode_obj.title).on("click", \
            lambda: play_episode_id(episode_obj.id, episodes)).classes('cursor-pointer')

async def ui_search_stream():
    channel_row.clear()
    serie_row.clear()
    # Search for streams by name
    search_string = search_input.value
    streams = xt.search_stream(r"^.*{}.*$".format(search_string))
    # Initialize the info_urls
    info_urls = []
    # Iterates the streams
    print("Type - Stream Id - Name", end="")
    for stream in streams:
        stream_type = stream.get('stream_type', 'series')
        if stream_type == 'series':
            series_id = stream['series_id']
            info_url = xt.get_series_info_URL_by_ID(series_id)
            # Add series_id without repetition
            if info_url not in info_urls:
                info_urls.append(info_url)
        else:
            print('')
            print(f"{stream_type} - {stream['stream_id']} - {stream['name']}", end="")
            add_card(stream_type, stream['stream_id'], stream['name'], stream['stream_icon'], streams=streams)
            ui.update() # Required in slower PCs.
            await asyncio.sleep(.25) # Required for ui self-refresh.
    print('')

    # Innitialize episodes. This is needed to play them later.
    episodes = []

    for info_url in info_urls:
        # Make the request to the URL with suitable User-Agent to fix 403 error.
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(info_url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
        else:
            print(f"Failed to retrieve data from '{info_url}'. Status code: {response.status_code}")
            continue

        # Get the Serie "info"
        serie_info = data.get('info', {})
        serie_obj = Serie(xt, series_info=serie_info)

        # Print the series name and some info
        print('*****************************************************************************************')
        print(serie_obj.name)
        print(serie_obj.genre)
        if serie_obj.plot is not None:
            print(serie_obj.plot)
        print('*****************************************************************************************')
        print('Stream Id - Title')

        # Starts the Serie Card
        with serie_row:
            with ui.card().tight().style('width: 49%;'):
                logo = serie_obj.logo
                if logo and is_valid_image_url(logo):
                    image_url = logo
                else:
                    image_url = f'https://picsum.photos/360/540?random={random.randint(1, 100)}'
                ui.image(image_url)
                with ui.card_section():
                    ui.label(serie_obj.name)
                    ui.label(serie_obj.genre)
                    if serie_obj.plot is not None:
                        ui.label(serie_obj.plot)

                # Get the Serie "seasons"
                seasons_data = data.get('seasons', [])

                # Get the Serie "episodes"
                episodes_data = data.get('episodes', {})

                for season in seasons_data:
                    season_number = season.get('season_number', None)
                    season_name = season.get('name', None)
                    episodes_raw_data = episodes_data.get(f"{season_number}", [])
                    if episodes_raw_data:
                        print(season_name)
                        with ui.card_section():
                            ui.label(season_name).style('font-weight: bold')
                            for episode in episodes_raw_data:
                                episode_obj = Episode(xt, series_info=serie_info, group_title='dummy', episode_info=episode)
                                print(f"{episode_obj.id} - {episode_obj.title}")
                                episodes.append(episode_obj) # Required to play it back
                                add_label(episode_obj, episodes)
                                await asyncio.sleep(.01) # Required for ui self-refresh.

# Page title and search row
ui.page_title('xtreamPOC - sght500')
with ui.row().style('width: 100%;') as search_row:
    search_input = ui.input("Enter name to search:", placeholder="For Example: Game of Thrones").style('width: 63%;')
    ui.button('Search', on_click=lambda: asyncio.create_task(ui_search_stream())).style('width: 16%;')
    replay = ui.switch("Replay").style('width: 8%;')
    record = ui.checkbox("Record").style('width: 8%; font-weight: bold; color: red')
# Two result rows
channel_row = ui.row()
serie_row = ui.row()
ui.run()

# The startup notice
print("""xtreamPOC: A proof of concept of Xtream Portal Codes using pyXtream, mpv and nicegui.
Copyright (C) 2024  Mario Montoya

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Mario Montoya <marioSGHT500@gmail.com>
""")

# Load JSON configuration file
with open('xtreamPOC.json', 'r') as file:
    config = json.load(file)
mpv_path = config['mpv_path']
mpv_rec_win = config['mpv_rec_win']
mpv_rec_linux = config['mpv_rec_linux']
providers = config['iptv_providers']
time_out = config['time_out']
default = config['default']
shift_19 = config['shift_1-9']

# Check if there's a default override
try:
    with open('default_override.json', 'r') as file:
        config = json.load(file)
    default_override = config['default_override']
    default = default_override
except FileNotFoundError:
    pass

print(f"Available providers: (Select with <Shift> to override default.) You have {time_out} seconds to select.")
print("-------------------------------------------------")
options = ""
for i, provider in enumerate(providers):
    options = options + str(i + 1)
    if default == str(i + 1):
        print(f"{i + 1}. {provider['provider_name']} (*)")
    else:
        print(f"{i + 1}. {provider['provider_name']}")

key_options = options + shift_19[0:len(options)]
userOption, timedOut = timedKey(f"Select provider [{options}]: ", timeout=time_out, allowCharacters=key_options)
if timedOut:
    userOption = default

# Check if the user wants to override the default provider
pos = shift_19.find(userOption)
if pos >= 0:
    default_override = options[pos]
    default_dict = {
        "default_override": default_override
    }
    with open("default_override.json", "w") as file:
        json.dump(default_dict, file)
    userOption = default_override

provider = providers[int(userOption) - 1]
provider_name = provider['provider_name']
username = provider['username']
password = provider['password']
provider_url = provider['provider_url']

print("-------------------------------------------------")
print(f"Selected provider: {userOption}. {provider_name}")
print("")

# Innitializes xt and connects to your selected IPTV provider
try:
    xt = XTream(provider_name, username, password, provider_url)
    if xt.auth_data != {}:
        xt.load_iptv()
        ui.notify("Connected to: " + provider_name, type="positive")
    else:
        raise Exception(f"Invalid username {username} and/or password")
except Exception as error:
    print("Error:", type(error).__name__, "–", error)
    print("Please, verify your credentials.")
    ui.notify("Please, verify your credentials.", type="warning")
    ui.notify("Error: " + type(error).__name__ + f" – {error}", type="negative")
