# SINoALICE-Simplified-API

A simplified set of Python classes and functions for interacting with the SINoALICE web API.

For those who are unaware, SINoALICE is a mobile game. A very niche game with a... dminishing player population. Well, you're probably not here to read about this, so we'll leave it at that.

This repository contains a set of classes which are used to interact the the SINoALICE web API, but is really just code which uses POSTs request to the server. You can already do this with existing repositories on github, but I figured it'd be nice to simplify their usage a bit, which is exactly what this is: A simplified version. Maybe save some time if someone ever decides to come along and do the same thing.

## Prerequisites

There are a few prerequisites that need to be met before using these functions.

- An existing account in SINoALICE
- Reverse engineered values for the following:
  - AES key
  - UID
  - UUID
  - XUID
  - Private RSA key

## Reverse Engineering

I figured I should probably make a small section for this at least if I'm making an API that heavily depends on values retrieved from reverse engineering the app.

The main tools you'll need:
- Frida
- Ghidra or IDA
- Other general android RE tools like apktool, etc.

Android app reverse engineering guides shouldn't be particularly hard to find or follow, so I'll omit that here. I'll just list some specific notes to be aware of below:

## Other Info

SINoALICE is a IL2CPP app. Keep that in mind when reverse engineering.
You'll likely need a rooted android device to use Frida to hook into function calls
Modifying the apk and injecting frida-gadget will not work from my own experience
Using frida's command line arg realm=emulated will not work either
For more information, refer to the linked repositories in the credits section of the README. Specifically the discussions in the closed issues, and their README files
Again, this is all based on my own experiences as a first timer trying to reverse engineer an android app. In fact, calling this "reverse engineering" feels too grand for something like this. There are probably better ways to do this than what I've done here, but hey, if it works, it works.

## Usage

- Using the example.env file as reference, create a .env file containing the values reverse engineered above.
- Note: This will cause the account associated with the UID to be used in the API requests. It is suggested to use a "dummy" account.
- Install the required modules lsited in the requirements.txt file
- Import and use the API classes

## Examples

TBC

## Credits

Credit goes to [see-aestas](https://github.com/see-aestas/SINoALICE-API) and [Egoistically](https://github.com/Egoistically/SINoALICE) for laying the foundations and groundwork that made this possible, specifically the BaseAPI.py file, which is just modified from their work.

## Other Comments

For anyone familiar with the SINoALICE, you may know about sites such as deachsword and the no longer unavailable kurelog, which were able to access SINoALICE GC data, as well as a significant amount of other player data. Having used these sites myself, I can confidantly say that my work here is nothing new. There are many who have been down this path before and have a far greater understanding of SINoALICe's API and structure, so I consider this a personal project to see whether I am able to follow in their footsteps.

And well, I was also interested in how it all worked anyway, so I figured I'd try at least.
