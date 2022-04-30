#wxPython
from copy import copy
from struct import calcsize
import wx
from wx.lib import plot as wxplot
import numpy as np
from numpy import arange, sin, pi
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

class plotPanel(wx.Panel):
    pointSpacing = 0.001

    def __init__(self, *args, **kw):
        super(plotPanel, self).__init__(*args, **kw)
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()
        self.bits = 1
        self.signed = False
        self.riseTime = 0.05
        self.maxVal = 3.3
        self._calcInitalPlot()
        self._applyPlotSettings()
    
    def _calcInitalPlot(self):
        self.t = arange(0.0, 3.0, self.pointSpacing)
        self.s = sin(2 * pi * self.t)*3.3
    
    def _bitScaling(self):
        self.rs /= self.maxVal
        #rs should be rounded to bits
        scalar = 2**(self.bits-1)
        if self.signed:
            scalar /= 2
        self.rs *= scalar
        self.rs = np.round(self.rs)
        if not self.signed:
            self.rs = [x if x > 0 else 0 for x in self.rs]
        self.rs = np.array(self.rs,dtype=float)/scalar
        self.rs *= self.maxVal
    
    def _applyRSTime(self):
        def makeP2PRise(point1,point2,dataPoints,amount=1):
            #use superellipse formula to make an amount of rise/fall graphs
            if amount == 1:
                ns = [1]
            else:
                ns = np.linspace(np.log10(0.25),np.log10(10),amount)
                ns = np.power(10,ns)
            def curve(xs,n):
                def f(x,n):
                    return (1 - x**n)**(1/n)
                return [f(x,n) for x in xs]
            X = np.linspace(0,1,dataPoints)
            ys = np.array([curve(X,n) for n in ns])
            X *= (point2[0]-point1[0])
            X += point1[0]
            ys *= np.sign(point1[1]-point2[1])
            ys *= abs(point2[1]-point1[1])
            ys += point2[1]
            #ys *= -1
            
            xs = np.array([X for y in ys])
            return xs.flatten(),ys.flatten()
        self.st,self.ss = np.array([]),np.array([])
        pointsForward = int(self.riseTime/self.pointSpacing/2)
        pointsBackward = int(self.riseTime/self.pointSpacing/2)
        is2Del = []
        for i,_ in enumerate(self.rs):
            if (higher := self.rs[i] > self.rs[i-1]) or (lower := self.rs[i] < self.rs[i-1]):
                point1 = (self.rt[i-1-pointsBackward],self.rs[i-1-pointsBackward])
                point2 = (self.rt[i+pointsForward],self.rs[i+pointsForward])
                addX, addY = makeP2PRise(point1,point2,pointsForward+pointsBackward,30)
                self.st = np.append(self.st,addX)
                self.ss = np.append(self.ss,addY)
                is2Del.append(range(i-1-pointsBackward,i+pointsForward))
        self.rs = np.delete(self.rs,is2Del)
        self.rt = np.delete(self.rt,is2Del)

    def _applyPlotSettings(self):
        self.rt = copy(self.t)
        self.rs = copy(self.s)
        self._bitScaling()
        self._applyRSTime()


    def draw(self):
        self.axes.plot(self.st, self.ss, color='orange', linewidth=0.3)
        self.axes.plot(self.rt, self.rs, marker='.', linewidth=0)
        

class settingsPanel(wx.Panel):
    def __init__(self, *args, **kw):
        super(settingsPanel, self).__init__(*args, **kw)
        self.BackgroundColour = wx.Colour(255, 255, 255)
        st = wx.StaticText(self, label="settings:")
        font = st.GetFont()
        #fam = font.GetFamily()
        font.SetFamily(wx.FONTFAMILY_SCRIPT)
        font.SetFaceName("Comic Sans MS")
        font = font.Italic()
        font = font.Bold()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.Fit()

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


"""class appMenuBar(wx.MenuBar):
    def __init__(self, *args, **kw):
        super(appMenuBar, self).__init__(*args, **kw)
        # Make a file menu with Hello and Exit items
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        self.fileMenu = appFileMenu()
        self.helpMenu = appHelpMenu()
        self.plotMenu = appPlotMenu()
        self.Append(self.fileMenu, "&File")
        self.Append(self.helpMenu, "&Help")
        self.Append(self.plotMenu, "&Plot")"""

class mainFrame(wx.Frame):
    #A Frame that says Hello World
    def __init__(self, *args, **kw):
        super(mainFrame, self).__init__(*args, **kw)
        self.BackgroundColour = wx.Colour(255, 255, 255)
        frameIcon = wx.Icon("./icons/wxwin.ico")
        self.SetIcon(frameIcon)
        self.makeMenuBar()
        vbox = wx.BoxSizer(wx.VERTICAL)
        #gs = wx.GridSizer(2, 1, 5, 5)
        self.settingsPanel = settingsPanel(self)
        vbox.Add(self.settingsPanel, 1, wx.EXPAND)
        vbox.Add(wx.StaticLine(self), 0, wx.ALL|wx.EXPAND, 5)
        self.plotPanel = plotPanel(self)
        vbox.Add(self.plotPanel, 1, wx.EXPAND)
        

        self.plotPanel.draw()
        """gs.AddMany([
            #(helloPanel(self), 0, wx.EXPAND),
            (self.settingsPanel, 0, wx.EXPAND),
            (self.plotPanel, 0, wx.EXPAND)])
        vbox.Add(gs, proportion=1, flag=wx.EXPAND)"""
        self.terminal = wx.TextCtrl(self, style=wx.TE_RIGHT)
        vbox.Add(self.terminal, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
        self.SetSizer(vbox)
        # create a menu bar
        

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
    frm = mainFrame(None, title='Hello World 2', size=(1000, 800))
    frm.Show()
    app.MainLoop()