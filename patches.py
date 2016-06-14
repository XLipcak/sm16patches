from struct import pack

from urlparse import urlparse

import re
from rdflib import Graph, plugin, URIRef, Literal, BNode
from rdflib.namespace import RDF

import datetime
import json
import ast
import os

class PatchRequestPersistence:

    # store into file for now, consider DB or remote API later
    def __init__(self, dataSource):

        # datasource specify data directory now
        self.directory = dataSource

    def save(self, patchRequestJson):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        patchRequest = PatchRequest(patchRequestJson, self.getIdentifier(), True)

        print('Saving patch request with id: ' + patchRequest.identifier)
        patchRequest.graph.serialize(self.directory + "/" + 'Patch_' + patchRequest.identifier + ".ttl", format='turtle')

    def load(self):
        print('Loading patch requests...')
        patchRequests = []

        for filename in os.listdir(self.directory):
            print('Reading from file: ' + filename)
            g = Graph()
            g.parse(self.directory + "/" + filename, format="nt")
            patchRequests.append(PatchRequest(g, filename[6:][:-3], False))

        return patchRequests

    def getIdentifier(self):
        max = 0
        for filename in os.listdir(self.directory):
            ## gotta find a way to prevent my Mac from generating these
            ## sorry guys
            if filename == ".DS_Store":
                continue
            idRegex = re.compile("(\d+)")
            match = idRegex.search(filename)
            actualId = match.group()
            if max < int(actualId):
                max = int(actualId)
        return str(max + 1)



class PatchRequest():
    def __init__(self, patchRequest, identifier, isFromJson):
        self.identifier = identifier
        if not isFromJson:
            self.graph = patchRequest
        else:
            # Build graph representation of Patch request from JSON

            # Find subject
            subject = patchRequest["url"]

            self.graph = Graph()

            # First layer
            self.graph.add((BNode(self.identifier.encode("utf-8")), RDF.type,
                            URIRef("http://purl.org/hpi/patchr#Patch".encode("utf-8"))))
            self.graph.add((BNode(self.identifier.encode("utf-8")),
                            URIRef("http://purl.org/hpi/patchr#appliesTo".encode("utf-8")),
                            URIRef(subject.encode("utf-8"))))
            self.graph.add((BNode(self.identifier.encode("utf-8")),
                            URIRef("http://purl.org/hpi/patchr#status".encode("utf-8")),
                            URIRef("http://purl.org/hpi/patchr#Open".encode("utf-8"))))

            # Update instruction layer
            self.graph.add((BNode(self.identifier.encode("utf-8")),
                            URIRef("http://purl.org/hpi/patchr#update".encode("utf-8")),
                            BNode("updateInstruction".encode("utf-8"))))
            self.graph.add((BNode("updateInstruction".encode("utf-8")), RDF.type,
                            URIRef("http://webr3.org/owl/guo#UpdateInstruction".encode("utf-8"))))
            self.graph.add((BNode("updateInstruction".encode("utf-8")),
                            URIRef("http://webr3.org/owl/guo#target_graph".encode("utf-8")),
                            URIRef(self.parseUrl(subject).encode("utf-8"))))
            self.graph.add((BNode("updateInstruction".encode("utf-8")),
                            URIRef("http://webr3.org/owl/guo#target_subject".encode("utf-8")),
                            URIRef(subject.encode("utf-8"))))

            # Delete and insert instructions layer
            self.graph.add((BNode("updateInstruction".encode("utf-8")),
                            URIRef("http://webr3.org/owl/guo#delete".encode("utf-8")),
                            BNode("deleteInstruction".encode("utf-8"))))
            self.graph.add((BNode("updateInstruction".encode("utf-8")),
                            URIRef("http://webr3.org/owl/guo#insert".encode("utf-8")),
                            BNode("insertInstruction".encode("utf-8"))))

            for patch in patchRequest.get('addedData'):
                objectType = patch.get('object').get('type')
                if(objectType == 'literal' or objectType == 'text'):
                    self.graph.add((BNode("insertInstruction"),URIRef(patch.get('predicate').encode("utf-8")),Literal(patch.get('object').get('value').encode("utf-8"))))
                else:
                    self.graph.add((BNode("insertInstruction"),URIRef(patch.get('predicate').encode("utf-8")),URIRef(patch.get('object').get('value').encode("utf-8"))))

            for patch in patchRequest.get('updatedData'):
                objectType = patch.get('object').get('type')
                if (objectType == 'literal' or objectType == 'text'):
                    self.graph.add((BNode("insertInstruction"), URIRef(patch.get('predicate').encode("utf-8")),
                                    Literal(patch.get('object').get('value').encode("utf-8"))))
                else:
                    self.graph.add((BNode("insertInstruction"), URIRef(patch.get('predicate').encode("utf-8")),
                                    URIRef(patch.get('object').get('value').encode("utf-8"))))

            for patch in patchRequest.get('deletedData'):
                objectType = patch.get('object').get('type')
                if (objectType == 'literal' or objectType == 'text'):
                    self.graph.add((BNode("deleteInstruction"), URIRef(patch.get('predicate').encode("utf-8")),
                                    Literal(patch.get('object').get('value').encode("utf-8"))))
                else:
                    self.graph.add((BNode("deleteInstruction"), URIRef(patch.get('predicate').encode("utf-8")),
                                    URIRef(patch.get('object').get('value').encode("utf-8"))))

            # Was generated by layer
            self.graph.add((BNode(self.identifier.encode("utf-8")),
                            URIRef("http://purl.org/net/provenance/ns#wasGeneratedBy".encode("utf-8")),
                            BNode("generatedBy".encode("utf-8"))))
            self.graph.add((BNode("generatedBy".encode("utf-8")), RDF.type,
                            URIRef("http://purl.org/net/provenance/ns#Activity".encode("utf-8"))))
            self.graph.add((BNode("generatedBy".encode("utf-8")),
                            URIRef("http://purl.org/net/provenance/ns#performedAt".encode("utf-8")),
                            Literal(str(datetime.datetime.now()))))

    def parseUrl(self, url):
        try:
            parsedUrl = urlparse(url)
        except:
            print('URL not parsed!')
            return url
        return parsedUrl.scheme + '://' + parsedUrl.netloc + '/'

    def __str__(self):
        return self.graph.serialize(format="nt")
