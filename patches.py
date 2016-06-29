from struct import pack

from urlparse import urlparse

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
        generatedPatches = self.generatePatchRequestJson(changeRequestJson)

        # Resource is subject - write to resource dir
        with open(self.getSubjectPath(resourceUrl) + "/" + 'Patch_' + str(patchRequestId) + ".json", 'w') as outfile:
            json.dump(generatedPatches[0], outfile)

        # Resource is object - write to resource dir
        with open(self.getObjectPath(resourceUrl) + "/" + 'Patch_' + str(patchRequestId) + ".json",
                    'w') as outfile:
            json.dump(generatedPatches[1], outfile)

        # Resource is object - write to subject dir
        for subjectId, value in generatedPatches[2].iteritems():
            self.createResourceFolderStructure(self.getResourceId(subjectId))
            with open(self.getSubjectPath(subjectId) + "/" + 'Patch_' + str(patchRequestId) + ".json",
                      'w') as outfile:
                json.dump(value, outfile)

        # Resource is subject - write to object dir
        for objectId, value in generatedPatches[3].iteritems():
            self.createResourceFolderStructure(self.getResourceId(objectId))
            with open(self.getObjectPath(objectId) + "/" + 'Patch_' + str(patchRequestId) + ".json",
                      'w') as outfile:
                json.dump(value, outfile)


    def load(self, patchRequestUrl):
        print('Loading patch requests for URL: ' + patchRequestUrl)

        patchRequests = {}
        patchRequests['deletedData'] = []
        patchRequests['addedData'] = []

        if patchRequestUrl == '':
            for root, dirs, files in os.walk(self.directory):
                for file in files:
                    print('Reading from file: ' + file)
                    with open(os.path.join(root, file), "r") as data_file:
                        data = json.load(data_file)
                        patchRequests['deletedData'].append(data['deletedData'])
                        patchRequests['addedData'].append(data['addedData'])
            return patchRequests

        path = self.getSubjectPath(patchRequestUrl)
        for filename in os.listdir(path):
            print('Reading from file: ' + filename)
            with open(path + '/' + filename) as data_file:
                data = json.load(data_file)
                patchRequests['deletedData'].append(data['deletedData'])
                patchRequests['addedData'].append(data['addedData'])

        path = self.getObjectPath(patchRequestUrl)
        for filename in os.listdir(path):
            print('Reading from file: ' + filename)
            with open(path + '/' + filename) as data_file:
                data = json.load(data_file)
                patchRequests['deletedData'].append(data['deletedData'])
                patchRequests['addedData'].append(data['addedData'])

        return patchRequests

    def generatePatchRequestJson(self, changeRequestJson):
        subject =  changeRequestJson["resourceUrl"]

        # JSON to be stored in the folder structure of the resource
        resourceAsSubjectStoredInResource = {}
        resourceAsSubjectStoredInResource['addedData'] = []
        resourceAsSubjectStoredInResource['deletedData'] = []

        # JSON to be stored in the folder structure of the resource
        resourceAsObjectStoredInResource = {}
        resourceAsObjectStoredInResource['addedData'] = []
        resourceAsObjectStoredInResource['deletedData'] = []

        # JSONs to be stored in the target folder structue
        # (target, predicate, resource)/(resource, predicate, target)
        resourceAsObjectStoredInTarget = {}
        resourceAsSubjectStoredInTarget = {}

        for patch in changeRequestJson.get('addedData'):
            if patch['subject'] == subject:
                resourceAsSubjectStoredInResource['addedData'].append(patch)
                if patch['objectDatatype'] == 'uri':
                    resourceAsSubjectStoredInTarget[patch['object']] = {}
                    resourceAsSubjectStoredInTarget[patch['object']]['addedData'] = []
                    resourceAsSubjectStoredInTarget[patch['object']]['deletedData'] = []
                    resourceAsSubjectStoredInTarget[patch['object']]['addedData'].append(patch)

            else:
                resourceAsObjectStoredInResource['addedData'].append(patch)

                if patch['subject'] in resourceAsObjectStoredInTarget:
                    resourceAsObjectStoredInTarget[patch['subject']]['addedData'].append(patch)
                else:
                    resourceAsObjectStoredInTarget[patch['subject']] = {}
                    resourceAsObjectStoredInTarget[patch['subject']]['addedData'] = []
                    resourceAsObjectStoredInTarget[patch['subject']]['deletedData'] = []
                    resourceAsObjectStoredInTarget[patch['subject']]['addedData'].append(patch)



        for patch in changeRequestJson.get('deletedData'):
            if patch['subject'] == subject:
                resourceAsSubjectStoredInResource['deletedData'].append(patch)
                if patch['objectDatatype'] == 'uri':
                    resourceAsSubjectStoredInTarget[patch['object']] = {}
                    resourceAsSubjectStoredInTarget[patch['object']]['addedData'] = []
                    resourceAsSubjectStoredInTarget[patch['object']]['deletedData'] = []
                    resourceAsSubjectStoredInTarget[patch['object']]['deletedData'].append(patch)

            else:
                resourceAsObjectStoredInResource['deletedData'].append(patch)

                if patch['subject'] in resourceAsObjectStoredInTarget:
                    resourceAsObjectStoredInTarget[patch['subject']]['deletedData'].append(patch)
                else:
                    resourceAsObjectStoredInTarget[patch['subject']] = {}
                    resourceAsObjectStoredInTarget[patch['subject']]['addedData'] = []
                    resourceAsObjectStoredInTarget[patch['subject']]['deletedData'] = []
                    resourceAsObjectStoredInTarget[patch['subject']]['deletedData'].append(patch)

        return [resourceAsSubjectStoredInResource, resourceAsObjectStoredInResource, resourceAsObjectStoredInTarget, resourceAsSubjectStoredInTarget]

    def createResourceFolderStructure(self, resourceId):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        baseDir = self.directory + "/" + resourceId
        if not os.path.exists(baseDir):
            os.makedirs(baseDir)
            os.makedirs(baseDir + "/" + "as_subject")
            os.makedirs(baseDir + "/" + "as_object")

    def getResourceId(self, resourceUrl):
        return resourceUrl.replace('/', '_')

    def getSubjectPath(self, resourceName):
        return self.directory + "/" + self.getResourceId(resourceName) + "/" + "as_subject"

    def getObjectPath(self, resourceName):
        return self.directory + "/" + self.getResourceId(resourceName) + "/" + "as_object"
