from UI import drawScene
from units import unit

uSeconds = unit('us')
mSeconds = unit('ms')
Seconds = unit('s')




def graphDrawerScene():#TODO: make this... It should be a sort of interactive graph drawing window where you can make a waveform with a resolution, set rise/falltimes, set logic type, and such. The output should a cosine transform
    bitResolution = 1
    graphSize = uSeconds(10)
    drawScene('graphdrawer')
    return



def main():
    graphDrawerScene()

if __name__ == '__main__':
    main()