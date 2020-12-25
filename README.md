## What I need to run it?
- Python3 with a few libraries (requirements.txt).
- The Chrome driver for selenium (every Chrome version has its own version of driver). 

[Download Driver](https://sites.google.com/a/chromium.org/chromedriver/downloads)


## How to run it?
Inside the Bot folder:
```bash
python3 main.py
```



## How it works?

### Culture
It only works with Admin. 
### Buldings
In the file settings.json there is a list where we can specify the priority of every building.
The bot select which building upgrade based in that list.
### Farm
- Captain Activated: The bot use the captain village view.
- No Admin: The bot goes through every city and loot the villages one by one.
### Academy
In the file settings.json there is a list where we can specify which items we want the bot do a research for in the academy.