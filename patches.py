from struct import pack

from urlparse import urlparse
import time
import re
from rdflib import Graph, plugin, URIRef, Literal, BNode
from rdflib.namespace import RDF

import datetime
import json
import ast
import os
import time

class PatchRequestPersistence:

    # dataSource - folder location
    def __init__(self, dataSource):
        self.directory = dataSource

    def save(self, changeRequestJson):
        resourceUrl = changeRequestJson["resourceUrl"]
        resourceId = self.getResourceId(resourceUrl)
        patchRequestId = int(round(time.time() * 1000))

        self.createResourceFolderStructure(resourceId)
        print('Saving patch request with id: ' + str(patchRequestId))

        # generate list of JSON dictionaries which will be written into different files
        generatedPatches = self.generatePatchRequestJsonGroupedByURI(changeRequestJson)

        # Resource is subject
        for subjectId, value in generatedPatches[0].iteritems():
            self.createResourceFolderStructure(self.getResourceId(subjectId))
            with open(self.getSubjectPath(subjectId) + "/" + 'Patch_' + str(patchRequestId) + ".json",
                      'w') as outfile:
                value['resourceUrl'] = subjectId
                value['timestamp'] = time.strftime("%c")
                json.dump(value, outfile)

        # Resource is object
        for objectId, value in generatedPatches[1].iteritems():
            self.createResourceFolderStructure(self.getResourceId(objectId))
            with open(self.getObjectPath(objectId) + "/" + 'Patch_' + str(patchRequestId) + ".json",
                      'w') as outfile:
                value['timestamp'] = time.strftime("%c")
                json.dump(value, outfile)


    def load(self, patchRequestUrl):
        print('Loading patch requests for URL: ' + patchRequestUrl)

        patchRequests = {}

        # patchRequestUrl not specified => LOAD all patch requests (always only from as_subject dir)
        if patchRequestUrl == '':
            for root, dirs, files in os.walk(self.directory):
                if "as_object" not in root:
                    for file in files:
                        print('Reading from file: ' + file)
                        with open(os.path.join(root, file), "r") as data_file:
                            data = json.load(data_file)
                            id = data['resourceUrl']
                            time = data['timestamp']
                            if id not in patchRequests:
                                patchRequests[str(id)] = {}
                            if time not in patchRequests[str(id)]:
                                patchRequests[str(id)][time] = {}
                                patchRequests[str(id)][time] = {}
                                patchRequests[str(id)][time]['deletedData'] = []
                                patchRequests[str(id)][time]['addedData'] = []

                            patchRequests[str(id)][time]['deletedData'].append(data['deletedData'])
                            patchRequests[str(id)][time]['addedData'].append(data['addedData'])

            return patchRequests

        # patchRequestUrl specified => LOAD all patch requests where it appears as subject
        path = self.getSubjectPath(patchRequestUrl)
        try:
            for filename in os.listdir(path):
                print('Reading from file: ' + filename)

                with open(path + '/' + filename) as data_file:
                    data = json.load(data_file)
                    id = data['resourceUrl']
                    time = data['timestamp']
                    if id not in patchRequests:
                        patchRequests[str(id)] = {}
                    if time not in patchRequests[str(id)]:
                        patchRequests[str(id)][time] = {}
                        patchRequests[str(id)][time] = {}
                        patchRequests[str(id)][time]['deletedData'] = []
                        patchRequests[str(id)][time]['addedData'] = []

                    patchRequests[str(id)][time]['deletedData'].append(data['deletedData'])
                    patchRequests[str(id)][time]['addedData'].append(data['addedData'])
        except OSError:
            pass

        return patchRequests

    def loadPatchesForTriple(self, subject, predicate, object):
        patchRequests = self.load(subject)

        resultPatchRequests = {}
        resultPatchRequests['addedData'] = []
        resultPatchRequests['deletedData'] = []
        if subject in patchRequests:
            for subject, subjectDict in patchRequests.iteritems():
                for timestamp, patches in subjectDict.iteritems():
                    for addedPatches in patches['addedData']:
                        for patch in addedPatches:
                            if 'predicate' in patch and patch['predicate'] == predicate:
                                patch['timestamp'] = timestamp
                                resultPatchRequests['addedData'].append(patch)

                    for deletedPatches in patches['deletedData']:
                        for patch in deletedPatches:
                            if 'predicate' in patch and patch['predicate'] == predicate and patch['object'] == object:
                                resultPatchRequests['deletedData'].append(timestamp)

        return resultPatchRequests

    def generatePatchRequestJsonGroupedByURI(self, changeRequestJson):
        subject =  changeRequestJson["resourceUrl"]

        # Dictionaries of JSONs grouped by subject/object
        groupWhereResourceIsSubject = {}
        groupWhereResourceIsObject = {}

        for patch in changeRequestJson.get('addedData'):
            if patch['subject'] == subject:
                # Resource is subject
                if patch['subject'] in groupWhereResourceIsSubject:
                    groupWhereResourceIsSubject[patch['subject']]['addedData'].append(patch)
                else:
                    groupWhereResourceIsSubject[patch['subject']] = {}
                    groupWhereResourceIsSubject[patch['subject']]['addedData'] = []
                    groupWhereResourceIsSubject[patch['subject']]['deletedData'] = []
                    groupWhereResourceIsSubject[patch['subject']]['addedData'].append(patch)

                # Resource is subject, object is URI
                if patch['objectDatatype'] == 'uri':
                    if patch['object'] in groupWhereResourceIsObject:
                        groupWhereResourceIsObject[patch['object']]['addedData'].append(patch)
                    else:
                        groupWhereResourceIsObject[patch['object']] = {}
                        groupWhereResourceIsObject[patch['object']]['addedData'] = []
                        groupWhereResourceIsObject[patch['object']]['deletedData'] = []
                        groupWhereResourceIsObject[patch['object']]['addedData'].append(patch)

            else:
                # Resource is object
                if patch['object'] in groupWhereResourceIsObject:
                    groupWhereResourceIsObject[patch['object']]['addedData'].append(patch)
                else:
                    groupWhereResourceIsObject[patch['object']] = {}
                    groupWhereResourceIsObject[patch['object']]['addedData'] = []
                    groupWhereResourceIsObject[patch['object']]['deletedData'] = []
                    groupWhereResourceIsObject[patch['object']]['addedData'].append(patch)

                # Resource is object => subject is URI
                if patch['subject'] in groupWhereResourceIsSubject:
                    groupWhereResourceIsSubject[patch['subject']]['addedData'].append(patch)
                else:
                    groupWhereResourceIsSubject[patch['subject']] = {}
                    groupWhereResourceIsSubject[patch['subject']]['addedData'] = []
                    groupWhereResourceIsSubject[patch['subject']]['deletedData'] = []
                    groupWhereResourceIsSubject[patch['subject']]['addedData'].append(patch)



        for patch in changeRequestJson.get('deletedData'):
            if patch['subject'] == subject:
                # Resource is subject
                if patch['subject'] in groupWhereResourceIsSubject:
                    groupWhereResourceIsSubject[patch['subject']]['deletedData'].append(patch)
                else:
                    groupWhereResourceIsSubject[patch['subject']] = {}
                    groupWhereResourceIsSubject[patch['subject']]['addedData'] = []
                    groupWhereResourceIsSubject[patch['subject']]['deletedData'] = []
                    groupWhereResourceIsSubject[patch['subject']]['deletedData'].append(patch)

                # Resource is subject, object is URI
                if patch['objectDatatype'] == 'uri':
                    if patch['object'] in groupWhereResourceIsObject:
                        groupWhereResourceIsObject[patch['object']]['deletedData'].append(patch)
                    else:
                        groupWhereResourceIsObject[patch['object']] = {}
                        groupWhereResourceIsObject[patch['object']]['addedData'] = []
                        groupWhereResourceIsObject[patch['object']]['deletedData'] = []
                        groupWhereResourceIsObject[patch['object']]['deletedData'].append(patch)

            else:
                # Resource is object
                if patch['object'] in groupWhereResourceIsObject:
                    groupWhereResourceIsObject[patch['object']]['deletedData'].append(patch)
                else:
                    groupWhereResourceIsObject[patch['object']] = {}
                    groupWhereResourceIsObject[patch['object']]['addedData'] = []
                    groupWhereResourceIsObject[patch['object']]['deletedData'] = []
                    groupWhereResourceIsObject[patch['object']]['deletedData'].append(patch)

                # Resource is object => subject is URI
                if patch['subject'] in groupWhereResourceIsSubject:
                    groupWhereResourceIsSubject[patch['subject']]['deletedData'].append(patch)
                else:
                    groupWhereResourceIsSubject[patch['subject']] = {}
                    groupWhereResourceIsSubject[patch['subject']]['addedData'] = []
                    groupWhereResourceIsSubject[patch['subject']]['deletedData'] = []
                    groupWhereResourceIsSubject[patch['subject']]['deletedData'].append(patch)

        return [groupWhereResourceIsSubject, groupWhereResourceIsObject]

    def createResourceFolderStructure(self, resourceId):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        baseDir = self.directory + "/" + resourceId
        if not os.path.exists(baseDir):
            os.makedirs(baseDir)
            os.makedirs(baseDir + "/" + "as_subject")
            os.makedirs(baseDir + "/" + "as_object")

    def getResourceId(self, resourceUrl):
        return resourceUrl.replace('/', '_').replace(':', '_')

    def getSubjectPath(self, resourceName):
        return self.directory + "/" + self.getResourceId(resourceName) + "/" + "as_subject"

    def getObjectPath(self, resourceName):
        return self.directory + "/" + self.getResourceId(resourceName) + "/" + "as_object"
