class Event:
    def __init__(self,name, positions, onEvent):
        self.positions = positions
        self.onEvent = onEvent
        self.name = name

class EventManager:
    def __init__(self):
        self.events = []
        self.positions = {}

    def populatePositions():
        for event in self.events:
            for position in event.positions:
                self.positions[position] = event

    def getEvent(position):
        return self.positions[position]

    def runEvent(position):
        event = self.positions[position]
        if event != None:
            event.onEvent()


## On Even Definitions go here
