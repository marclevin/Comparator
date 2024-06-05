import ast
from tools import log
from astTools import *
from namesets import astNames
from ChangeVector import *
from State import *


def matchLists(x, y):
    """For each line in x, determine which line it best maps to in y"""
    x = [(x[i], i) for i in range(len(x))]
    y = [(y[i], i) for i in range(len(y))]
    # First, separate out all the lines based on their types, as we only match between types
    typeMap = {}
    for i in range(len(x)):
        t = type(x[i][0])
        if t in typeMap:
            pass
        xSubset = list(filter(lambda tmp: type(tmp[0]) == t, x))
        ySubset = list(filter(lambda tmp: type(tmp[0]) == t, y))
        typeMap[t] = (xSubset, ySubset)
    for j in range(len(y)):
        t = type(y[j][0])
        if t in typeMap:
            pass
        xSubset = list(filter(lambda tmp: type(tmp[0]) == t, x))
        ySubset = list(filter(lambda tmp: type(tmp[0]) == t, y))
        typeMap[t] = (xSubset, ySubset)

    mapSet = {}
    for t in typeMap:
        # For each type, find the optimal matching
        (xSubset, ySubset) = typeMap[t]
        # First, find exact matches and remove them
        # Give preference to items on the same line- then we won't need to do an edit
        i = 0
        while i < len(xSubset):
            j = 0
            while j < len(ySubset):
                if xSubset[i][1] == ySubset[j][1]:
                    if (
                        compareASTs(xSubset[i][0], ySubset[j][0], checkEquality=True)
                        == 0
                    ):
                        mapSet[ySubset[j][1]] = xSubset[i][1]
                        xSubset.pop(i)
                        ySubset.pop(j)
                        break
                j += 1
            else:
                i += 1
        # Then look for matches anywhere
        i = 0
        while i < len(xSubset):
            j = 0
            while j < len(ySubset):
                if compareASTs(xSubset[i][0], ySubset[j][0], checkEquality=True) == 0:
                    mapSet[ySubset[j][1]] = xSubset[i][1]
                    xSubset.pop(i)
                    ySubset.pop(j)
                    break
                j += 1
            else:
                i += 1  # if we break, don't increment!
        # TODO - check for subsets/supersets in here?
        # Then, look for the 'best we can do' matches
        distanceList = []
        for i in range(len(xSubset)):  # Identify the best matches across all pairs
            st1 = State()
            st1.tree = xSubset[i][0]
            for j in range(len(ySubset)):
                st2 = State()
                st2.tree = ySubset[j][0]
                d, _ = distance(st1, st2)
                d = int(d * 1000)
                distanceList.append((d, xSubset[i][1], ySubset[j][1]))
        # Compare first based on distance, then based on how close the lines are to each other
        distanceList.sort(key=lambda x: (x[0], x[1] - x[2]))
        l = min(len(xSubset), len(ySubset))
        # Now pick the best pairs 'til we run out of them
        while l > 0:
            (d, xLine, yLine) = distanceList[0]
            mapSet[yLine] = xLine
            distanceList = list(
                filter(lambda x: x[1] != xLine and x[2] != yLine, distanceList)
            )
            l -= 1
    # Now, look for matches across different types
    leftoverY = list(filter(lambda tmp: tmp not in mapSet, range(len(y))))
    leftoverX = list(filter(lambda tmp: tmp not in mapSet.values(), range(len(x))))
    # First, look for exact line matches
    i = 0
    while i < len(leftoverX):
        line = leftoverX[i]
        if line in leftoverY:
            mapSet[line] = line
            leftoverX.remove(line)
            leftoverY.remove(line)
        else:
            i += 1
    # Then, just put the rest in place
    for i in range(min(len(leftoverY), len(leftoverX))):  # map together all equal parts
        mapSet[leftoverY[i]] = leftoverX[i]
    if len(leftoverX) > len(leftoverY):  # if X greater, map all leftover x's to -1
        mapSet[-1] = leftoverX[len(leftoverY) :]
    elif len(leftoverY) > len(leftoverX):  # if Y greater, map all leftover y's to -1
        for i in range(len(leftoverX), len(leftoverY)):
            mapSet[leftoverY[i]] = -1
    # if equal, there are none left to map!
    return mapSet


def findKey(d, val):
    for k in d:
        if d[k] == val:
            return k
    return None


def xOffset(line, deletedLines):
    offset = 0
    for l in deletedLines:
        if l <= line:
            offset += 1
    return offset


def yOffset(line, addedLines):
    offset = 0
    for l in addedLines:
        if l <= line:
            offset += 1
    return offset


def findSwap(startList, endList):
    for i in range(len(startList)):
        if startList[i] == endList[i]:
            pass
        for j in range(i + 1, len(startList)):
            if startList[i] == endList[j] and endList[i] == startList[j]:
                return SwapVector([-1], startList[i], startList[j])
    return None


# Recursively generate all moves by working from the outside of the list inwards.
# This should be optimal for lists of up to size four, and once you get to size five, your program is too
# large and I don't care anymore.
def generateMovePairs(startList, endList):
    if len(startList) <= 1:
        return []
    elif startList[0] == endList[0]:
        return generateMovePairs(startList[1:], endList[1:])
    elif startList[-1] == endList[-1]:
        return generateMovePairs(startList[:-1], endList[:-1])
    elif startList[0] == endList[-1] and startList[-1] == endList[0]:
        # swap the two ends
        return [("swap", startList[0], startList[-1])] + generateMovePairs(
            startList[1:-1], endList[1:-1]
        )
    elif startList[0] == endList[-1]:
        # move the smallest element from back to front
        return [("move", startList[0])] + generateMovePairs(startList[1:], endList[:-1])
    elif startList[-1] == endList[0]:
        # move the largest element from front to back
        return [("move", startList[-1])] + generateMovePairs(
            startList[:-1], endList[1:]
        )
    else:
        i = endList.index(startList[0])  # find the position in endList
        return [("move", startList[0])] + generateMovePairs(
            startList[1:], endList[:i] + endList[i + 1 :]
        )


