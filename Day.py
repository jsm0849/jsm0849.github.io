class Day:
    temps = []
    rains = []

    def __init__(self, day, month):
        self.day = day
        self.month = month

    def addTemp(self, temp):
        self.temps.append(temp)

    def addRain(self, rain):
        self.rains.append(rain)

    def getMedianTemp(self):
        for i in range(len(self.temps)):
            for j in range(len(self.temps) - 1):
                if float(self.temps[j]) < float(self.temps[j + 1]):
                    temporaryTemp = self.temps[j]
                    self.temps[j] = self.temps[j + 1]
                    self.temps[j + 1] = temporaryTemp
        return self.temps[int(len(self.temps) / 2)]

    def getMedianRains(self):
        for i in range(len(self.rains)):
            for j in range(len(self.rains) - 1):
                if float(self.rains[j]) < float(self.rains[j + 1]):
                    temporaryRain = self.rains[j]
                    self.rains[j] = self.rains[j + 1]
                    self.rains[j + 1] = temporaryRain
        return self.rains[int(len(self.rains) / 2)]