#from concurrent.futures import thread

from doctest import master
from os import path
from PIL import Image,ImageTk
import tkinter as tk

window = tk.Tk()
sw,sh = window.winfo_screenwidth(),window.winfo_screenheight()
w,h = sw//2,sh//2
a,b = (sw-w)//2-sw//2-sw//4-5,(sh-h)//2+sh//2-sh//8-60#sloppy positioning @ second monitor
window.geometry('%sx%s+%s+%s'%(w,h,a,b))
canvas = tk.Canvas(window, width= 1920, height= 1080)    
canvas.pack()

masterScale = 20

class sprite():
    pos = (0,0)
    img = None
    def __init__(self, pos, img = None):
        self.pos = pos
        self.img = img

def renderCircuit(circuit):
    sprites = []
    for c in circuit.components:
        c._updateIcon(masterScale)
        pos = c.pos[0]*masterScale,c.pos[1]*masterScale
        sprites.append(sprite(pos,c.icon))
    for s in sprites:
        canvas.create_image(s.pos[0],s.pos[1],  image=s.img)
        canvas.pack()
    for k in circuit.nets.keys():
        n = circuit.nets[k]
        pinPositions = []
        for c in circuit.components:
            scale = c.scale[0]*masterScale,c.scale[1]*masterScale
            pos = c.pos[0]*masterScale,c.pos[1]*masterScale
            for i,con in enumerate(c.connections):
                if con == n.id:
                    pinPositions.append(c.pinPositions[i])#TODO: why this line??
                    pinPositions[-1] = (pinPositions[-1][0]*scale[0]+pos[0],pinPositions[-1][1]*scale[1]+pos[1])
        for i in range(len(pinPositions)-1):
            canvas.create_line(
                *pinPositions[i], 
                *pinPositions[i+1], 
                fill="#000fff000",
                width=masterScale/10
                )
            canvas.pack()
            #plt.plot([pinPositions[i][0], pinPositions[i+1][0]], [pinPositions[i][1], pinPositions[i+1][1]], color='k', linestyle='-', linewidth=1)
    tk.mainloop()

def imgInsert(size, pos, imgPath = None, img = None):
    if imgPath:
        if path.basename(imgPath) == imgPath:
            imgPath = path.join(path.dirname(__file__),"opAmpIcon.png")
        img = Image.open(imgPath)
    img = img.resize(size, Image.ANTIALIAS)
    sprite = ImageTk.PhotoImage(img)   
    canvas.create_image(pos[0],pos[1], image=sprite)
