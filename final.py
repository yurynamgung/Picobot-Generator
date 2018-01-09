import random
import copy

keyDir = ['xxxx', 'Nxxx', 'NxWx', 'xxWx',
          'xxWS', 'xxxS', 'xExS', 'xExx', 'NExx']
POSSIBLE_MOVES = ['N', 'E', 'W', 'S']

HEIGHT = 25
WIDTH = 25
NUMSTATES = 5


class Program:
    def __init__(self):
        #keys are tuples
        self.rules = {}

    """returns a random set of 45 rules"""

    def randomize(self):
        #for each state/dir combination, assign random state/coord
        for state in range(NUMSTATES):
            for pattern in keyDir:
                randomState = random.choice(range(NUMSTATES))

                #make sure movedir isn't illegal
                #pattern = direction rule/illegal to go where wall exists
                movedir = random.choice(POSSIBLE_MOVES)
                while movedir in pattern:
                    movedir = random.choice(POSSIBLE_MOVES)

                self.rules[(state, pattern)] = (movedir, randomState)

    """returns next move and state in tuple form"""

    def getMove(self, state, surroundings):
        return self.rules[(state, surroundings)]

    """choose a single rule and change value for that rule"""

    def mutate(self):
        keyChange = random.choice(list(self.rules))
        randomState = random.choice(range(NUMSTATES))

        #new dir and state
        #only possible directions allowed
        movedir = random.choice(POSSIBLE_MOVES)
        while movedir in keyChange:
            movedir = random.choice(POSSIBLE_MOVES)
        newState = random.choice(range(NUMSTATES))

        self.rules[(randomState, keyChange)] = (movedir, newState)

    """randomly chooses rules from self and other to 'pass on'
    returns offspring w these new rules"""

    def crossover(self, other):
        default = copy.deepcopy(other)
        choice = random.choice(range(4))
        # if choice is 0, keep only 0 state rules
        # if choice is 1, keep only 0 & 1 state rules
        # etc.
        # if choice is 3, keep all except state 4
        # (state 0 will always be self, state 4 will always be other)

        while (choice >= 0):
            for key in list(self.rules):
                state, pattern = key
                if choice == state:
                    default.rules[key] = self.rules[key]
            choice -= 1
        return default

    """self.rules in string form that can be copy/pasted into picobot"""

    def __repr__(self):
        s = ''
        keys = list(self.rules.keys())
        #sorted(keys)
        for key in keys:
            s += str(key) + ' -> ' + str(self.rules[key])
            s += "\n"

        return s

    def __gt__(self, other):
        """ greater than operator - works randomly, but works! """
        return random.choice([True, False])

    def __lt__(self, other):
        """ less than operator - works randomly, but works! """
        return random.choice([True, False])


