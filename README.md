# xtreamPOC - A proof of concept of Xtream Portal Codes
Proof of Concept of Xtream Portal Codes using pyxtream, mpv and nicegui.

# Why I creared this script
I needed an IPTV player that can run on linux in an old PC.
By old I mean an HP 1000 with an Intel core i3 CPU and 4 GB of memory.
I run Linux Mint on that computer which is plugged to my TV via HDMI.
I tried to play my IPTV content with Hypnotix, which is pre-installed.
But Hypnotix crashed 90% of the times with my IPTV provider.

Then I tried the IPTV Smarters Web Player: http://webtv.iptvsmarters.com . The issues with Smarters Web were:
* Unable to select a different language audio track.
* Some movies show error "Flowplayer cannot play this content".
* Live channels with too many glitches in my slow PC.

# Transition
Then I tried soperlomo's pyxtream and I tried the:

* Functional Test <code>functional_test.py</code>

The user iterface didn't play any content and when searching for
series in the functional test with my IPTV provider makes the
script to crash.

# Solution
This script connects to my IPTV provider using soperlomo's pyxtream.
Then I search for content, including series, and then I de-serialize the
response from my IPTV provider which is in JSON format. I use some of the objects from soperlomo's pyxtream.
Nevertheless, most of the series information was only available in that JSON format. Thus, I needed to use that raw JSON info, de-serialize it to be able to access the series, the seasons and the episodes. 

# How you can use it
You can use this script if you have an IPTV provider which supports Xtream Codes. If your IPTV provider only supports m3u lists then this script won't work for you.

Check the steps in the <code>tutorial</code> folder. You will see where you have to fill your IPTV provider name and your credentials.

# What you will need
You need to install mpv to be able to play your content.
You will also need to install the python libraries required for this script.

The mpv is a media player which runs nice on an old computer like my HP 1000.
The python libraries are the ones required by pyxtream and some additional ones for my script.

# mpv
You can get mpv from it's home page: https://mpv.io/

For linux distros like Debian, Ubuntu or Mint you can simply say:

<code>
sudo apt install mpv
</code>

For Windows, you can use the binaries available from mpv's home page.

# python libraries
Although I tried to capture all the libraries required by my python script while I was deploying it in my old HP 1000, it's not warantied I captured them all.
The python libraries I know you will need are listed here as pip install commands:

<code>
pip install pyxtream
pip install pyxtream[REST_API]
pip install jsonschema
pip install nicegui
</code>

