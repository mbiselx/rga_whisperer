import pyqtgraph as pg
import pyqtgraph.exporters
from pyqtgraph import mkQApp, QtGui


class Plotter(pg.PlotWidget):
    sigDataChanged = pg.Qt.QtCore.Signal()

    def __init__(self, parent=None, background='default', plotItem=None, **kargs):
        super().__init__(parent, background, plotItem, **kargs)

        self._xdata = []
        self._ydata = []
        self._yavg = []
        self._ydecay = .01
        self.miny = 1e-10
        self._xdata_set = False

        self._target_id = None

        self.sigDataChanged.connect(self.replot)
        self.sigTransformChanged.connect(self.replot)

        self.plotItem.setLogMode(False, True)
        self.plotItem.showGrid(True, True)

        self.plotItem.getAxis('left').setLabel('Ion Current', units='A')
        self.plotItem.getAxis('bottom').setLabel('Atomic Mass', units='u')

        self.save_action = QtGui.QAction('save', self)
        self.save_action.setShortcut(QtGui.QKeySequence('Ctrl+S'))
        self.save_action.triggered.connect(self.save)
        self.addAction(self.save_action)

    def replot(self):

        if self.plotItem.getAxis('left').logMode:
            ybars = sum(
                map(list, zip(len(self._ydata) *
                    [self.miny], self._ydata)),
                start=[]
            )
        else:
            ybars = sum(
                map(list, zip(len(self._ydata)*[0.], self._ydata)),
                start=[]
            )

        self.plotItem.plot(
            x=sum(
                map(list, zip(self._xdata, self._xdata)),
                start=[],
            ),
            y=ybars,
            connect='pairs',
            clear=True,
            pen='red',
        )
        # if not self.plotItem.getAxis('left').logMode or all(y >= self.miny for y in self._yavg if y > 0):
        self.plotItem.plot(
            x=self._xdata,
            y=self._yavg,
            pen='white',
            brush='white',
        )

    def set_target_id(self, id: bytes):
        self._target_id = id

    def set_xdata(self, data: list):
        self._xdata = data
        self._xdata_set = True

    def set_ydata(self, data: list):

        # set the x-axis first, if it hase not been set yet
        if not self._xdata_set:
            self._xdata = list(range(len(data)))

        # crop the incoming ydata to the x-axis
        self._ydata = data[:len(self._xdata)]

        # do an exponential average thingy to reduce noise
        if len(self._yavg) == len(self._ydata):
            self._yavg = list(map(
                lambda yy: (yy[0]*(1-self._ydecay)+yy[1]*self._ydecay),
                zip(self._yavg, self._ydata)
            ))
        else:
            self._yavg = self._ydata.copy()

        # replot !
        self.sigDataChanged.emit()

    def save(self):
        if not hasattr(self, "_count"):
            self._screenshot_count = 1
        print(f"saving as 'screenshot_{self._screenshot_count}.png'")
        exporter = pyqtgraph.exporters.ImageExporter(self.plotItem)
        exporter.export(f'screenshot_{self._screenshot_count}.png')
        self._screenshot_count += 1
