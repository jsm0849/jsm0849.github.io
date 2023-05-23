class Day:

    def __init__(self, day, month, id):
        self.day = day
        self.month = month
        self.id = id
        self._temps = []
        self._rains = []

    def addTemp(self, temp):
        self._temps.append(temp)

    def addRain(self, rain):
        self._rains.append(rain)

    def getMedianTemp(self):
        for i in range(len(self._temps)):
            for j in range(len(self._temps) - 1):
                if float(self._temps[j]) < float(self._temps[j + 1]):
                    temporaryTemp = self._temps[j]
                    self._temps[j] = self._temps[j + 1]
                    self._temps[j + 1] = temporaryTemp
        return self._temps[int(len(self._temps) / 2)]

    def getMedianRain(self):
        for i in range(len(self._rains)):
            for j in range(len(self._rains) - 1):
                if float(self._rains[j]) < float(self._rains[j + 1]):
                    temporaryRain = self._rains[j]
                    self._rains[j] = self._rains[j + 1]
                    self._rains[j + 1] = temporaryRain
        return self._rains[int(len(self._rains) / 2)]