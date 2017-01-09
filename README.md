# Minesweeper

This game of minesweeper is implemented in Python. It should work for multiple platforms. 
(I have only tried Windows and Linux so far)

## Dependencies

* Python3
* PyQt5

## Installation

1. Install Python 3
```# apt-get install python3```
2. Install PyQt5 
```# apt-get install python3-pyqt5```
3. Download this repository
4. Run the ```minesweeper.py``` script

## Note about functionality

In order to maximize my highscores, I added a functionality called 'cording'. When you click on a number and there are a corresponding number of adjacent mines flagged, the game will automatically open all other unrevealed tiles. I have this activate immediately after opening a tile as well. This may be problematic if you have some spaces misflagged, but it really helps with speed if you get used to it.
