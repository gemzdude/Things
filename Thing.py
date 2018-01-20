from Xform import Xform


class Thing(object):


    def __init__(self, guess):
        self.guess = ""
        self.things = {}
        self.guess = Xform.encode(guess.upper())

    def getGuess(self):
        return Xform.decode(self.guess)

    def addThing(self, newQuestion, newThing):
        newKey = Xform.encode(newQuestion.upper())
        self.things[newKey] = newThing
        pass
