import re


class DiffOperate():
    def __init__(self, file):
        self.updateList = []
        self.matchList = []
        self.insertList = []
        self.moveList = []
        self.deleteList = []

        with open(file, 'r') as f:
            for line in f.readlines():
                if line.startswith("Match"):
                    # print(line)
                    matchObj = re.findall(r'(?<=\()\d+(?=\))', line)
                    # print(matchObj)
                    matchTuple = (int(matchObj[0]), int(matchObj[1]))
                    self.matchList.append(matchTuple)
                elif line.startswith("Insert"):
                    matchObj = re.findall(r'(?<=\()\d+(?=\))', line)
                    t = int(re.findall(r'\d+', line)[-1])
                    insertTuple = (int(matchObj[0]), int(matchObj[1]),t)
                    self.insertList.append(insertTuple)
                elif line.startswith("Move"):
                    matchObj = re.findall(r'(?<=\()\d+(?=\))', line)
                    t = int(re.findall(r'\d+', line)[-1])
                    MoveTuple = (int(matchObj[0]), int(matchObj[1]),t)
                    self.moveList.append(MoveTuple)
                elif line.startswith("Delete"):
                    matchObj = re.findall(r'(?<=\()\d+(?=\))', line)
                    self.deleteList.append(int(matchObj[0]))
                elif line.startswith("Update"):
                    matchObj = re.findall(r'(?<=\()\d+(?=\))', line)
                    self.updateList.append(int(matchObj[0]))
                    # print("update", matchObj[0])

        # print(self.matchList)
        # print(self.insertList)
        # print(self.moveList)
        # print(self.deleteList)

    def getMatchedAfterID(self, beforeID):
        '''

        :param beforeID: AfterAST树中的ID
        :return: BeforeAST树中的ID，不存在则返回-1
        '''
        for i in self.matchList:
            if i[0] == beforeID:
                return i[1]
        else:
            return -1

    def getMatchedBeforeID(self, afterID):
        for i in self.matchList:
            if i[1] == afterID:
                return i[0]
        else:
            return -1

    def getInsertedIDs(self):
        '''
        返回After树被插入子节点的节点的ID
        '''
        tempList = []
        for i in self.insertList:
            tempList.append(i[1])
        return tempList

    def getJoinedIDs(self):
        '''
        返回加入After树的节点的ID
        '''
        tempList = []
        for i in self.insertList:
            tempList.append(i[0])
        return tempList


    def getMovedAfterIDsAndIndex(self):
        '''
        返回被移动之后的节点在After树中的ID
        '''
        tempList = []
        for i in self.moveList:
            tempList.append((i[1],i[2]))
        return tempList

    def getMovedBeforeIDs(self):
        '''
        返回被移动之前的节点在Before树中的ID
        '''
        tempList = []
        for i in self.moveList:
            tempList.append(i[0])
        return tempList

    def getDeleteBeforeIDs(self):
        '''
        返回被删除的节点在After树中的ID
        '''
        return self.deleteList

    def getUpdateBeforeIDs(self):
        return self.updateList

    def isJoinNode(self, id):
        '''
        判断是否是新加入的节点
        '''
        return (id in self.getJoinedIDs())


if __name__ == "__main__":
    d = DiffOperate("diffscript.txt")
