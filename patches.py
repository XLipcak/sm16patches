from urlparse import urlparse
from rdflib import Graph, plugin, URIRef, Literal, BNode
from rdflib.namespace import RDF

import datetime
import json
import ast

class PatchRequestPersistence:

    # store into file for now, consider DB or remote API later
    def __init__(self, dataSource):

        # datasource specify data directory now
        self.directory = dataSource

        # PatchRequest only for testing purposes store it and load all data
        # - to be deleted
        patchRequestTest = PatchRequest([
            {
                "instruction": "DELETE",
                "subject": "http://dbpedia.org/page/Albert_Einstein",
                "predicate": "http://xmls.com/foaf/0.1/accountName",
                "value": {
                    "type": "literal",
                    "value": "123120194"
                }
            },
            {
                "instruction": "ADD",
                "subject": "http://dbpedia.org/page/Albert_Einstein",
                "predicate": "http://xmls.com/foaf/0.1/accountName",
                "value": {
                    "type": "literal",
                    "value": "123120194"
                }
            }], True)

        self.save(patchRequestTest)
        self.load()

    def save(self, patchRequest):
        print('Saving patch request.')

        #with open(self.dataSource, 'a') as f:
         #   result = {}
         #   patchNum = 0
         #   for x in patchRequest.patchList:
         #       patchNum += 1
         #       result[str(patchNum)] = (patchRequest.patchList.get(patchNum).patchInstruction)

#            json.dump(result, f)
 #           f.write('\n')

    def load(self):
        print('Loading patch requests...')
        patchRequests = {}
        with open(self.directory, 'r') as f:
            try:
                patchNum = 0
                for line in f:
                    patchNum += 1
                    data = ast.literal_eval(line)
                    patchRequests[str(patchNum)] = data
            # if the file is empty the ValueError will be thrown
            except ValueError:
                print('Load ERROR')
                data = {}

        print('Loaded data: ')
        print(patchRequests)
        return patchRequests




class PatchRequest():
    ##TODO: rebuild this method according to correct processing of patches and graphs and received JSON
    def __init__(self, patchRequestJson, isFromJson):
        if not isFromJson:
            self.patchInstruction = patch
        else:

            identifier = 'Patch_1'
            self.graph = Graph()
            self.graph.add((BNode(identifier.encode("utf-8")), RDF.type, URIRef("http://purl.org/hpi/patchr#Patch".encode("utf-8")))) #top layer
            self.graph.add((URIRef("http://purl.org/hpi/patchr#Patch".encode("utf-8")),URIRef("http://purl.org/hpi/patchr#status".encode("utf-8")),URIRef("http://purl.org/hpi/patchr#Open".encode("utf-8")))) # just stick with open
            self.graph.add((URIRef("http://purl.org/hpi/patchr#Patch".encode("utf-8")),URIRef("http://purl.org/hpi/patchr#update".encode("utf-8")),BNode("updateInstruction".encode("utf-8"))))
            self.graph.add((BNode("updateInstruction".encode("utf-8")),RDF.type,URIRef("http://webr3.org/owl/guo#UpdateInstruction".encode("utf-8"))))
            self.graph.add((BNode("updateInstruction".encode("utf-8")),URIRef("http://webr3.org/owl/guo#delete".encode("utf-8")),BNode("deleteInstruction".encode("utf-8"))))
            self.graph.add((BNode("updateInstruction".encode("utf-8")),URIRef("http://webr3.org/owl/guo#insert".encode("utf-8")),BNode("insertInstruction".encode("utf-8"))))
            self.graph.add((URIRef("http://purl.org/hpi/patchr#Patch".encode("utf-8")),
                            URIRef("http://purl.org/hpi/patchr#appliesTo".encode("utf-8")),
                            Literal(self.parseUrl(
                                patchRequestJson[0].get('subject')).encode(
                                "utf-8"))))
            self.graph.add((BNode("updateInstruction".encode("utf-8")),
                            URIRef("http://webr3.org/owl/guo#target_graph".encode("utf-8")),
                            Literal(self.parseUrl(
                                patchRequestJson[0].get('subject')).encode("utf-8"))))
            self.graph.add((BNode("updateInstruction".encode("utf-8")),
                            URIRef("http://webr3.org/owl/guo#target_subject".encode("utf-8")),
                            URIRef(patchRequestJson[0].get('subject').encode("utf-8"))))

            #check json for update instruction
            
            for patch in patchRequestJson:
                actualPatchInstructionString = patch.get('instruction')

                objectType = patch.get('value').get('type')
                if(actualPatchInstructionString == 'DELETE'):
                    if(objectType == 'Literal'):
                        self.graph.add((BNode("deleteInstruction"),URIRef(patch.get('predicate').encode("utf-8")),Literal(patch.get('value').get('value').encode("utf-8"))))
                    else:
                        self.graph.add((BNode("deleteInstruction"),URIRef(patch.get('predicate').encode("utf-8")),URIRef(patch.get('value').get('value').encode("utf-8"))))
                if(actualPatchInstructionString == 'ADD'):
                    if(objectType == 'Literal'):
                        self.graph.add((BNode("insertInstruction"),URIRef(patch.get('predicate').encode("utf-8")),Literal(patch.get('value').get('value').encode("utf-8"))))
                    else:
                        self.graph.add((BNode("insertInstruction"),URIRef(patch.get('predicate').encode("utf-8")),URIRef(patch.get('value').get('value').encode("utf-8"))))

            self.graph.add((URIRef("http://purl.org/hpi/patchr#Patch".encode("utf-8")),URIRef("http://purl.org/net/provenance/ns#wasGeneratedBy".encode("utf-8")),BNode("generatedBy".encode("utf-8"))))
            self.graph.add((BNode("generatedBy".encode("utf-8")),RDF.type,URIRef("http://purl.org/net/provenance/ns#Activity".encode("utf-8"))))
            #add missing provenance
            timestamp = str(datetime.datetime.now())
            self.graph.add((BNode("generatedBy".encode("utf-8")),URIRef("http://purl.org/net/provenance/ns#performedAt".encode("utf-8")),Literal(timestamp)))


            print(self.graph.serialize(format="nt"))


    def parseUrl(self, url):
        parsedUrl = urlparse(url)
        return parsedUrl.scheme + '://' + parsedUrl.netloc + '/'

    def __str__(self):
        return str(self.patchInstruction)
