import datetime
class CoresPerSecond:

    def __init__(self, dbm, entries):
        self.dbm = dbm

        query = "select UNIX_TIMESTAMP(MIN(executionStartTime)), UNIX_TIMESTAMP(MAX(executionStopTime)) from submissions where UNIX_TIMESTAMP(executionStartTime) > 0 and dagNode != 'A' and dagNode != 'B' order by executionStartTime;"

        results = self.dbm.execCommandN(query)
        startTime = results[0][0]
        stopTime = results[0][1]

        self.values = []
        # cycle through the seconds, counting the number of cores being used
        # during each second
        for thisSecond in range(startTime, stopTime+1):
            x = 0
            length = entries.getLength()
            for i in range(length):
                ent = entries.getEntry(i)
                if ent.dagNode == 'A':
                    continue
                if ent.dagNode == 'B':
                    continue
                if (thisSecond >= ent.executionStartTime) and (thisSecond <= ent.executionStopTime):
                    x = x + 1
            
            self.values.append([thisSecond,x])

        # count the number of cores used at maximum
        # also calculate the first time that many cores were used
        # and the last time that many cores were used.
        self.maximumCores = -1
        self.timeFirstUsed = None
        self.timeLastUsed = None
        for j in range(len(self.values)):
            val = self.values[j]
            timeValue = val[0]
            cores = val[1]
            # this counts the times the maximum cores
            # were first used
            if cores > self.maximumCores:
                self.maximumCores = cores
                self.timeFirstUsed = timeValue
            # this extra conditional also tallies the
            # last time all the cores were used
            if cores == self.maximumCores:
                self.timeLastUsed = timeValue

    def getValues(self):
        return self.values
    
    def getMaximumCores(self):
        return self.maximumCores

    def maximumCoresFirstUsed(self):
        return self.timeFirstUsed

    def maximumCoresLastUsed(self):
        return self.timeLastUsed