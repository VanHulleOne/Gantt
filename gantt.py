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
INTERLOCKED = 2

#NOT_DONE = False
#DONE = True

steps = 0

class Op:
    
    def __init__(self, name, prereqs=None, duration=0):
        self.name = name
        if prereqs is None:
            prereqs = []
        self.prereqs = prereqs
        self.duration = duration
        self.postOps = []
        self.subOps = []
        self._state = WAITING
        
    @property
    def state(self):
        if self._state == WORKING:
            return WORKING
        if any(prereq._state == WORKING for prereq in self.prereqs):
            self._state = INTERLOCKED
        else:
            self._state = WAITING
        return self._state
    
    def setPrereqs(self):
        self.prereqs = [ops[prereq] for prereq in self.prereqs]
        for op in self.prereqs:
            op.postOps.append(self)
        
    def prereqsComplete(self):
        return all(prereq.state!=WORKING for prereq in self.prereqs)
    
    def startOp(self, startTime):
#        print('Op:', self)
#        print('Pre:', self.prereqs)
#        print('States:', [op.state for op in self.prereqs])
        if self.prereqsComplete():
#            print('Op:', self)
            self._state = WORKING
            if self.subOps:
                return self.runSubOps(startTime)
            return self.duration + startTime
        return -1

    def finishOp(self):
        self._state = WAITING
        return self.postOps # + self.subOps
    
    def runSubOps(self, currTime):
        global steps
        steps += 1
        if steps > 6:
            raise Exception()
        events = PriorityQueue()
        for op in self.subOps:
            endTime = op.startOp(currTime)
            if endTime >= 0:
                events.put(Event(endTime, op))
#                print('Put event:', Event(endTime, op))
        initialState = tuple(op.state for op in self.subOps)
        
        numLoops = 0
        
        while not events.empty():
            if numLoops > 6:
                break
            numLoops += 1
            currEvent = events.get()
            print(currEvent)
            currTime = currEvent.endTime
            for op in currEvent.op.finishOp():
                endTime = op.startOp(currTime)
                if endTime >= 0:
                    newEvent = Event(endTime, op)
                    events.put(newEvent)
                    
            currState = tuple(op.state for op in self.subOps)
            if initialState == currState:
                break 
        
        print('Cycle time:', currTime)
        return currTime
    
    def __repr__(self):
        return 'Op({})'.format(self.name)

mainOP = Op('Main')    
indexOP = Op('Index', ['Print', 'Rotate'], 0.25)
printOP = Op('Print', ['Index'], 0.75)
rotateOP = Op('Rotate', ['Index'], 0)

rDownOP = Op('rDown', [], 0.25)
rRotateOP = Op('rRotate', ['rDown'], 1)
rUpOP = Op('rUp', ['rRotate'], 0.3)

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








