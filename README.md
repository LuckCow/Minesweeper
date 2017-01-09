<h1>Minesweeper</h1>
<p>This game of minesweeper is implemented in Python. It should work for multiple platforms. (I have only tried Windows and Linux so far)</p>
<h2>Dependencies</h2>
<ul>
<li>Python3.4 (any version of python 3 should work)</li>
<li>PyQt4 (PyQt5 should work aswell)</li>
</ul>
<h2>Note about functionality</h2>
<p>In order to maximize my highscores, I added a functionality called 'cording'. When you click on a number and there are a corresponding number of adjacent mines flagged, the game will automatically open all other unrevealed tiles. I have this activate immediately after opening a tile as well. This may be problematic if you have some spaces misflagged, but it really helps with speed if you get used to it.</p>
