#!/usr/bin/env python3
import sys
import os
from ASTDiff import ASTDiff
oldFileName = sys.argv[1]
newFileName = sys.argv[2]
os.system("gumtree parse " + oldFileName + " > ASTbefore.txt")
os.system("gumtree parse " + newFileName + " > ASTafter.txt")
os.system("gumtree diff " + oldFileName + " " + newFileName + " > diffscipt.txt")

astDiff = ASTDiff()
# print(astDiff.getDiffTreeNode())
astDiff.outputPrueInsertNode()