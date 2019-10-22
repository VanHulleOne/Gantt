# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 16:24:03 2019

gantt.py

@author: Myself
"""

from queue import PriorityQueue
from collections import namedtuple

#PreReq = namedtuple('PreReq', 'op state')

Event = namedtuple('Event', 'endTime op')

#events = PriorityQueue()

OP = 0
STATE = 1

WAITING = 0
WORKING = 1

NOT_DONE = False
DONE = True

steps = 0

class Op:
    
    def __init__(self, name, prereqs=None, duration=0, initial=False):
        self.name = name
        if prereqs is None:
            prereqs = []
        self.prereqs = prereqs
        self.prereqSignals = {prereq: initial for prereq in self.prereqs}
        self.duration = duration
        self.postOps = []
        self.subOps = []
        self.initial = initial
        self.state = WAITING
        self.eventList = []

    
    def setPrereqs(self):
        self.prereqs = [ops[prereq] for prereq in self.prereqs]
        for op in self.prereqs:
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
        for event in self.eventList:
            print('  '*level, event)
            event.op.eventPrint(level+1)
    
    def runSubOps(self, startTime):
        currTime = startTime
        if steps > 6:
            raise Exception()
        events = PriorityQueue()
        for op in self.subOps:
            endTime = op.startOp(currTime)
            if endTime >= 0:
                events.put(Event(endTime, op))
        initialState = tuple(op.state for op in self.subOps)
        
        numLoops = 0
        
        while not events.empty():
            if numLoops > 6:
                break
            numLoops += 1
            currEvent = events.get()
            self.eventList.append(currEvent)
#            print(currEvent)
            currTime = currEvent.endTime
            for op in currEvent.op.finishOp():
                endTime = op.startOp(currTime)
                if endTime >= 0:
                    newEvent = Event(endTime, op)
                    events.put(newEvent)
                    
            currState = tuple(op.state for op in self.subOps)
            if initialState == currState:
                break 
        
#        print('{} cycle time:'.format(self.name), currTime-startTime)
        return currTime
    
    def __hash__(self):
        return hash(self.name)
    
    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        return str(self) == str(other)
    
    def __repr__(self):
        return 'Op({})'.format(self.name)

mainOP = Op('Main')    
indexOP = Op('Index', ['Print', 'Rotate'], 0.25, initial=True)
printOP = Op('Print', ['Index'], 0.75)
rotateOP = Op('Rotate', ['Index'], 0)

rDownOP = Op('rDown', [], 0.25)
rRotateOP = Op('rRotate', ['rDown'], 1)
rUpOP = Op('rUp', ['rRotate'], 0.4)

rotateOP.subOps = [rDownOP, rRotateOP, rUpOP]


mainOP.subOps = [indexOP, printOP, rotateOP]

ops = {'Index': indexOP,
       'Print': printOP,
       'Rotate': rotateOP,
       'rDown': rDownOP,
       'rRotate': rRotateOP,
       'rUp': rUpOP,
       }

for op in ops.values():
    op.setPrereqs()

mainOP.startOp(0)
mainOP.eventPrint()







