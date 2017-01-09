#!/usr/bin/python3
"""
MineSweeper
Author: Nick Collins
Date: 4/1/2016

Rules
99 Mines are randomly placed, numbers are generated, which indicate the number of adacent mines
The game is won when all of the numbers are revealed
The game is lost when the player clicks on a mine

Features:
GUI
Full minesweeper functionality including cording
Highscores

Display:
Board
Time
Mine flag count

TODO:
Possibly look into 'evil' minesweeper, which dynamically creates board,
causing a loss for player whenever possible (would probably be impossible to win with current board size)
Implement changing board size and mine number
Implement logic board solving verification option
Implement nice minesweeper, which dynamically creates board allowing for mistakes
Impliment a review/analyze functality that tracks mouse movement and records areas that cause trouble for practice later

Known Bugs:
None

"""
from PyQt5 import Qt
import sys, random, time, json, datetime, os


class mainWindow(Qt.QMainWindow):
    """
    Main window contains an Board and toolbar options
    """
    def __init__(self):
        super(mainWindow, self).__init__()
        self.tmr = timer()
        self.mc = mineCounter('0')

        self.b = boardWidget(self.tmr, self.mc)
        self.initUI()
        
        
    def initUI(self):
        exitAction = Qt.QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(Qt.qApp.quit)

        #Restart icon and function
        ri = Qt.QPixmap()
        ri.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'restart.png'), 'PNG')
        restart = Qt.QAction(Qt.QIcon(ri), 'New Game', self)
        restart.setShortcut('Ctrl+N')
        restart.triggered.connect(self.b.resetGame)

        #Grid layout
        self.gridContainer = Qt.QWidget()
        self.grid = Qt.QGridLayout()
        self.grid.addWidget(self.tmr , 0,0)
        self.grid.addWidget(self.mc, 0, 1)
        self.grid.addWidget(self.b, 1, 0, 20, 2)
        self.gridContainer.setLayout(self.grid)
        #self.grid.setRowMinimumHeight(1, 400)
        #self.grid.setColumnMinimumWidth(0, self.size().width())
        self.setCentralWidget(self.gridContainer)
        
        self.toolbar = self.addToolBar('Tooooooooools')
        self.toolbar.addAction(restart)
        #self.toolbar.addAction(exitAction)
        
        self.resize(self.b.w * 50, self.b.h * 50 + 200)
        self.setWindowTitle('Python Minesweeper')
        self.show()

class mineCounter(Qt.QWidget):
    """
    Qt widget that counts and displays the number of mines flagged
    """
    def __init__(self, numMines):
        super(mineCounter, self).__init__()
        self.mines = 0
        self.text = 'Mines: ' + str(self.mines) + '/99'
        self.initUI()

    def initUI(self):
        pass

    def addMine(self):
        self.mines += 1
        self.text = 'Mines: ' + str(self.mines) + '/99'
        self.update()

    def subMine(self):
        self.mines -= 1
        self.text = 'Mines: ' + str(self.mines) + '/99'
        self.update()

    def resetMines(self):
        self.mines = 0
        self.text = 'Mines: 0/99'
        self.update()
    
    def paintEvent(self, event):
        qp = Qt.QPainter()
        qp.begin(self)
        qp.fillRect(event.rect(), Qt.QColor(255,255,255))
        self.drawText(qp, event)
        qp.end()
        
    def drawText(self, qp, event):
        qp.setPen(Qt.QColor(0,0,0))
        qp.setFont(Qt.QFont('Decorative', 14))
        qp.drawText(event.rect(), Qt.Qt.AlignCenter, self.text) 
        
