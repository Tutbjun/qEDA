"""temp dev file. to be integrated..."""

from copy import copy
import wx
from wx.lib.agw.floatspin import FloatSpin
import numpy as np
from numpy import arange, sin, pi
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
from scipy import signal
from numba import jit

#TODO: make UI updates according to sketch
#TODO: make mouseover plot disapear when mouse is out of plot
#TODO: figure out why gaussian changes plot in the fringes where it shouldn't

@jit
def _numbaMouseOverCalc(mx : float, my : float, pointSpacing : float, mouseAreaWidth : float, bt : np.array, bs : np.array, gaussianCurve : np.array):
    mouseStartVal = float(mx) - float(mouseAreaWidth)
    mouseEndVal = float(mx+mouseAreaWidth)
    mouseStartIndex = int(mouseStartVal/pointSpacing)
    mouseEndIndex = int(mouseEndVal/pointSpacing)
    if mouseStartIndex < 0:
        mouseStartIndex = 0
    if mouseEndIndex >= len(bt):
        mouseEndIndex = len(bt)-1
    if mouseStartIndex != mouseEndIndex and mouseEndIndex > mouseStartIndex:
        #plot gaussian curve across mt:
        gaussian = gaussianCurve
        if mouseStartIndex <= 0:
            gaussian = gaussian[len(gaussian)-(mouseEndIndex-mouseStartIndex):]
        elif mouseEndIndex >= len(bt)-1:
            gaussian = gaussian[:(mouseEndIndex-mouseStartIndex)]
        mt = bt[mouseStartIndex:mouseEndIndex]
        #self.mt -= self.mouseAreaWidth
        ms = gaussian*my
        invGaussian = -gaussian+1
        ms += bs[mouseStartIndex:mouseEndIndex]*invGaussian
        return mt, ms, mouseStartIndex, mouseEndIndex
    else:
        return np.empty(0),np.empty(0), mouseStartIndex, mouseEndIndex

@jit
def _numbaBitScaling(array : np.array, bits : int, signed : bool, maxVal : float):
        array /= maxVal
        #rs should be rounded to bits
        scalar = 2**(bits-1)
        if signed:
            scalar /= 2
        array *= scalar
        array += 0.5
        for i in range(len(array)):
            array[i] = int(array[i])
        if not signed:
            array = np.clip(array, 0, None)
        array /= scalar
        array = np.clip(array, -1, 1)
        array *= maxVal
        return array

@jit
def _numbaSuperellipseCurve(xs : np.array, n : float):
    def f(x,n):
        return (1 - x**n)**(1/n)
    ret = np.zeros(len(xs),dtype=np.float64)
    for i in range(len(xs)):
        ret[i] = f(xs[i],n)
    return ret

@jit
def numbaP2PRise(point1 : np.array, point2 : np.array, dataPoints : int, amount : int = 1):
    #use superellipse formula to make an amount of rise/fall graphs
    ns = np.linspace(float(np.log10(0.25)),float(np.log10(10)),amount)
    ns = np.power(10,ns)
    X = np.linspace(0,1,dataPoints)
    ys = np.zeros((amount,dataPoints),dtype=np.float64)
    for i in range(len(ns)):
        ys[i] = _numbaSuperellipseCurve(X,ns[i])
    X *= (point2[0]-point1[0])
    X += point1[0]
    ys *= np.sign(point1[1]-point2[1])
    ys *= abs(point2[1]-point1[1])
    ys += point2[1]
    xs = np.zeros(ys.shape,dtype=np.float64)
    for i in range(len(xs)):
        xs[i] = X
    return xs.flatten(),ys.flatten()

