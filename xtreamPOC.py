"""
Script Name:    xtreamPOC.py
Description:    Proof of Concept of Xtream Codes Portal using PyXtream.
                It loads a simple page to search and play your content.
Author:         Mario Montoya <marioSGHT500@gmail.com>
Date:           2024-06-12

Version History:
- v0.1 (2024-06-12): It uses pyXtream, mpv and nicegui.

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
import random # Random cover images
import asyncio # Refresh ui
# TODO Remove duplicate streams, like movies.

# Specify the path to the mpv.exe file in Windows
mpv_path = 'C:\\path\\to\\mpv\\mpv.exe'

# Fill with your Xtream Provider credentials:
provider_name = 'YourProviderName'
username = 'user'
password = '1234'
provider_url = 'http://yourproviderurl.com:8080/'

def open_stream_url(url):
    # Specify the command-line arguments
    args = ['--slang=eng', '--alang=eng', '--fullscreen', url]
    # Run the mpv command
    if platform.system() == "Windows":
        subprocess.Popen([mpv_path] + args)
    elif platform.system() == "Darwin" or platform.system() == "Linux":  # macOS or Linux
        subprocess.Popen(['mpv'] + args)
    else:
        raise OSError("Unsupported operating system")    

def play_stream_id(stream_id, streams):
    played = False
    for stream in streams:
        if stream_id == stream.get('stream_id', 0) and not played:
            print(f"Playig {stream['name']}")
            ui.notify(f"Playig {stream['name']}")
            open_stream_url(stream['url'])
            played = True

def play_episode_id(episode_id, episodes):
    for episode_obj in episodes:
        if episode_obj.id == episode_id:
            print(f"Playing {episode_obj.title}")
            ui.notify(f"Playing {episode_obj.title}")
            open_stream_url(episode_obj.url)

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
        if stream['stream_type'] == 'series':
            series_id = stream['series_id']
            info_url = xt.get_series_info_URL_by_ID(series_id)
            # Add series_id without repetition
            if info_url not in info_urls:
                info_urls.append(info_url)
        else:
            print('')
            print(f"{stream['stream_type']} - {stream['stream_id']} - {stream['name']}", end="")
            add_card(stream['stream_type'], stream['stream_id'], stream['name'], stream['stream_icon'], streams=streams)
            ui.update() # Required in slower PCs.
            await asyncio.sleep(.25) # Required for ui self-refresh.
    print('')

    # Innitialize episodes. This is needed to play them later.
    episodes = []

    for info_url in info_urls:
        # Make the request to the URL
        response = requests.get(info_url)

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

Mario Montoya <marioSGHT500@gmail.com>""")

# Innitializes xt and connects to your IPTV provider
xt = XTream(provider_name, username, password, provider_url)
if xt.auth_data != {}:
    xt.load_iptv()
else:
    print("Could not connect")
    exit()

# Creates a wide search row
with ui.row().style('width: 100%;') as search_row:
    search_input = ui.input("Enter name to search:", placeholder="For Example: Juego de Tronos").style('width: 78%;')
    ui.button('Search', on_click=lambda: asyncio.create_task(ui_search_stream())).style('width: 20%;')
# And two result rows
channel_row = ui.row()
serie_row = ui.row()

ui.run()
