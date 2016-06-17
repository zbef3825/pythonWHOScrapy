# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import requests
import json
import time
import re

class countryVirusPL(object):

    def __init__(self):
        self.headers = {'Content-Type': 'application/json'}
        self.last_updated = {
            "virusName": 'null',
            "country": 'null',
            'lastUpdated': 'null'
        }
        # Comparison is not required anymore (Depreciated)
        # last_row = requests.get("https://afternoon-garden-52459.herokuapp.com/api/get/lastrow")
        #
        # if last_row.json()['success']:
        #     self.last_updated["virusName"] = last_row.json()['list'][0]['virusname'].encode('utf-8')
        #     self.last_updated["country"] = last_row.json()['list'][0]['country'].encode('utf-8')
        #     self.last_updated["lastUpdated"] = last_row.json()['list'][0]['lastupdated']

        self.result_array = []
        self.virusName = ""
        self.country = ""
        self.parsed_country = ""

        print ".........................Pipeline Initiated..........................."

    def uploading(self):
        # This function should accept array object

        # added sleep timer for no data collision
        time.sleep(5)
        # print json.dumps(outbreak)
        # http://localhost:3000/api/post
        # https://afternoon-garden-52459.herokuapp.com/api/post
        print self.result_array
        uploading_row = requests.post("https://afternoon-garden-52459.herokuapp.com/api/post", data=json.dumps(self.result_array),
                                      headers=self.headers)
        # print uploading_row.text
        if uploading_row.status_code == 200:
            print ".....................Data Saved.........................."
            return True
        else:
            print "..............Data is not save correctly................."
            return False

    def __re_org(self, uploading_data_parsed):
        # Accepts data and make object array
        # print uploading_data_parsed
        self.result_array.append(uploading_data_parsed)


    def parsing_data(self, uploading_data_raw):
        # Before uploading data, country name should be parsed correctly
        # refer to android parsing
        # If parsing is done correctly at this stage, android mobile will not suffer from data manipulation

        virus_raw = uploading_data_raw['virusName'].strip()
        self.country_raw = uploading_data_raw['country'].strip()

        #run regex on virusname if there is bracket
        acron = re.search("\\(([^)]+)\\)", virus_raw)
        if acron == None:
            # if no bracket was found, only need to capitalize First letter
            self.virusName = virus_raw.title()
        else:
            # if bracket was found, Need to capitalize Virus name
            # .group(0) yields with bracket
            # .group(1) yields without bracket(Only String inside)
            virus = acron.group(1)
            self.virusName = virus.upper()


        # Country name needs to parse many different regex
        if self.country_raw.lower() == "saint vincent and the grenadines":
            self.parsed_country = self.country_raw
            outbreak = {
                "virusName": self.virusName,
                "country": self.parsed_country,
                "lastUpdated": uploading_data_raw['lastUpdated']
            }
            self.__re_org(outbreak)

        elif self.country_raw.lower() == "trinidad and tobago":
            self.parsed_country = self.country_raw
            outbreak = {
                "virusName": self.virusName,
                "country": self.parsed_country,
                "lastUpdated": uploading_data_raw['lastUpdated']
            }
            self.__re_org(outbreak)
        else:
            # if country name is not indicated above, need to parse out dash and "and" word
            country = self.country_raw.split(" - ", 1)

            # if there is more than one in country var, it means we had dash in the string
            # Search for AND or ,
            # For multiple delimiter use regex
            if len(country) > 1:
                self.parsed_country = re.split(" and |, ", country[1])
            else:
                self.parsed_country = re.split(" and |, ", country[0])

            # For ever parsed_country element, push same virus name and last updated data into re_org function
            for i in xrange(len(self.parsed_country)):
                outbreak = {
                    "virusName": self.virusName,
                    "country": self.parsed_country[i],
                    "lastUpdated": uploading_data_raw['lastUpdated']
                }
                self.__re_org(outbreak)

    # No need to compare as the server will take care of comparison(Depreciate)
    # def comparing(self, arg1, arg2):
    #     if (arg1['virusName'] == arg2['virusName']) & (arg1['country'] == arg2['country']):
    #         return True
    #     else:
    #         return False

    # When process_item is called, we need to organize data and pass the raw data to self.parsing_data
    # parsing_data will parse data and add structured data to self.result_array
    def process_item(self, item, spider):
        extracted_row = {
            "virusName": 'null',
            "country": 'null',
            "lastUpdated": 'null'
        }

        for index, data in enumerate(item['outbreakNameCountry']):
            # virus_country_line = data.encode('utf-8').split(" \xe2\x80\x93 ", 1)
            virus_country_line = re.split(
                " \xe2\x80\x90 | \xe2\x80\x93 | \x2D ",
                data.encode('utf-8'))
            if len(virus_country_line) > 2:
                virus = virus_country_line[0]
                country = virus_country_line[2]
            else:
                virus = virus_country_line[0]
                country = virus_country_line[1]

            extracted_row['virusName'] = virus
            extracted_row['country'] = country
            extracted_row['lastUpdated'] = item['lastUpdated'][index]

            self.parsing_data(extracted_row)

            # comparison = self.comparing(self.last_updated, extracted_row)
            # if comparison:
            #     print "........Breaking out from Loop........."
            #     spider.close_down = True
            #     break
            #
            # elif comparison == False:
            #     print "..............Uploading................"
            #     self.uploading(extracted_row)

        self.uploading()

        return item
