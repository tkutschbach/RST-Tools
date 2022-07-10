import sys
sys.path.append("RST-Tace")

from rsttace.input.parser import RstTreeParser
from rsttace.core.rsttree import MultiNucRelation

class WordRelationsExtractor():
    """ The WordRelationsExtractor reads a rs3-file by the given path.
        It then generates a list of relations for each of the words in
        the annotated text, based on the given RST-annotations """
    
    def __init__(self, filePath: str):
        self.wordRelationsTable = []
        self.relationsList = []
        self.__extractWordsAndRelations(filePath)
        
    def getWordRelationsTable(self):
        return self.wordRelationsTable
    
    def getRelationsList(self):
        return self.relationsList
        
    def __extractWordsAndRelations(self, filePath: str):
        rstTree = RstTreeParser(filePath).read()
        relationTextPairs = extractRelationsTextPairs(rstTree.root)
        for pair in relationTextPairs:
            relations = pair[0]
            text = pair[1]

            # Add relations to relation list, if not already contained
            for rel in relations:
                if rel not in self.relationsList:
                    self.relationsList.append(rel)

            words = extractWords(text)
            for word in words:
                self.wordRelationsTable.append([word, relations])
                
        self.relationsList.sort()
        return
                
### Internal Helper Functions ##################################################

def extractRelations(rstNode):
    """ For rstNode: Extract relation to the next parent or (larger) sibling """
    hasLargerSibling = (rstNode.toSibling is not None) and (rstNode.toSibling.start is rstNode)
    hasRealParent = isinstance(rstNode.toParent, MultiNucRelation)
    
    if hasLargerSibling:
        return [rstNode.toSibling.relation] + extractRelations(rstNode.toSibling.end)
    elif hasRealParent:
        return [rstNode.toParent.relation] + extractRelations(rstNode.toParent.parent)
    else: # Parent is a Span -> Extract relation from one level above
        if rstNode.toParent is not None:
            return extractRelations(rstNode.toParent.parent)
        else:
            return []

def extractRelationsTextPairs(rstNode):   
    if rstNode is None:
        return []
    else:
        retList = []
        # Generate entry for current node
        if rstNode.text is not None:
            text = rstNode.text
            relations = extractRelations(rstNode)
            retList.append([relations, text])
        
        # Append lists of children (MultiNucRelation and Span)
        if (rstNode.toChildren is not None):
            for child in rstNode.toChildren.children:
                retList = retList + extractRelationsTextPairs(child)
               
        return retList
    
def splitIntoTokens(text):
    from nltk.tokenize import word_tokenize
    return word_tokenize(text)

def removePunctuation(tokens):
    return [w for w in tokens if w.isalpha()]

def convertToLowerCase(words):
    return [w.lower() for w in words]

def removeStopWords(words):
    from nltk.corpus import stopwords
    stopWords = set(stopwords.words('german'))
    return [w for w in words if not w in stopWords]

def extractWords(text):
    tokens = splitIntoTokens(text)
    words = removePunctuation(tokens)
    #words = convertToLowerCase(words)
    #words = removeStopWords(words)
    return words