class plotPanel(wx.Panel):
    pointSpacing = 0.001
    mouseAreaWidth = 0.2
    gaussianCurve = np.array(signal.gaussian(2*mouseAreaWidth/pointSpacing,std=1/mouseAreaWidth*10))

    def __init__(self, *args, **kw):
        super(plotPanel, self).__init__(*args, **kw)
        self._genPlot()
        self._genSettings()
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.sizer.Add(self.settingsSizer, 0, wx.CENTER)
        self.SetSizer(self.sizer)
        self.Fit()
        self.mouseXY = np.array((0,0),dtype=np.float64)
        self._calcInitalPlot()
        self._applyPlotSettings()
    
    def _genPlot(self):
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        #self.curser = Cursor(self.axes, useblit=True, color='red', linewidth=1)
        self.canvas.mpl_connect('motion_notify_event', self.OnMousePlotMove)
        self.canvas.mpl_connect('button_press_event', self.OnMousePlotPress)

    def _genSettings(self):
        self.settingsSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.settings = {"bits":1,"signed":False,"riseTime":0.05,"maxVal":3.3}

        bitChoser = wx.BoxSizer(wx.VERTICAL)
        bitChoser.Add(wx.StaticText(self, label="bits:"), 0, wx.EXPAND, 10)
        bitChoserField = wx.SpinCtrl(self, value=str(self.settings["bits"]), min=1, max=32)
        bitChoser.Add(bitChoserField, 0, wx.Left, 10)
        bitChoserField.Bind(wx.EVT_TEXT, self.OnBitChange)

        signChooser = wx.CheckBox(self, label='Signed')
        signChooser.Bind(wx.EVT_CHECKBOX, self.OnSignChange)

        RSChoser = wx.BoxSizer(wx.VERTICAL)
        RSChoser.Add(wx.StaticText(self, label="R/S time:"), 0, wx.EXPAND, 10)
        RSChoserField = FloatSpin(self, value=str(self.settings["riseTime"]), min_val=0.0, max_val=1, increment=0.001, digits=3)
        RSChoser.Add(RSChoserField, 0, wx.EXPAND, 10)
        RSChoserField.Bind(wx.EVT_TEXT, self.OnRSChange)

        
        self.settingsSizer.AddMany([
            (bitChoser, 0, wx.Top),
            (RSChoser, 0, wx.EXPAND),
            (wx.StaticText(self, label="max V/I"), 0, wx.EXPAND),
            (signChooser, 0, wx.Top),
            (wx.StaticText(self, label="variance"), 0, wx.EXPAND),
            (wx.StaticText(self, label="V/I"), 0, wx.EXPAND),
        ])

    def OnBitChange(self,event):
        self.settings["bits"] = event.GetInt()
        self.Update()

    def OnSignChange(self,event):
        self.settings["signed"] = event.IsChecked()
        self.Update()

    def OnRSChange(self,event):
        var = event.GetString()
        self.settings["riseTime"] = float(var)
        self.Update()

    def OnMousePlotMove(self,event):
        x,y = event.xdata,event.ydata
        if x is None or y is None:
            return None
        else:
            self.mouseXY = np.array((x,y),dtype=np.float64)
            self.Update()
    
    def OnMousePlotPress(self,event):
        toUpdate = np.array(range(len(self.mt)))
        toUpdate_graphSpace = toUpdate + self.mouseStartIndex
        #TODO: These three lines are so dirty that they might as well be shrown to the composter... Please fix
        toUpdate_graphSpace + 1
        if self.mouseStartIndex == 0:
            toUpdate_graphSpace -= 2
        
        #toUpdate_graphSpace += 1
        toUpdate_graphSpace = np.array([x for x in toUpdate_graphSpace if x >= 0])
        toUpdate = toUpdate[len(toUpdate)-len(toUpdate_graphSpace):]
        self.s[toUpdate_graphSpace] = self.ms[toUpdate]
        self.Update()

    def _calcInitalPlot(self):
        self.t = arange(0.0, 3.0, self.pointSpacing)
        self.s = sin(2 * pi * self.t)*3.3
        self.mt = []
        self.ms = []
    
    def _bitScaling(self):
        self.rs = _numbaBitScaling(self.rs, self.settings["bits"], self.settings["signed"], self.settings["maxVal"])
    
    def _applyRSTime(self):
       
        riseTime = self.settings["riseTime"]
        self.st,self.ss = np.array([]),np.array([])
        pointsForward = int(riseTime/self.pointSpacing/2)
        pointsBackward = int(riseTime/self.pointSpacing/2)
        is2Del = []
        for i,_ in enumerate(self.rs):
            if (higher := self.rs[i] > self.rs[i-1]) or (lower := self.rs[i] < self.rs[i-1]):
                if i-1-pointsBackward >= 0 and i+pointsForward < len(self.rs):
                    point1 = (self.rt[i-1-pointsBackward],self.rs[i-1-pointsBackward])
                    point2 = (self.rt[i+pointsForward],self.rs[i+pointsForward])
                    addX, addY = numbaP2PRise(point1,point2,pointsForward+pointsBackward,30)
                    self.st = np.append(self.st,addX)
                    self.ss = np.append(self.ss,addY)
                    is2Del.append(range(i-pointsBackward,i+pointsForward))
        self.rs = np.delete(self.rs,is2Del)
        self.rt = np.delete(self.rt,is2Del)

    def _doMouseOverPlot(self):#TODO: needs to be faster
        self.mt, self.ms, mouseStartIndex, _ = _numbaMouseOverCalc(self.mouseXY[0],self.mouseXY[1],self.pointSpacing,self.mouseAreaWidth,self.bt,self.bs,self.gaussianCurve)
        self.mouseStartIndex = mouseStartIndex

    def _applyPlotSettings(self):
        self.rt = copy(self.t)
        self.rs = copy(self.s)
        self._bitScaling()
        self.bt = copy(self.rt)
        self.bs = copy(self.rs)
        self._applyRSTime()

    def Update(self):
        self.axes.clear()
        self._applyPlotSettings()
        self._doMouseOverPlot()
        self._draw()

    def _draw(self):
        self.axes.plot(self.st, self.ss, color='orange', linewidth=0.3)
        self.axes.plot(self.rt, self.rs, marker='.', linewidth=0)
        self.axes.plot(self.mt, self.ms, marker='.', linewidth=0)
        self.axes.margins(0.3)
        self.canvas.draw()

