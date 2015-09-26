class Event:
    def __init__(self,name, positions, onEvent):
        self.positions = positions
        self.onEvent = onEvent
        self.name = name

class EventManager:
    def __init__(self, events):
        self.events = events
        self.positions = {}
        self.populatePositions()

    def populatePositions(self):
        for event in self.events:
            for position in event.positions:
                self.positions[position] = event

    def getEvent(self, position):
        return self.positions[position]

    def runEvent(self, position, triggering_object):
        if position in self.positions:
            self.positions[position].onEvent(triggering_object)


## On Even Definitions go here
