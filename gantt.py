# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 16:24:03 2019

gantt.py

@author: Myself
"""

from queue import PriorityQueue
from collections import namedtuple

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
        self.prereqs = prereqs
        self.prereqSignals = {prereq: initial for prereq in self.prereqs}
        self.duration = duration
        self.postOps = []
        if subOps is None:
            subOps = []
        self.subOps = subOps
        self.initial = initial
        self.state = WAITING
        self.eventList = []

    
    def setPostOps(self):
        for opName in self.prereqs:
            op = opsDict[opName]
            op.postOps.append(self)
        
    def prereqsComplete(self):
        return all(status == DONE for status in self.prereqSignals.values())
    
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
            op.prereqSignals[self] = DONE
        self.prereqSignals = {preop: NOT_DONE for preop in self.prereqs}
        return self.postOps
    
    def eventPrint(self, level=0):
        if level == 0:
            print(self.name, 'Cycle Time: {:0.2f}'.format(self.eventList[-1].endTime))
        for event in self.eventList:
            print('  '*level, event)
            event.op.eventPrint(level+1)
    
    def runSubOps(self, startTime):
        currTime = startTime
        if steps > 6:
            raise Exception()
        events = PriorityQueue()
        for opName in self.subOps:
            op = opsDict[opName]
            endTime = op.startOp(currTime)
            if endTime >= 0:
                events.put(Event(endTime, op, endTime-startTime))
        initialState = tuple(opsDict[opName].state for opName in self.subOps)

        while not events.empty():
            currEvent = events.get()
            self.eventList.append(currEvent)
            currTime = currEvent.endTime
            for opName in currEvent.op.finishOp():
                op = opsDict[opName]
                endTime = op.startOp(currTime)
                if endTime >= 0:
                    newEvent = Event(endTime, op, endTime-currTime)
                    events.put(newEvent)
                    
            currState = tuple(opsDict[opName].state for opName in self.subOps)
            if initialState == currState:
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
                ]

opsDict = {op.name:op for op in masterOpList}
for op in masterOpList:
    op.setPostOps()
#rotateOP.subOps = [rDownOP, rRotateOP, rUpOP]
#
#
#mainOP.subOps = [indexOP, printOP, rotateOP]
#
#ops = {'Index': indexOP,
#       'Print': printOP,
#       'Rotate': rotateOP,
#       'rDown': rDownOP,
#       'rRotate': rRotateOP,
#       'rUp': rUpOP,
#       }
#
#for op in ops.values():
#    op.setPrereqs()

opsDict['Main'].startOp(0)
opsDict['Main'].eventPrint()







