from urlparse import urlparse
import json
import ast

class PatchRequestPersistence:

    # store into file for now, consider DB later
    def __init__(self, dataSource):
        self.dataSource = dataSource

        # PatchRequest only for testing purposes store it and load all data
        # - to be deleted
        patchRequestTest = PatchRequest([{
            "instruction": "UPDATE",
            "changes": {
                "ADD": {
                    "subject": "http://dbpedia.org/page/Albert_Einstein",
                    "predicate": "http://xmls.com/foaf/0.1/accountName",
                    "value": {
                        "type": "literal",
                        "value": "123120194"
                    }
                },
                "DELETE": {
                    "subject": "http://dbpedia.org/page/Albert_Einstein",
                    "predicate": "http://xmls.com/foaf/0.1/accountName",
                    "value": {
                        "type": "literal",
                        "value": "123120194"
                    }
                }
            }},
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
            }])
        self.save(patchRequestTest)
        self.load()

    def save(self, patchRequest):
        print('Saving patch request.')

        with open(self.dataSource, 'a') as f:
            result = {}
            patchNum = 0
            for x in patchRequest.patchList:
                patchNum += 1
                result[str(patchNum)] = (patchRequest.patchList.get(patchNum).patchInstruction)

            json.dump(result, f)
            f.write('\n')

    def load(self):
        print('Loading patch requests...')
        patchRequests = {}
        with open(self.dataSource, 'r') as f:
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
    def __init__(self, patchRequestJson):

        # one patch request can contain several patches - store them in the dictionary
        self.patchList = {}

        patchNum = 0
        for patch in patchRequestJson:
            patchNum += 1
            self.patchList[patchNum] = (Patch(patch))

    def __str__(self):
        print('Printing patch request:')
        result = {}
        patchNum = 0
        for x in self.patchList:
            patchNum += 1
            result[str(patchNum)] = (self.patchList.get(patchNum).patchInstruction)

        return str(result)




class Patch():
    ##TODO: rebuild this method according to correct processing of patches and graphs and received JSON
    def __init__(self, patch):

        actualPatchInstructionString = patch.get('instruction')

        self.patchInstruction = {}
        self.patchInstruction['status'] = 'Open'
        self.patchInstruction['appliesTo'] = '-'
        self.patchInstruction['patchType'] = '-'
        self.patchInstruction['comment'] = '-'
        self.patchInstruction['memberOf'] = '-'

        self.patchInstruction['wasGeneratedBy'] = {}
        self.patchInstruction['wasGeneratedBy']['wasAssociatedWith'] = '-'
        self.patchInstruction['wasGeneratedBy']['confidence'] = '-'

        self.patchInstruction['update'] = {}

        # update instruction contains add and delete instruction
        if actualPatchInstructionString == 'UPDATE':
            patchUpdateInstructions = patch.get('changes')
            ##TODO Implement another solution of getting target graph
            self.patchInstruction['update']['target_graph'] = self.parseUrl(
                patchUpdateInstructions.get('ADD').get('subject'))
            self.patchInstruction['update']['target_subject'] = patchUpdateInstructions.get('ADD').get('subject')
            self.patchInstruction['update']['insert'] = {
                'predicate': patchUpdateInstructions.get('ADD').get('predicate'),
                'object': patchUpdateInstructions.get('ADD').get('value').get('value')}
            self.patchInstruction['update']['delete'] = {
                'predicate': patchUpdateInstructions.get('DELETE').get('predicate'),
                'object': patchUpdateInstructions.get('DELETE').get('value').get('value')}

        elif actualPatchInstructionString == 'DELETE' or actualPatchInstructionString == 'ADD':
            self.patchInstruction['update']['target_graph'] = self.parseUrl(
                patch.get('subject'))
            self.patchInstruction['update']['target_subject'] = patch.get('subject')
            self.patchInstruction['update'][actualPatchInstructionString] = {
                'predicate': patch.get('predicate'),
                'object': patch.get('value').get('value')}


    def parseUrl(self, url):
        parsedUrl = urlparse(url)
        return parsedUrl.scheme + '://' + parsedUrl.netloc + '/'

    def __str__(self):
        return str(self.patchInstruction)
