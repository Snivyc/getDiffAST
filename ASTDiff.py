from AST import AST
from diffOperate import DiffOperate
import copy

class ASTDiff(object):

    def __init__(self, oldfile, newfile):
        self.astBefore = AST("ASTbefore.json", oldfile)
        self.astAfter = AST("ASTafter.json", newfile)
        self.diff = DiffOperate("diffscript.txt")
        self.structureHandle = {
            "IfStatement": "if语句",
            "ForStatement": "for循环",
            "DoStatement": "do-while循环语句",
            "ReturnStatement": "return语句",
            "TryStatement": "try语句",
            "ThrowStatement": "抛出异常语句",
            "SwitchStatement": "Switch语句",
            "SingleVariableDeclaration": "方法的参数列表，单形参的变量声明???（没懂）",
            "ImportDeclaration": "import包",
            "ExpressionStatement": "表达式语句",
            "WhileStatement": "while语句",
            "MethodInvocation": "函数调用",
            "MethodDeclaration": "函数定义"
        }
        self.defectClassDict = {
            # ("IfStatement", 0): "1.1 if.条件",
            # ("IfStatement", 1): "1.2 if.主体",
            # ("IfStatement", 2): "1.3 if.else体",
            # ("ExpressionStatement", 0): "4 表达式语句",
            # ("WhileStatement", 0): "2.1 while.条件",
            # ("WhileStatement", 1): "2.2 while.主体",
            # ("ReturnStatement", 0): "3 return语句",
            # ("ImportDeclaration", 0): "7 import语句",
            # ("ForStatement", 0): "8.1 for.初始条件",
            # ("ForStatement", 1): "8.2 for.循环条件",
            # ("ForStatement", 2): "8.3 for.结束执行的语句",
            # ("ForStatement", 3): "8.4 for.主体",
            # ("SingleVariableDeclaration", 0): "形参.类型",
            # ("SingleVariableDeclaration", 1): "形参.名称",
            ("IfStatement", 0): "1.1",
            ("IfStatement", 1): "1.2",
            ("IfStatement", 2): "1.3",
            ("ExpressionStatement", 0): "4",
            ("WhileStatement", 0): "2.1",
            ("WhileStatement", 1): "2.2",
            ("ReturnStatement", 0): "3",
            ("ImportDeclaration", 0): "7",
            ("ForStatement", 0): "8.1",
            ("ForStatement", 1): "8.2 ",
            ("ForStatement", 2): "8.3",
            ("ForStatement", 3): "8.4",
            # ("SingleVariableDeclaration", 0): "形参.类型",
            # ("SingleVariableDeclaration", 1): "形参.名称",
        }

    def getBlockName(self, changedType, index, nodeID, ast):
        '''
        输入语句块，和修改的子节点的下标，返回修改的类型
        '''
        if (changedType, index) in self.defectClassDict:
            return self.defectClassDict[(changedType, index)]
        # if changedType == "MethodInvocation":
        #     return "函数调用语句"
        if changedType == "SuperMethodInvocation":
            # return "调用父类方法"
            return
        if changedType == "MethodDeclaration":
            typeLabel = ast.getNodeByID(nodeID).children[index].typeLabel
            if typeLabel == "SimpleName":
                # return "6.1 函数定义.函数名称"
                return "6.1"
            elif typeLabel == "PrimitiveType":
                # return "6.3 函数定义.返回值类型"
                return "6.3"
            elif typeLabel == "Modifier":
                # return "6.4 函数定义.修饰词节点"
                return "6.4"
            elif typeLabel == "SingleVariableDeclaration":
                # return "6.2 函数定义.参数"
                return "6.2"
            else:
                # return "路过..打扰了.."
                return
        if changedType == "MethodInvocation":
            # print(nodeID)
            node = ast.getNodeByID(nodeID)
            block = None
            # print(node.typeLabel)
            # print("***************************************")
            # print(node.pos, node.pos+node.length)
            # print(ast.CODE[node.pos: node.pos+node.length])
            for i in range(len(node.children)-1):
                start = node.children[i].pos + node.children[i].length
                end = node.children[i + 1].pos
                # print(start, end)
                # print(ast.CODE[start : end])
                if "(" in ast.CODE[start:end]:
                    block = i
                    break
            else:
                # return "5.1 函数调用.方法名"
                return "5.1"
            if index <= block:
                # return "5.1 函数调用.方法名"
                return "5.1"
            else:
                # return "5.2 函数调用.参数"
                return "5.2"

        # return "（未定义）"
        return

    def getDiffTreeNode(self):
        '''
            寻找最小的包含所有修改的子树，返回这棵树的头节点
        '''
        changedNodeID = set() #子节点变化的Node的ID，before树中
        changedNodeID = changedNodeID | set(self.diff.getDeleteBeforeIDs())
        tempSet = set()
        for i in self.diff.getInsertedIDs():
            if self.diff.getMatchedBeforeID(i) != -1:
                tempSet.add(self.diff.getMatchedBeforeID(i))
        changedNodeID = changedNodeID | tempSet
        changedNodeID = changedNodeID | {self.astBefore.ASTNodeList[i].parent.id for i in self.diff.getMovedBeforeIDs()}
        tempSet = set()
        for i in self.diff.getMovedAfterIDs():
            if self.diff.getMatchedBeforeID(i) != -1:
                tempSet.add(self.diff.getMatchedBeforeID(i))
        changedNodeID = changedNodeID | tempSet
        changedNodeID = list(changedNodeID)
        def getCommonParent(changedNodeID):
            while (len(changedNodeID) > 1):
                a = self.astBefore.ASTNodeList[changedNodeID.pop()]
                b = self.astBefore.ASTNodeList[changedNodeID.pop()]
                c = a
                print(changedNodeID)
                while(b != None):
                    a = c
                    while(a != None):
                        print(a.id, b.id)
                        if a is b:
                            changedNodeID.append(a.id)
                            return getCommonParent(changedNodeID)
                        b = b.parent
                    a = a.parent
                    print(a)
            else:
                return changedNodeID
        commonParentID = getCommonParent(changedNodeID)[0]
        # print(self.astBefore.astToJson(commonParentID))
        return commonParentID

    def getPrueInsertNode(self):
        '''
        如果一个节点，其自身及所有的孩子都是新增的（被插入，移动），其父节点不是新增的，则返回
        '''
        joinedNodeIDs = self.diff.getJoinedIDs() + self.diff.getMovedAfterIDs()

        # def isPrue(i):
        #     if self.diff.getMatchedBeforeID(i) == -1:
        #         return -1
        #     childrenList = self.astAfter.getNodeByID(i).children
        #     if childrenList != []:
        #         return -2
        #     for j in childrenList:
        #         result = isPrue(j.id)
        #         if result == -1:
        #             return -1
        #         else:
        #             return 1
        #
        mergeList = []

        for i in joinedNodeIDs:
            if self.diff.isJoinNode(self.astAfter.getNodeByID(i).parent.id):
                continue
            mergeList.append(i)
            # if self.astAfter.getNodeByID(i).children == []:
            #     continue
            # if isPrue(i):
            #     returnList.append(i)
        return self.searchUpHandleNode(mergeList,self.astAfter)

    def getPrueDeleteNode(self):
        deletedNodeIDs = self.diff.getDeleteBeforeIDs() + self.diff.getMovedBeforeIDs()
        mergeList = []

        for i in deletedNodeIDs:
            if self.astBefore.getNodeByID(i).parent.id in deletedNodeIDs:
                continue
            mergeList.append(i)
        return self.searchUpHandleNode(mergeList,self.astBefore)

    def outputChangedNode(self):
        allOutPut = set()
        # print("新加入的节点:")
        IDsList = self.getPrueInsertNode()
        for t in IDsList:
            typeLabel = self.astAfter.getNodeByID(t[0]).typeLabel
            # print(self.getBlockName(typeLabel, t[1], t[0], self.astAfter))
            allOutPut.add(self.getBlockName(typeLabel, t[1], t[0], self.astAfter))
        # print('-------------------------------------------------------------------------------------------------------')

        # print("删除的节点:")
        IDsList = self.getPrueDeleteNode()
        for t in IDsList:
            typeLabel = self.astBefore.getNodeByID(t[0]).typeLabel
            # print(self.getBlockName(typeLabel, t[1], t[0], self.astBefore))
            allOutPut.add(self.getBlockName(typeLabel, t[1], t[0], self.astBefore))
        # print('-------------------------------------------------------------------------------------------------------')

        # print("修改的语句块：")
        for t in self.findUpdateBlockNode():
            typeLabel = self.astBefore.getNodeByID(t[0]).typeLabel
            # print(t)
            # if (typeLabel, t[1]) in self.defectClassDict:
            # print(self.getBlockName(typeLabel, t[1], t[0], self.astBefore))
            allOutPut.add(self.getBlockName(typeLabel, t[1], t[0], self.astBefore))
            # else:
            #     print(typeLabel, "（未定义）")
            # print(self.astBefore.getNodeByID(ID).typeLabel, self.structureHandle[self.astBefore.getNodeByID(ID).typeLabel])
        # print('-------------------------------------------------------------------------------------------------------')
        # allOutPut = [i for i in allOutPut if i != None]
        # allOutPut.sort()
        print("1111111111",allOutPut)
        return allOutPut

    def findUpdateBlockNode(self):
        '''
        寻找所有changed所在的节点更新的语句块
        '''
        updateList = self.diff.getUpdateBeforeIDs()
        mergeList = []
        for i in updateList:
            if self.astBefore.getNodeByID(i).parent.id in updateList:
                continue
            mergeList.append(i)
        # print(mergeList)
        return self.searchUpHandleNode(mergeList, self.astBefore)


    def searchUpHandleNode(self, mergeList, AST):
        '''
        在ASTBeftore中向上搜索
        '''
        structureNode = set()
        for i in mergeList:
            tempNode = AST.getNodeByID(i)
            index = self.getIndexInParent(tempNode.id, AST)
            tempNodeO = tempNode
            tempNode = tempNode.parent
            while True:
                if tempNode == None:
                    break
                elif tempNode.typeLabel == "MethodDeclaration":
                    # print(tempNodeO.id)
                    structureNode.add((tempNode.id, index))
                    break
                # print(tempNode.typeLabel,"----------")
                elif tempNode.typeLabel in self.structureHandle:
                    # print(tempNodeO.id)
                    structureNode.add((tempNode.id, index))
                    # print(tempNode.typeLabel, '123123123123123')
                # print(index)
                index = self.getIndexInParent(tempNode.id, AST)
                tempNode = tempNode.parent

        # print(structureNode)
        return structureNode


    def getIndexInParent(self, ID, ast):
        '''
        获取改节点在父节点中的下标，！！！！！！！需移动到AST类中！！！！！！！！！
        '''
        parent = ast.getNodeByID(ID).parent
        if parent != None:
            for i in range(len(parent.children)):
                if parent.children[i].id == ID:
                    return i
        else:
            return 0



if __name__ == "__main__":
    astDiff = ASTDiff()
    # print(astDiff.getDiffTreeNode())
    astDiff.outputChangedNode()
    # print(astDiff.findUpdateBlockNode())