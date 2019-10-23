# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 16:24:03 2019

gantt.py

@author: Myself
"""

from queue import PriorityQueue
from collections import namedtuple, Counter

#PreReq = namedtuple('PreReq', 'op state')

Event = namedtuple('Event', 'endTime op cycleTime')

#events = PriorityQueue()

OP = 0
STATE = 1

WAITING = 0
WORKING = 1

NOT_DONE = False
DONE = True

steps = 0

class Op:
    
    def __init__(self, name, prereqs=None, duration=0, *args, subOps=None, initial=False):
        self.name = name
        if prereqs is None:
            prereqs = []
        self.prereqs = Counter(prereqs)
        
        self.prereqCounts = Counter(prereqs if initial else None) # {prereq: initial for prereq in self.prereqs}
        self.duration = duration
        self.postOps = []
        if subOps is None:
            subOps = []
        self.subOps = subOps
        self.initial = initial
        self.state = WAITING
        self.eventList = []
        
    def prereqsComplete(self):
        return not bool(self.prereqs - self.prereqCounts)
#        return all(status == DONE for status in self.prereqSignals.values())
    
    def startOp(self, startTime):
        if self.prereqsComplete():
            self.state = WORKING
            if self.subOps:
                return self.runSubOps(startTime)
            return self.duration + startTime
        return -1

    def finishOp(self):
        self.state = WAITING
        for op in self.postOps:
            op.prereqCounts[self] += 1
        self.prereqCounts = Counter()
        return self.postOps
    
    def eventPrint(self, level=0):
        if level == 0:
            print(self.name, 'Cycle Time: {:0.2f}'.format(self.eventList[-1].endTime))
        for event in self.eventList:
            print('  '*level, event)
            event.op.eventPrint(level+1)
    
    def runSubOps(self, startTime):
        print('Op:', self.name)
        currTime = startTime
#        if steps > 6:
#            raise Exception()
        events = PriorityQueue()
        for op in self.subOps:
            endTime = op.startOp(currTime)
            if endTime >= 0:
                events.put(Event(endTime, op, endTime-startTime))
        initialState = tuple(Counter(op.prereqCounts.elements()) for op in self.subOps)
        
        print('Ini:', initialState)

        steps = 0
        while not events.empty() and steps <7:
            print('Step:', steps)
            steps += 1
            currEvent = events.get()
            self.eventList.append(currEvent)
            currTime = currEvent.endTime
            for op in currEvent.op.finishOp():
                endTime = op.startOp(currTime)
                if endTime >= 0:
                    newEvent = Event(endTime, op, endTime-currTime)
                    events.put(newEvent)
                    
            currState = tuple(Counter(op.prereqCounts.elements()) for op in self.subOps)
            print('Op:', self.name, 'Curr:', currState, 'Bool:', initialState == currState)
            if initialState == currState:
                print('Break')
                break 
            
        return currTime
    
    def __hash__(self):
        return hash(self.name)
    
    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        return str(self) == str(other)
    
    def __repr__(self):
        return 'Op({})'.format(self.name)

masterOpList = [Op('Main', subOps=['Index', 'Print', 'Rotate']),
                Op('Index', ['Print', 'Rotate'], 0.25, initial=True),
                Op('Print', ['Index'], 2.75),
                Op('Rotate', ['Index'], 0, subOps=['rDown', 'rRotate', 'rUp']),
                Op('rDown', [], 0.25),
                Op('rRotate', ['rDown'], 1),
                Op('rUp', ['rRotate'], 0.4),
                Op('PickTube', ['Index', 'PlaceTubes'], subOps='pApproach pGrab pRetract'.split()),
                Op('pApproach', [], 0.25),
                Op('pGrab', ['pApproach'], 0.25),
                Op('pRetract', ['pGrab'], 0.25),
                Op('PlaceTubes', {'PickTube':3}, 3.4),
                ]

opsDict = {op.name:op for op in masterOpList}

def setOps():
    for op in masterOpList:
        op.prereqs = Counter({opsDict[opName]: qty for opName, qty in op.prereqs.items()})
        op.subOps = [opsDict[opName] for opName in op.subOps]
        for preOp in op.prereqs.keys():
            preOp.postOps.append(op)

setOps()

opsDict['Main'].startOp(0)
opsDict['Main'].eventPrint()