class World:
    def __init__(self, initial_row, initial_col, program):
        self.prow = initial_row
        self.pcol = initial_col
        self.state = 0
        self.prog = program
        self.room = [[' '] * WIDTH for row in range(HEIGHT)]

    """return surroundings string i.e. 'xExx' for current pos of Picobot"""

    def getCurrentSurroundings(self):
        s = ''

        #check if NEWS is wall
        if self.prow == 1:
            s += 'N'
        else:
            s += 'x'

        if self.pcol == WIDTH - 1:
            s += 'E'
        else:
            s += 'x'

        if self.pcol == 1:
            s += 'W'
        else:
            s += 'x'

        if self.prow == HEIGHT - 1:
            s += 'S'
        else:
            s += 'x'

        return s

    """updates self.room, state, row, and col of Picobot using self.prog"""

    def step(self):
        surr = self.getCurrentSurroundings()
        nextMove, nextState = self.prog.rules[(self.state, surr)]

        #update room: marked as visited
        self.room[self.prow][self.pcol] = 'o'

        #update self position and state
        self.state = nextState
        if nextMove == 'N':
            self.prow -= 1
        if nextMove == 'E':
            self.pcol += 1
        if nextMove == 'W':
            self.pcol -= 1
        if nextMove == 'S':
            self.prow += 1

        #update room: new pico loc
        self.room[self.prow][self.pcol] = 'P'

    """input = # of steps to move"""

    def run(self, steps):
        for i in range(steps):
            self.step()

    """returns fraction of visited cells w 'o' marking"""

    def fractionVisitedCells(self):
        #count total blank cells (not walls)
        blank = 0
        for row in range(HEIGHT):
            for col in range(WIDTH):
                if (self.room[row][col] == 'o' or self.room[row][col] == ' '):
                    blank += 1

        #count total 'o's
        visited = 0
        for row in range(HEIGHT):
            for col in range(WIDTH):
                if (self.room[row][col] == 'o'):
                    visited += 1

        return visited / blank

    """make empty room w picobot"""

    def emptyRoom(self):

        # HEIGHT = rows
        # WIDTH = col
        # self.room[HEIGHT][WIDTH]
        """make walls"""
        self.room[0] = ['+'] + ['-'] * (WIDTH - 2) + ['+']
        self.room[HEIGHT - 1] = ['+'] + ['-'] * (WIDTH - 2) + ['+']
        for i in range(1, HEIGHT - 1):
            self.room[i][0] = '|'
            self.room[i][WIDTH - 1] = '|'

        """picobot"""
        self.room[self.prow][self.pcol] = 'P'

    def __repr__(self):
        s = ''
        for row in range(HEIGHT):
            for col in range(WIDTH):
                s += self.room[row][col]
            s += '\n'

        return s


"""generates input number of random programs"""


def generatePrograms(input):
    programList = []
    for i in range(input):
        a = Program()
        a.randomize()
        programList.append(a)

    return programList


"""average fitness fraction over the trials"""


def evaluateFitness(program, trials=20, steps=800):
    list = []
    while trials > 0:
        initialRow = random.choice(range(1, HEIGHT - 1))
        initialCol = random.choice(range(1, WIDTH - 1))

        w = World(initialRow, initialCol, program)
        w.emptyRoom()  # sets up walls and chooses random spot for picobot
        w.run(steps)  # runs program for given # of steps

        fract = w.fractionVisitedCells()
        list.append(fract)
        trials -= 1
    return sum(list) / len(list)


"""returns list of evolved programs"""


def GA(popsize, numgens):
    programList = generatePrograms(popsize)
    numParents = int(.1 * popsize)  # 10% of pop will be parents

    i = 0
    while i < numgens:
        fitnessList = []
        pfitList = []

        for program in programList:
            fitness = evaluateFitness(program)
            pfitList.append((fitness, program))
            fitnessList.append(fitness)

        sortedPFL = sorted(pfitList)
        # most fit 10% become parents
        parents = sortedPFL[len(sortedPFL) - numParents:]

        #extract just the programs from parents
        childList = []
        for p in parents:
            f, pr = p
            childList.append(pr)  # keep parents as part of next gen

        while len(childList) < popsize:
            #make children programs
            fitness1, parent1 = random.choice(parents)
            fitness2, parent2 = random.choice(parents)

            mnum = random.choice(range(30))  # 1/30 chance of mutation
            if mnum == 0:
                pmun = random.choice([parent1, parent2])
                pmun.mutate()  # determines if mutate more than one line

            child = parent1.crossover(parent2)
            childList.append(child)

        #print avg and max fitness

        avgFit = sum(fitnessList) / len(fitnessList)
        bestFit = max(fitnessList)
        print("Generation " + str(i))
        print('\t' + 'Average fitness: ' + str(avgFit))
        print('\t' + 'Best fitness: ' + str(bestFit))
        print('\n')

        programList = childList  # next gen
        i += 1

    saveToFile('pico.txt', max(programList))


def saveToFile(filename, p):
    """ saves the data from Program p
    to a file named filename """
    f = open(filename, "w")
    print(p, file=f)  # prints Picobot program from __repr__
    f.close()