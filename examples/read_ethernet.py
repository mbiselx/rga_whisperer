from rga_whisperer.gui import Plotter, mkQApp
from rga_whisperer.interfaces import ethernet
from rga_whisperer.message_types import *


app = mkQApp('Ethernet Live Feed')
gui = Plotter()

app.exec()
