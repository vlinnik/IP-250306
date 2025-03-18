import sys
from pysca import app
from pysca.device import PYPLC
import pygui.navbar as navbar
from concrete6 import concrete6

# import subprocess
# logic = subprocess.Popen(["python3", "src/krax.py"])

def main():
    import argparse
    args = argparse.ArgumentParser(sys.argv)
    args.add_argument('--device', action='store', type=str, default='192.168.2.10', help='IP address of the device')
    ns = args.parse_known_args()[0]
    
    dev = PYPLC(ns.device)
    app.devices['PLC'] = dev
    app.animate(concrete6.instance)

    Home = app.window('ui/Home.ui')
    navbar.instance.show() 
    navbar.append(Home)
    navbar.tools(app.window('ui/Extensions.ui'))

    navbar.instance.setWindowTitle(Home.windowTitle())

    concrete6.setMainWindow(navbar.instance)
    concrete6.setContainerPanels( [Home.doserpanel,Home.doserpanel_2,Home.doserpanel_3,Home.doserpanel_4,Home.doserpanel_5] )
    concrete6.reload( )

    dev.start()
    app.start(ctx=globals())

    concrete6.save( )

# logic.terminate( )

if __name__=='__main__':
    main( )