def findMoveVectors(mapSet, x, y, add, delete):
    """We'll find all the moved lines by recreating the mapSet from a tmpSet using actions"""
    startList = list(range(len(x)))
    endList = [mapSet[i] for i in range(len(y))]
    # Remove deletes from startList and adds from endList
    for line in delete:
        startList.remove(line)
    while -1 in endList:
        endList.remove(-1)
    if len(startList) != len(endList):
        log(
            "diffAsts\tfindMovedLines\tUnequal lists: "
            + str(len(startList))
            + ","
            + str(len(endList)),
            "bug",
        )
        return []
    moveActions = []
    if startList != endList:
        movePairs = generateMovePairs(startList, endList)
        for pair in movePairs:
            if pair[0] == "move":
                moveActions.append(MoveVector([-1], pair[1], endList.index(pair[1])))
            elif pair[0] == "swap":
                moveActions.append(SwapVector([-1], pair[1], pair[2]))
            else:
                log("Missing movePair type: " + str(pair[0]), "bug")
    # We need to make sure the indicies start at the appropriate numbers, since they're referring to the original tree
    if len(delete) > 0:
        for action in moveActions:
            if isinstance(action, MoveVector):
                addToCount = 0
                for deleteAction in delete:
                    if deleteAction <= action.newSubtree:
                        addToCount += 1
                action.newSubtree += addToCount
    return moveActions


def diffLists(x, y, ignoreVariables=False):
    mapSet = matchLists(x, y)
    changeVectors = []

    # First, get all the added and deleted lines
    deletedLines = mapSet[-1] if -1 in mapSet else []
    for line in sorted(deletedLines):
        changeVectors.append(DeleteVector([line], x[line], None))

    addedLines = list(filter(lambda tmp: mapSet[tmp] == -1, mapSet.keys()))
    addedOffset = 0  # Because added lines don't start in the list, we need
    # to offset their positions for each new one that's added
    for line in sorted(addedLines):
        changeVectors.append(AddVector([line - addedOffset], None, y[line]))
        addedOffset += 1

    # Now, find all the required moves
    changeVectors += findMoveVectors(mapSet, x, y, addedLines, deletedLines)

    # Finally, for each pair of lines (which have already been moved appropriately,
    # find if they need a normal ChangeVector
    for j in mapSet:
        i = mapSet[j]
        # Not a delete or an add
        if j != -1 and i != -1:
            tempVectors = diffAsts(x[i], y[j], ignoreVariables=ignoreVariables)
            for change in tempVectors:
                change.path.append(i)
            changeVectors += tempVectors
    return changeVectors


def diffAsts(x, y, ignoreVariables=False):
    """Find all change vectors between x and y"""
    xAST = isinstance(x, ast.AST)
    yAST = isinstance(y, ast.AST)
    if xAST and yAST:
        if type(x) != type(y):  # different node types
            if occursIn(x, y):
                return [SubVector([], x, y)]
            elif occursIn(y, x):
                return [SuperVector([], x, y)]
            else:
                return [ChangeVector([], x, y)]
        elif ignoreVariables and type(x) == type(y) == ast.Name:
            if not builtInName(x.id) and not builtInName(y.id):
                return []  # ignore the actual IDs

        result = []
        for field in x._fields:
            currentDiffs = diffAsts(
                getattr(x, field), getattr(y, field), ignoreVariables=ignoreVariables
            )
            if currentDiffs != []:  # add the next step in the path
                for change in currentDiffs:
                    change.path.append((field, astNames[type(x)]))
                result += currentDiffs
        return result
    elif (not xAST) and (not yAST):
        if type(x) == list and type(y) == list:
            return diffLists(x, y, ignoreVariables=ignoreVariables)
        elif x != y or type(x) != type(
            y
        ):  # need the type check to distinguish ints from floats
            return [ReplaceVector([], x, y)]  # they're primitive, so just switch them
        else:  # equal values
            return []
    else:  # Two mismatched types
        return [ChangeVector([], x, y)]


def getChanges(s, t, ignoreVariables=False):
    changes = diffAsts(s, t, ignoreVariables=ignoreVariables)
    for change in changes:
        change.start = s  # WARNING: should maybe have a deepcopy here? It will alias s
    return changes


def distance(s, t, givenChanges=None, forceReweight=False, ignoreVariables=False):
    # """A method for comparing solution states, which returns a number between
    # 	0 (identical solutions) and 1 (completely different)"""
    # # First weigh the trees, to propogate metadata
    # if s == None or t == None:
    # 	return 1 # can't compare to a None state
    # if forceReweight:
    # 	baseWeight = max(getWeight(s.tree), getWeight(t.tree))
    # else:
    # 	if not hasattr(s, "treeWeight"):
    # 		s.treeWeight = getWeight(s.tree)
    # 	if not hasattr(t, "treeWeight"):
    # 		t.treeWeight = getWeight(t.tree)
    # 	baseWeight = max(s.treeWeight, t.treeWeight)

    # if givenChanges != None:
    # 	changes = givenChanges
    # else:
    # 	changes = getChanges(s.tree, t.tree, ignoreVariables=ignoreVariables)

    # changeWeight = getChangesWeight(changes)
    # return (1.0 * changeWeight / baseWeight, changes)
    return 1.0, []
