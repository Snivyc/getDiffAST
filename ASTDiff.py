from AST import AST
from diffOperate import DiffOperate
import copy

class ASTDiff(object):

    def __init__(self):
        self.astBefore = AST("ASTbefore.json")
        self.astAfter = AST("ASTafter.json")
        self.diff = DiffOperate("diffscript.txt")
        self.structureHandle = {"IfStatement":"if语句",
                                "ForStatement":"for循环",
                                "DoStatement":"do-while循环语句",
                                "ReturnStatement":"return语句",
                                "TryStatement":"try语句",
                                "ThrowStatement":"抛出异常语句",
                                "SwitchStatement":"Switch语句",
                                "SingleVariableDeclaration":"方法的参数列表，单形参的变量声明???（没懂）",
                                "ImportDeclaration":"import包",
                                "ExpressionStatement":"表达式语句",
                                "WhileStatement":"while语句",
                                "MethodInvocation":"函数调用",
                                }
        self.defectClassDict = {
            ("IfStatement",0):"if条件",
            ("IfStatement",1):"if主体",
            ("IfStatement",2):"ifelse体",
            ("ExpressionStatement",0):"表达式语句",
            ("WhileStatement",0):"while条件",
            ("WhileStatement",1):"while主体",
            ("ReturnStatement",0):"return语句",
            ("ImportDeclaration",0):"import语句",
            ("ForStatement", 0): "for初始条件",
            ("ForStatement", 1): "for循环条件",
            ("ForStatement", 2): "for结束执行的语句",
            ("ForStatement", 3): "for主体",
            ("SingleVariableDeclaration", 0): "形参类型",
            ("SingleVariableDeclaration", 1): "形参名称",
        }

    def getBlockName(self, changedType, index, nodeID):
        '''
        输入语句块，和修改的子节点的下标，返回修改的类型
        '''
        if (changedType, index) in self.defectClassDict:
            return self.defectClassDict[(changedType, index)]
        if changedType == "MethodInvocation":
            return "函数调用语句"
        if changedType == "MethodDeclaration":
            typeLabel = self.astBefore.getNodeByID(nodeID).children[index].typeLabel
            if typeLabel == "SimpleName":
                return "函数定义.函数名称"
            elif typeLabel == "PrimitiveType":
                return "函数定义.返回值类型"
            elif typeLabel == "Modifier":
                return "修饰词节点"
            else:
                return "路过..."
        return "（未定义）"


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
        joinedNodeIDs = self.diff.getJoinedIDs()

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
        returnList = []

        for i in joinedNodeIDs:
            if self.diff.isJoinNode(self.astAfter.getNodeByID(i).parent.id):
                continue
            returnList.append(i)
            # if self.astAfter.getNodeByID(i).children == []:
            #     continue
            # if isPrue(i):
            #     returnList.append(i)
        return returnList

    def getPrueDeleteNode(self):
        deletedNodeIDs = self.diff.getDeleteBeforeIDs()
        returnList = []

        for i in deletedNodeIDs:
            if self.astBefore.getNodeByID(i).parent.id in deletedNodeIDs:
                continue
            returnList.append(i)
        return returnList

    def outputPrueInsertNode(self):
        print("新加入的节点:")
        IDsList = self.getPrueInsertNode()
        for ID in IDsList:
            print(self.astAfter.getNodeByID(ID).typeLabel)
        print('-------------------------------------------------------------------------------------------------------')

        print("删除的节点:")
        IDsList = self.getPrueDeleteNode()
        for ID in IDsList:
            print(self.astBefore.getNodeByID(ID).typeLabel)
        print('-------------------------------------------------------------------------------------------------------')

        print("修改的语句块：")
        for t in self.findUpdateBlockNode():
            typeLabel = self.astBefore.getNodeByID(t[0]).typeLabel
            print(t)
            # if (typeLabel, t[1]) in self.defectClassDict:
            print(self.getBlockName(typeLabel, t[1], t[0]))
            # else:
            #     print(typeLabel, "（未定义）")
            # print(self.astBefore.getNodeByID(ID).typeLabel, self.structureHandle[self.astBefore.getNodeByID(ID).typeLabel])
        print('-------------------------------------------------------------------------------------------------------')


    def findUpdateBlockNode(self):
        updateList = self.diff.getUpdateBeforeIDs()
        mergeList = []
        for i in updateList:
            if self.astBefore.getNodeByID(i).parent.id in updateList:
                continue
            mergeList.append(i)
        structureNode = set()
        for i in mergeList:
            tempNode = self.astBefore.getNodeByID(i)
            index = None
            while True:
                # print(tempNode.typeLabel,"----------")
                if tempNode.typeLabel in self.structureHandle:

                    structureNode.add((tempNode.id, index))
                    # print(tempNode.typeLabel, '123123123123123')
                index = self.getIndexInParent(tempNode.id, self.astBefore)
                tempNode = tempNode.parent
                if tempNode.typeLabel == "MethodDeclaration" or None:
                    break
        return structureNode

    def getIndexInParent(self, ID, ast):
        '''
        获取改节点在父节点中的下标，！！！！！！！需移动到AST类中！！！！！！！！！
        '''
        parent = ast.getNodeByID(ID).parent
        for i in range(len(parent.children)):
            if parent.children[i].id == ID:
                return i








if __name__ == "__main__":
    astDiff = ASTDiff()
    # print(astDiff.getDiffTreeNode())
    astDiff.outputPrueInsertNode()
    # print(astDiff.findUpdateBlockNode())