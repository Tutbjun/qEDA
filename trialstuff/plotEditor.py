"""#wxPython
import wx

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

class appMenuBar(wx.MenuBar):
    def __init__(self, *args, **kw):
        super(appMenuBar, self).__init__(*args, **kw)
        # Make a file menu with Hello and Exit items
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        self.fileMenu = appFileMenu()
        self.helpMenu = appHelpMenu()
        self.Append(self.fileMenu, "&File")
        self.Append(self.helpMenu, "&Help")

class mainFrame(wx.Frame):
    #A Frame that says Hello World
    def __init__(self, *args, **kw):
        super(mainFrame, self).__init__(*args, **kw)
        
        self.pnl = helloPanel(self)
        #self.pn2 = nextPanel(self)
        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Welcome to wxPython!")

    def makeMenuBar(self):
        #A menu bar is composed of menus, which are composed of menu items.
        #This method builds a set of menus and binds handlers to be called
        #when the menu item is selected.
        menuBar = appMenuBar()
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnHello, menuBar.fileMenu.helloItem)
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


if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = mainFrame(None, title='Hello World 2')
    frm.Show()
    app.MainLoop()"""

#calculator example
import wx


class Example(wx.Frame):

    def __init__(self, parent, title):
        super(Example, self).__init__(parent, title=title)

        self.InitUI()
        self.Centre()


    def InitUI(self):

        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.display = wx.TextCtrl(self, style=wx.TE_RIGHT)
        vbox.Add(self.display, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=4)
        gs = wx.GridSizer(5, 4, 5, 5)

        gs.AddMany( [(wx.Button(self, label='Cls'), 0, wx.EXPAND),
            (wx.Button(self, label='Bck'), 0, wx.EXPAND),
            (wx.StaticText(self), wx.EXPAND),
            (wx.Button(self, label='Close'), 0, wx.EXPAND),
            (wx.Button(self, label='7'), 0, wx.EXPAND),
            (wx.Button(self, label='8'), 0, wx.EXPAND),
            (wx.Button(self, label='9'), 0, wx.EXPAND),
            (wx.Button(self, label='/'), 0, wx.EXPAND),
            (wx.Button(self, label='4'), 0, wx.EXPAND),
            (wx.Button(self, label='5'), 0, wx.EXPAND),
            (wx.Button(self, label='6'), 0, wx.EXPAND),
            (wx.Button(self, label='*'), 0, wx.EXPAND),
            (wx.Button(self, label='1'), 0, wx.EXPAND),
            (wx.Button(self, label='2'), 0, wx.EXPAND),
            (wx.Button(self, label='3'), 0, wx.EXPAND),
            (wx.Button(self, label='-'), 0, wx.EXPAND),
            (wx.Button(self, label='0'), 0, wx.EXPAND),
            (wx.Button(self, label='.'), 0, wx.EXPAND),
            (wx.Button(self, label='='), 0, wx.EXPAND),
            (wx.Button(self, label='+'), 0, wx.EXPAND) ])

        vbox.Add(gs, proportion=1, flag=wx.EXPAND)
        self.SetSizer(vbox)


def main():

    app = wx.App()
    ex = Example(None, title='Calculator')
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()