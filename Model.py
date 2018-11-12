class ASTNode(object):
    def __init__(self, temp, children):
        self.type = int(temp["type"])
        self.label = temp.get("label")
        self.typeLabel = temp["typeLabel"]
        self.pos = int(temp["pos"])
        self.length = int(temp["length"])
        self.children = children
        self.id = temp["id"]
        self.parent = None

