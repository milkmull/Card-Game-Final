# Card-Game

## About the project

Table top card game with local wireless play.

### Built with
* [pygame](https://www.pygame.org)

## Getting started

### Prerequisites
* python3
* pygame
```python3 -m pip install -U pygame```
* Tkinter
```python3 -m pip install -U tk```
  on linux: ```sudo apt install python3-tk```
* cv2
```python3 -m pip install -U opencv-python```
* pyperclip
```python3 -m pip install -U pyperclip``` on linux you may need to also install `xclip` via `sudo apt install xclip`
* pyaudio
```python3 -m pip install -U pyaudio``` 
  on linux: ```sudo apt install python3-pyaudio```

### Disable Windows Defender to Allow Server to Run

windows defender > Manage Settings > Add or Remove Exclusions > Add Exclusion > File
Add the file Card Game file

### Installation
1. Clone the repo
``git clone https://github.com/milkmull/Card-Game-Final.git``
2. Install dependencies
3. Run main.py
`python3 main.py`
4. To start a single player game against computers click "single player" on the main menu
4. To start a local wireless game, click "host game" on the main menu
5. To join a local wireless game click "find game" on the main menu