class nextPanel(wx.Panel):
    def __init__(self, *args, **kw):
        super(nextPanel, self).__init__(*args, **kw)
        st = wx.StaticText(self, label="more text! woooooo!")
        font = st.GetFont()
        #fam = font.GetFamily()
        font.SetFamily(wx.FONTFAMILY_SCRIPT)
        font.SetFaceName("Comic Sans MS")
        font = font.Italic()
        font = font.Bold()
        font.PointSize = int(1.5*font.PointSize)
        st.SetFont(font)

class helloPanel(wx.Panel):
    def __init__(self, *args, **kw):
        super(helloPanel, self).__init__(*args, **kw)
        self.SetBackgroundColour("pink")
        # put some text with a larger bold font on it
        st = wx.StaticText(self, label="Hello World!")
        font = st.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st.SetFont(font)

        # and create a sizer to manage the layout of child widgets
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(st, wx.SizerFlags().Border(wx.TOP|wx.LEFT, 25))
        self.SetSizer(sizer)

class appFileMenu(wx.Menu):
    def __init__(self, *args, **kw):
        super(appFileMenu, self).__init__(*args, **kw)
        # Make a file menu with Hello and Exit items
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        self.helloItem = self.Append(-1, "&Hello...\tCtrl-H",
                "Help string shown in status bar for this menu item")
        self.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        self.exitItem = self.Append(wx.ID_EXIT)

class appHelpMenu(wx.Menu):
    def __init__(self, *args, **kw):
        super(appHelpMenu, self).__init__(*args, **kw)
        # Make a help menu with About and Help items
        self.aboutItem = self.Append(wx.ID_ABOUT)

class appPlotMenu(wx.Menu):
    def __init__(self, *args, **kw):
        super(appPlotMenu, self).__init__(*args, **kw)
        self.helloItem = self.Append(-1, "&Hello...\tCtrl-H",
                "Help string shown in status bar for this menu item")
        self.AppendSeparator()
        self.sinCosItem =  self.Append(206, 'Draw1 - sin, cos',
                    'Draw Sin and Cos curves')
        #self.Bind(wx.EVT_MENU, self.OnPlotDraw1, id=206)

class mainFrame(wx.Frame):
    #A Frame that says Hello World
    def __init__(self, *args, **kw):
        super(mainFrame, self).__init__(*args, **kw)
        self.BackgroundColour = wx.Colour(255, 255, 255)
        frameIcon = wx.Icon("./icons/wxwin.ico")
        self.SetIcon(frameIcon)
        self.makeMenuBar()
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.plotPanels = []
        self.plotPanels.append(plotPanel(self))
        self.plotPanels.append(plotPanel(self))
        
        for i in range(0, len(self.plotPanels)):
            vbox.Add(self.plotPanels[i], 1, wx.EXPAND)
            self.plotPanels[i]._draw()
        
        self.terminal = wx.TextCtrl(self, style=wx.TE_RIGHT)
        vbox.Add(self.terminal, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
        self.SetSizer(vbox)
        
        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Welcome to wxPython!")

    def makeMenuBar(self):
        #A menu bar is composed of menus, which are composed of menu items.
        #This method builds a set of menus and binds handlers to be called
        #when the menu item is selected.
        menuBar = wx.MenuBar()#appMenuBar()
        menuBar.fileMenu = appFileMenu()
        menuBar.Append(menuBar.fileMenu, "&File")
        menuBar.helpMenu = appHelpMenu()
        menuBar.Append(menuBar.helpMenu, "&Help")
        menuBar.plotMenu = appPlotMenu()
        menuBar.Append(menuBar.plotMenu, "&Plot")
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.OnHello, menuBar.fileMenu.helloItem)
        self.Bind(wx.EVT_MENU, self.OnHello, menuBar.plotMenu.helloItem)
        self.Bind(wx.EVT_MENU, self.onTrigPlot, menuBar.plotMenu.sinCosItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  menuBar.fileMenu.exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuBar.helpMenu.aboutItem)

    def OnExit(self, event):
        #Close the frame, terminating the application.
        self.Close(True)

    def OnHello(self, event):
        #Say hello to the user.
        wx.MessageBox("Hello again from wxPython")

    def OnAbout(self, event):
        #Display an About Dialog
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK|wx.ICON_INFORMATION)
    
    def onTrigPlot(self, event):
        self.plotPanel.plotTrig()

if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = mainFrame(None, title="'Hello World' ;)", size=(1200, 1000))
    frm.Show()
    app.MainLoop()