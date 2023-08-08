import pyqtgraph as pg
from pyqtgraph import mkQApp


class Plotter(pg.PlotWidget):
    sigDataChanged = pg.Qt.QtCore.Signal()

    def __init__(self, parent=None, background='default', plotItem=None, **kargs):
        super().__init__(parent, background, plotItem, **kargs)

        self._xdata = []
        self._ydata = []
        self._yavg = []
        self._ydecay = .01
        self._xdata_set = False

        self._target_id = None

        self.sigDataChanged.connect(self.replot)

    def replot(self):
        self.plotItem.plot(
            x=self._xdata,
            y=self._ydata,
            clear=True,
            pen='red',
        )
        self.plotItem.plot(
            x=self._xdata,
            y=self._yavg,
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
