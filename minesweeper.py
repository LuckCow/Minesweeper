
from PyQt4 import Qt

import sys, random
from PyQt4 import Qt


class mainWindow(Qt.QMainWindow):
    """
    Main window contains an Board and toolbar options
    """
    def __init__(self):
        super(mainWindow, self).__init__()
        self.b = boardWidget()
        self.initUI()
        

        self.setCentralWidget(self.b)
        self.resize(self.b.size())
        
    def initUI(self):
        exitAction = Qt.QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(Qt.qApp.quit)

        #TODO: add tooltip for this
        restart = Qt.QAction(Qt.QIcon('bin/restart.png'), 'New Game', self)
        restart.setShortcut('Ctrl+N')
        restart.triggered.connect(self.b.resetGame)#TODO: make reset game function
                                
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(restart)
                          
        self.setWindowTitle('PyneSweeper')
        self.show()

        
#TODO: Add timer!!
#TODO: add mine counter
class boardWidget(Qt.QWidget):
    """
    Stores minesweeper board (mines and numbers)
    Stores current cover
    Display methods as QtWidget
    """

    
    def __init__(self):
        super(boardWidget, self).__init__()
        self.mines = 99
        self.w = int(30)
        self.h = int(16)
        self.pad = 5
        self.resize((self.w + 1)*30 + 10, (self.h + 1)*30 + 10)
        self.setSquareSize()
        row = ['0' for i in range(self.w)]
        self.board = [row.copy() for i in range(self.h)]
        
        row = [1 for i in range(self.w)]
        self.cover = [row.copy() for i in range(self.h)]

        row = [False for i in range(self.w)]
        self.flags = [row.copy() for i in range(self.h)] 
        self.loadImages()
        self.gameState = 0

    def loadImages(self):
        path = 'bin/'
        self.tileImg = Qt.QImage()
        self.tileImg.load(path+'tile.png', 'PNG')
        self.emptyTileImg = Qt.QImage()
        self.emptyTileImg.load(path+'emptyTile.png', 'PNG')
        self.flagImg = Qt.QImage()
        self.flagImg.load(path+'flag.png', 'PNG')
        self.wrongFlagImg = Qt.QImage()
        self.wrongFlagImg.load(path+'wrongFlag.png', 'PNG')
        self.mineImg = Qt.QImage()
        self.mineImg.load(path+'mine.png', 'PNG')
        self.explodedMineImg = Qt.QImage()
        self.explodedMineImg.load(path+'explodedMine.png', 'PNG')
        self.numberImages = [Qt.QImage() for i in range(0,8)]
        for i in range(0,8):
            self.numberImages[i].load(path + str(i+1) + '.png', 'PNG')

    def mouseReleaseEvent(self, e):
        #print('Mouse Pressed:','Button:',e.button(),'x',e.x(),'y',e.y())
        row = (e.y() - self.pad) // self.sq
        col = (e.x() - self.pad) // self.sq
        if self.gameState == 0:
            self.gameState = 1
            if e.button() == 1:
                if row in range(0, self.h) and col in range(0, self.w):
                    self.generateBoard(row, col)
                    self.tryTile(row,col)
        elif self.gameState == 1:
            if e.button() == 1: #left click
                self.tryTile(row, col)
            elif e.button() == 2: #right click
                self.flagTile(row, col)

    def tryTile(self, row, col):
        if self.flags[row][col]:
            return #do not do anything if flag is clicked
        if self.board[row][col] != 'M':
            self.cover[row][col] = 0
            if self.board[row][col] == '0':
                self.openAdjacentTiles(row, col)
        else: #Lose game
            self.gameState = 2
            self.explodedRow = row
            self.explodedCol = col
        self.checkWin() #might want to move?
        self.update()
        
    def flagTile(self, row, col):
        if self.cover[row][col] == 1:
            self.flags[row][col] = not self.flags[row][col]
            self.update()

    #TODO: rewrite this function iteratively due to inefficient nature of python recursion(and low depth)
    #Also, perhaps check for win iteratively aswell
    def openAdjacentTiles(self, row, col):
        #i, row
        #j, col
        for i in range(row-1, row+2, 1): #row
            for j in range(col-1, col+2, 1): #col
                if i >= 0 and j >=0 and i < self.h and j < self.w:
                    if self.cover[i][j] == 0:
                        pass
                    else:
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

    def checkWin(self):
        if sum(map(sum, self.cover)) == (self.mines):
            self.win()
            
    def win(self):
        print('GG-!!-You-Win-!!-GG')
        pass
        #TODO: save time
        #TODO: show highscores
        #TODO: ask for replay
        
    def paintEvent(self, e):
        qp = Qt.QPainter()
        qp.begin(self)
        self.drawBoard(qp)
        qp.end()

    def drawBoard(self, qp):
      
        qp.setPen(Qt.QPen(Qt.Qt.black, Qt.Qt.SolidLine))
        s = self.sq
        p = self.pad
        self.setSquareSize()
        qp.setFont(Qt.QFont('Times', self.sq // 2))
        
        row = ['0' for i in range(self.w)]
        rectangles = [row.copy() for i in range(self.h)]
        #Squares
        for i in range(0, self.w):
            for j in range(0,self.h):
                rectangles[j][i] = Qt.QRect(p+(i*s), p+(j*s), s, s)

        # Draw rectangles and text inside each rectangle
        for i in range(0,self.h):
            #qp.drawRects(rectangles[i])
            for j in range(0, self.w):
                
                #qp.drawText(rectangles[i][j],5,self.board[i][j])
                if self.cover[i][j]:
                    qp.drawImage(rectangles[i][j],self.tileImg)
                    if self.flags[i][j]:
                        qp.drawImage(rectangles[i][j],self.flagImg)
                else:
                    qp.drawImage(rectangles[i][j], self.emptyTileImg)
                    qp.drawImage(rectangles[i][j], self.numberImages[int(self.board[i][j]) - 1])

        if self.gameState == 2:
            for i in range(0,self.h):
                for j in range(0, self.w):
                    if self.board[i][j] == 'M' and not self.flags[i][j]:
                        qp.drawImage(rectangles[i][j], self.mineImg)
                    if self.flags[i][j] and self.board[i][j] != 'M':
                        qp.drawImage(rectangles[i][j], self.wrongFlagImg)
            qp.drawImage(rectangles[self.explodedRow][self.explodedCol], self.explodedMineImg)
                        
    def setSquareSize(self):
        sqW = (self.size().width()-10) // self.w
        sqH = (self.size().height()-10) // self.h
        self.sq = min([sqW, sqH])

    def generateBoard(self, row, col):
        self.placeMines(row, col)
        self.calculateNumbers()

    def placeMines(self, row, col):
        minesPlaced = 0
        while (minesPlaced < 99):
            x = random.randrange(self.w)
            y = random.randrange(self.h)
            #print(x,y)
            if self.board[y][x] == '0' and not (y in [row-1, row, row+1] and x in [col-1, col, col+1]):
                self.board[y][x] = 'M'
                minesPlaced = minesPlaced + 1
                #print(minesPlaced)
        
    def calculateNumbers(self):
        for i in range(0, self.h):
            for j in range(0, self.w):#self.board[i]:
                if self.board[i][j] != 'M':
                    self.board[i][j] = str(self.getAdjacentMines(j,i))

    def getAdjacentMines(self, x, y):
        numMines = 0
        for j in range(y-1, y+2, 1):
            for i in range(x-1, x+2, 1):
                if i >= 0 and j >=0 and j < self.h and i < self.w:
                    if self.board[j][i] == 'M':
                        numMines += 1
        return numMines
            
        
def main():
    app = Qt.QApplication(sys.argv)
    
    w = mainWindow()
    print(w.b.board)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()