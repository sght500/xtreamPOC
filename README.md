# xtreamPOC - A proof of concept of Xtream Portal Codes
Proof of Concept of Xtream Portal Codes using pyxtream, mpv and nicegui.

# Why I creared this script
I needed an IPTV player that can run on Linux on an old PC. By old, I mean an HP 1000 with an Intel Core i3 CPU and 4 GB of memory. I run Linux Mint on that computer, which is plugged into my TV via HDMI. I tried to play my IPTV content with Hypnotix, which is pre-installed, but Hypnotix crashed 90% of the time with my IPTV provider.

Then I tried the IPTV Smarters Web Player: http://webtv.iptvsmarters.com. The issues with Smarters Web were:

* Unable to select a different language audio track.
* Some movies show the error "Flowplayer cannot play this content."
* Live channels had too many glitches on my slow PC.

# Transition
Then I tried soperlomo's pyxtream and the Functional Test (<code>functional_test.py</code>). The user interface didn't play any content, and searching for series in the functional test with my IPTV provider caused the script to crash.

# Solution
This script connects to my IPTV provider using soperlomo's pyxtream. I search for content, including series, and then deserialize the response from my IPTV provider, which is in JSON format. I use some of the objects from soperlomo's pyxtream. However, most of the series information was only available in that JSON format. Thus, I needed to use that raw JSON info and deserialize it to access the series, seasons, and episodes.

# How you can use it
You can use this script if you have an IPTV provider that supports Xtream Codes. If your IPTV provider only supports m3u lists, then this script won't work for you.

Check the steps in the <code>tutorial</code> folder. You will see where you have to fill in your IPTV provider name and your credentials.

# What you will need
You need to install mpv to be able to play your content. You will also need to install the Python libraries required for this script.

mpv is a media player that runs nicely on an old computer like my HP 1000. The Python libraries are the ones required by pyxtream and some additional ones for my script.

# mpv
You can get mpv from its homepage: https://mpv.io/

For Linux distros like Debian, Ubuntu, or Mint, you can simply run:

<code>sudo apt install mpv</code>

For Windows, you can use the binaries available from mpv's home page.

# python libraries
Although I tried to capture all the libraries required by my Python script while I was deploying it on my old HP 1000, it's not guaranteed I captured them all. The Python libraries I know you will need are listed here as pip install commands:

<code>pip install pyxtream
pip install pyxtream[REST_API]
pip install jsonschema
pip install nicegui</code>