class timer(Qt.QWidget):
    """
    Qt widget that times the game and displays the time
    """
    def __init__(self):
        super(timer, self).__init__()

        self.initUI()

    def initUI(self):
        self.timeStr = 'Time: '
        self.seconds = 0
        self.timer = Qt.QBasicTimer()
        self.text = self.timeStr + '...'

    def startTimer(self):
        self.timer.start(1000, self) #QObj accepts timer events

    def endTimer(self):
        self.timer.stop()

    def resetTimer(self):
        self.timer.stop()
        self.seconds = 0
        self.text = self.timeStr + '...'
        self.update()
        
    def timerEvent(self, e):
        self.seconds += 1
        self.text = self.timeStr + str(self.seconds)#[:-2] + ':' + str(self.seconds)[-2:]
        self.update()
        
    def paintEvent(self, event):
        qp = Qt.QPainter()
        qp.begin(self)
        qp.fillRect(event.rect(), Qt.QColor('White'))
        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(Qt.QColor('Black'))
        qp.setFont(Qt.QFont('Decorative', 14))
        qp.drawText(event.rect(), Qt.Qt.AlignCenter, self.text) 

        
class boardWidget(Qt.QWidget):
    """
    Minesweeper board logic and display
    """

    def __init__(self, guiTimer, guiMineCounter):
        """
        Initialzes variables:
        self.board[][] - stores mines and numbers as chars
        self.cover[][] - stores whether tile is covered or uncovered as 1(covered) or 0(uncovered)
        self.flags[][] - stores whether a tile is flaged (true or false)
        mines - number of mines
        w - width of grid
        h - height of grid
        gameState - indicates whether game is unstarted(0), in progress(1), lost(2) or won(3)
        """
        super(boardWidget, self).__init__()
        self.mines = 99
        self.w = int(30)
        self.h = int(16)
        self.defaultSqSize = 50
        self.resize((self.w)*self.defaultSqSize + 10, (self.h + 1)*self.defaultSqSize)
        self.setSquareSize()
        row = ['0' for i in range(self.w)]
        self.board = [row.copy() for i in range(self.h)]
        
        row = [1 for i in range(self.w)]
        self.cover = [row.copy() for i in range(self.h)]

        row = [False for i in range(self.w)]
        self.flags = [row.copy() for i in range(self.h)]
        self.flaggedMines = 0

        self.rPressed = False
        self.lPressed = False

        self.grid = [row.copy() for i in range(self.h)]
        #Grid of QSquares (sized according to current window size
        s = self.sq
        for i in range(0, self.w):
            for j in range(0,self.h):
                self.grid[j][i] = Qt.QRect((i*s), (j*s), s, s)
        
        self.loadImages()
        self.gameState = 0

        self.addGUImc = Qt.QAction(self)
        self.addGUImc.triggered.connect(guiMineCounter.addMine)
        self.subGUImc = Qt.QAction(self)
        self.subGUImc.triggered.connect(guiMineCounter.subMine)
        self.resetGUImc = Qt.QAction(self)
        self.resetGUImc.triggered.connect(guiMineCounter.resetMines)
        self.startGUItimer = Qt.QAction(self)
        self.startGUItimer.triggered.connect(guiTimer.startTimer)
        self.endGUItimer = Qt.QAction(self)
        self.endGUItimer.triggered.connect(guiTimer.endTimer)
        self.resetGUItimer = Qt.QAction(self)
        self.resetGUItimer.triggered.connect(guiTimer.resetTimer)

    def loadImages(self):
        '''
        Loads up picture files, which are stored in the 'data/' directory
        '''
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', '{}')
        self.tileImg = Qt.QImage()
        self.tileImg.load(path.format('tile.png'), 'PNG')
        self.emptyTileImg = Qt.QImage()
        self.emptyTileImg.load(path.format('emptyTile.png'), 'PNG')
        self.flagImg = Qt.QImage()
        self.flagImg.load(path.format('flag.png'), 'PNG')
        self.wrongFlagImg = Qt.QImage()
        self.wrongFlagImg.load(path.format('wrongFlag.png'), 'PNG')
        self.mineImg = Qt.QImage()
        self.mineImg.load(path.format('mine.png'), 'PNG')
        self.explodedMineImg = Qt.QImage()
        self.explodedMineImg.load(path.format('explodedMine.png'), 'PNG')
        self.numberImages = [Qt.QImage() for i in range(0,8)]
        for i in range(0,8):
            self.numberImages[i].load(path.format(str(i+1) + '.png'), 'PNG')

    def mousePressEvent(self, e):
        row = (e.y()) // self.sq
        col = (e.x()) // self.sq
        if self.gameState == 1:
            if e.button() == 2: #right click
                self.flagTile(row, col)
            
    def mouseReleaseEvent(self, e):
        row = (e.y()) // self.sq
        col = (e.x()) // self.sq
        if self.gameState == 0:
            if e.button() == 1:
                if row in range(0, self.h) and col in range(0, self.w):
                    self.startGame(row, col)
        elif self.gameState == 1:
            if e.button() == 1 and row < self.h and col < self.w:
                #left click -> open tiles directly and then coord
                self.openTile(row, col)
                self.cordTile(row, col) 
                self.checkWin()
                self.update()

    def startGame(self, row, col):
        self.gameState = 1
        self.generateBoard(row, col)
        self.openTile(row,col)
        self.t0 = time.time()
        self.startGUItimer.activate(Qt.QAction.Trigger)
        self.update()

    def cordTile(self, row, col):
        if self.cover[row][col]:
            return
        if self.getAdjacentFlags(row, col) == int(self.board[row][col]):
            for i in range(row - 1, row + 2):
                for j in range(col - 1, col + 2):
                    if i >= 0 and j >= 0 and i < self.h and j < self.w:
                        self.openTile(i, j)
                

    def openTile(self, row, col):
        if self.flags[row][col] or not self.cover[row][col]:
            return #do not do anything if flag is clicked
        if self.board[row][col] != 'M':
            self.cover[row][col] = 0
            if self.board[row][col] == '0':
                self.openAdjacentTiles(row, col)
        else: #Lose game
            self.gameState = 2
            self.explodedRow = row
            self.explodedCol = col
            self.endGUItimer.activate(Qt.QAction.Trigger)

        
    def flagTile(self, row, col):
        if self.cover[row][col] == 1:
            if self.flags[row][col]:
                self.flags[row][col] = False
                self.flaggedMines -= 1
                self.subGUImc.activate(Qt.QAction.Trigger)
            else:
                self.flags[row][col] = True
                self.flaggedMines += 1
                self.addGUImc.activate(Qt.QAction.Trigger)
            self.update()
            
    def openAdjacentTiles(self, row, col):
        #i, row
        #j, col
        for i in range(row-1, row+2, 1): #row
            for j in range(col-1, col+2, 1): #col
                if i >= 0 and j >=0 and i < self.h and j < self.w:
                    if self.cover[i][j] == 0:
                        pass
                    else:
                        if self.flags[i][j]:
                            self.flagTile(i,j)
                            
                        self.cover[i][j] = 0
                        
                        if self.board[i][j] == '0':
                            self.openAdjacentTiles(i, j)
                

    def resetGame(self):
        row = ['0' for i in range(self.w)]
        self.board = [row.copy() for i in range(self.h)]
        row = [1 for i in range(self.w)]
        self.cover = [row.copy() for i in range(self.h)]
        row = [False for i in range(self.w)]
        self.flags = [row.copy() for i in range(self.h)] 
        self.gameState = 0
        self.update()
        self.resetGUItimer.activate(Qt.QAction.Trigger)
        self.resetGUImc.activate(Qt.QAction.Trigger)

    def checkWin(self):
        #if covered tiles equals mines, board is solved
        if sum(map(sum, self.cover)) == (self.mines):
            self.win()
            
    def win(self):
        self.gameState = 3
        self.totalTime = time.time() - self.t0
        self.endGUItimer.activate(Qt.QAction.Trigger)
        self.update()
        self.updateHighscores()


    def updateHighscores(self):
        time = round(self.totalTime, 2)
        displayString = 'Your time was: ' + str(time)
        
        try:
            with open('highscores.json', 'r') as score_file:
                scores = json.load(score_file)
        except FileNotFoundError:
            scores = {'highscores':[]}

        newEntry = {"date":str(datetime.date.today()), "score":time}
        for i, entry in enumerate(scores['highscores']):
            if time < entry['score']:
                scores['highscores'].insert(i, newEntry)
                if len(scores['highscores']) > 5:
                    scores['highscores'].pop()
                displayString += '\nNew Highscore! Wewt!'
                break
        else:
            if len(scores['highscores']) < 5:
                scores['highscores'].append(newEntry)
                displayString += '\nNew Highscore! Wewt!'

        with open('highscores.json', 'w') as score_file:
            score_file.write(json.dumps(scores))
        
        displayString += '\n\nHighscores:\n'
        for i, sc in enumerate(scores['highscores']):
            displayString += '{}. {} ({})\n'.format(i+1, sc["score"], sc["date"])
            
        wnBox = Qt.QMessageBox(Qt.QMessageBox.NoIcon, 'You Win!', displayString, Qt.QMessageBox.Ok)
        wnBox.exec_()
        
    def paintEvent(self, e):
        qp = Qt.QPainter()
        qp.begin(self)
        self.drawBoard(qp)
        qp.end()

    def drawBoard(self, qp):
        s = self.sq
        # Draw Appropriate image in each grid square
        for i in range(0,self.h):
            for j in range(0, self.w):
                #Draw cover tile and flags if covered
                if self.cover[i][j]:
                    qp.drawImage(self.grid[i][j], self.tileImg)
                    if self.flags[i][j]:
                        qp.drawImage(self.grid[i][j], self.flagImg)
                #Draw emptyTile and number
                else:
                    qp.drawImage(self.grid[i][j], self.emptyTileImg)
                    if self.board[i][j] != '0':
                        qp.drawImage(self.grid[i][j], self.numberImages[int(self.board[i][j]) - 1])
                        
        #Show mine positions at loss
        if self.gameState == 2:
            for i in range(0,self.h):
                for j in range(0, self.w):
                    if self.board[i][j] == 'M' and not self.flags[i][j]:

                        qp.drawImage(self.grid[i][j], self.mineImg)
                    if self.flags[i][j] and self.board[i][j] != 'M':
                        qp.drawImage(self.grid[i][j], self.wrongFlagImg)
            qp.drawImage(self.grid[self.explodedRow][self.explodedCol], self.explodedMineImg)

    def resizeEvent(self, e):
        self.setSquareSize()
        s= self.sq
        #resize grid
        for i in range(0, self.w):
            for j in range(0,self.h):
                self.grid[j][i].setRect((i*s), (j*s), s, s)
            
    def setSquareSize(self):
        #Set square size according to window size
        sqW = (self.size().width()-10) // self.w
        sqH = (self.size().height()-10) // self.h
        self.sq = min([sqW, sqH])

    def generateBoard(self, row, col):
        self.placeMines(row, col)
        self.calculateNumbers()

    def placeMines(self, row, col):
        #Randomly place mines on board
        minesPlaced = 0
        while (minesPlaced < self.mines):
            x = random.randrange(self.w)
            y = random.randrange(self.h)
            if self.board[y][x] == '0' and not (y in [row-1, row, row+1] and x in [col-1, col, col+1]):
                self.board[y][x] = 'M'
                minesPlaced = minesPlaced + 1
        
    def calculateNumbers(self):
        for i in range(0, self.h):
            for j in range(0, self.w):
                if self.board[i][j] != 'M':
                    self.board[i][j] = str(self.getAdjacentMines(j,i))

    def getAdjacentMines(self, x, y):
        numMines = 0
        for j in range(y-1, y+2, 1):
            for i in range(x-1, x+2, 1):
                if i >= 0 and j >= 0 and j < self.h and i < self.w:
                    if self.board[j][i] == 'M':
                        numMines += 1
        return numMines

    def getAdjacentFlags(self, row, col):
        numFlags = 0
        for i in range(row - 1, row + 2):
            for j in range(col - 1, col + 2):
                if i >= 0 and j >= 0 and i < self.h and j < self.w:
                    if self.flags[i][j]:
                        numFlags += 1
        return numFlags
            
        
def main():
    app = Qt.QApplication(sys.argv)
    w = mainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
