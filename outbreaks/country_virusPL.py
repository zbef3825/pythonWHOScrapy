# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import requests
import json
import time

class countryVirusPL(object):

    def __init__(self):
        self.headers = {'Content-Type': 'application/json'}
        self.last_updated = {
            "virusName": 'null',
            "country": 'null',
            'lastUpdated': 'null'
        }

        last_row = requests.get("https://afternoon-garden-52459.herokuapp.com/api/get/lastrow")

        if last_row.json()['success']:
            self.last_updated["virusName"] = last_row.json()['list'][0]['virusname'].encode('utf-8')
            self.last_updated["country"] = last_row.json()['list'][0]['country'].encode('utf-8')
            self.last_updated["lastUpdated"] = last_row.json()['list'][0]['lastupdated']

        print ".........................Pipeline Initiated..........................."

    def uploading(self, uploading_data):
        time.sleep(5)
        outbreak = {
            "virusName": uploading_data['virusName'],
            "country": uploading_data['country'],
            "lastUpdated": uploading_data['lastUpdated']
        }
        # print json.dumps(outbreak)
        # http://localhost:3000/api/post
        # https://afternoon-garden-52459.herokuapp.com/api/post
        uploading_row = requests.post("https://afternoon-garden-52459.herokuapp.com/api/post", data=json.dumps(outbreak), headers=self.headers)
        print uploading_row.text
        if uploading_row.status_code == 200:
            print ".....................Data Saved.........................."
            return True
        else:
            print "..............Data is not save correctly................."
            return False

    def comparing(self, arg1, arg2):
        if (arg1['virusName'] == arg2['virusName']) & (arg1['country'] == arg2['country']):
            return True
        else:
            return False

    def process_item(self, item, spider):
        extracted_row = {
            "virusName": 'null',
            "country": 'null',
            "lastUpdated": 'null'
        }

        for index, data in enumerate(item['outbreakNameCountry']):
            virus_country_line = data.encode('utf-8').split(" \xe2\x80\x93 ", 1)
            virus = virus_country_line[0]
            country = virus_country_line[1]
            # print item['lastUpdated'][index]
            # print virus
            # print country

            extracted_row['virusName'] = virus
            extracted_row['country'] = country
            extracted_row['lastUpdated'] = item['lastUpdated'][index]
            comparison = self.comparing(self.last_updated, extracted_row)
            if comparison:
                print "........Breaking out from Loop........."
                spider.close_down = True
                break

            elif comparison == False:
                print "..............Uploading................"
                self.uploading(extracted_row)

        return item
