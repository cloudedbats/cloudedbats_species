#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib 
import json
import urllib.request

class IucnRedlist(object):
    """ """
    def __init__(self, 
                 api_token=None,
                 debug=False):
        """ """
        self.api_token = api_token
        self.debug = debug
        #
        self.clear()
        #
        self.define_headers()
    
    def clear(self):
        """ """
        self.version = ''
        #
        self.chiroptera_count = 0
        self.chiroptera_dict = {}
        self.chiroptera_info_dict = {}
        self.chiroptera_checklist = {}
        #
        self.country_count = 0
        self.country_dict = {}
        #
        self.chiroptera_by_country_count = 0
        self.chiroptera_by_country_list = []
    
    def define_headers(self):
        """ """
        self.chiroptera_checklist_header = [
            'scientific_name', 
            'taxonid', 
            ]
        #
        self.chiroptera_info_header = [
            'scientific_name', 
            'taxonid', 
            'kingdom', 
            'phylum', 
            'class', 
            'order',  
            'family',   
            'genus', 
            'main_common_name', 
            'authority', 
            'published_year', 
            'category', 
            'criteria', 
            'marine_system', 
            'freshwater_system', 
            'terrestrial_system', 
            'aoo_km2', 
            'eoo_km2', 
            'elevation_upper', 
            'elevation_lower', 
            'depth_upper', 
            'depth_lower', 
            'assessor', 
            'reviewer',  
            'errata_flag', 
            'errata_reason', 
            'amended_flag', 
            'amended_reason', 
            ]
        #
        self.country_header = [
            'isocode', 
            'country',
            ]
        #
        self.chiroptera_by_country_header = [
            'country_isocode', 
            'taxonid', 
            'scientific_name', 
            'category',
            ]
    
    def redlist_version(self):
        """ """ 
        return self.version
    
    def redlist_citation(self):
        """ """ 
        citation_string = 'IUCN <YEAR>. IUCN Red List of Threatened Species. Version <VERSION> <www.iucnredlist.org>'
        citation_string = citation_string.replace('<YEAR>', self.version[0:4])
        citation_string = citation_string.replace('<VERSION>', self.version)
        return citation_string
    
    def chiroptera_info(self):
        """ """ 
        return self.chiroptera_info_dict
    
    def country_dict(self):
        """ """ 
        return self.country_dict
    
#     def region_dict(self):
#         """ """ 
#         return self.region_dict
    
    def chiroptera_by_country_list(self):
        """ """
        return self.chiroptera_by_country_list
    
    def get_all(self):
        """ """ 
        if not self.api_token:
            return
        #  
        self.get_version()
        #  
        self.get_chiroptera_species()
        #
        self.get_chiroptera_info()
        #
        self.get_countries()
        #
#         self.get_regions()
        #
        self.get_chiroptera_by_country()
        #
#         self.get_chiroptera_by_region()
   
    def save_all(self, dirpath='.'):
        """ """
        #
        version_file = pathlib.Path(dirpath, 'redlist_version.txt') 
        with version_file.open('w') as file:
            file.write(self.version)
        #  
        checklist_file = pathlib.Path(dirpath, 'redlist_chiroptera_checklist.txt') 
        with checklist_file.open('w') as file:
            file.write('\t'.join(self.chiroptera_checklist_header) + '\r\n')
            for species_dict in self.chiroptera_dict.values():
                file.write(species_dict['scientific_name'] + '\t' + 
                           str(species_dict['taxonid']) + '\r\n')
        #  
        info_file = pathlib.Path(dirpath, 'redlist_chiroptera_info.txt') 
        with info_file.open('w') as file:
            file.write('\t'.join(self.chiroptera_info_header) + '\r\n')
            for key in sorted(self.chiroptera_info_dict.keys()):
                species_dict = self.chiroptera_info_dict[key]
                row = []
                for item in self.chiroptera_info_header:
                    value = str(species_dict.get(item, ''))
                    if value == 'None':
                        value = ''
                    row.append(value)
                file.write('\t'.join(row) + '\r\n')
        #
        country_file = pathlib.Path(dirpath, 'redlist_countries.txt') 
        with country_file.open('w') as file:
            file.write('\t'.join(self.country_header) + '\r\n')
            for key in sorted(self.country_dict.keys()):
                file.write(key +'\t' + self.country_dict[key] + '\r\n')
        #
#         region_file = pathlib.Path(dirpath, 'redlist_regions.txt') 
#         with region_file.open('w') as file:
#             file.write('\t'.join(self.region_header) + '\r\n')
#             for key in sorted(self.region_dict.keys()):
#                 file.write(key + '\t' + self.region_dict[key] + '\r\n')
        #
        self.get_chiroptera_by_country()
        country_file = pathlib.Path(dirpath, 'redlist_chiroptera_by_countries.txt') 
        with country_file.open('w') as file:
            file.write('\t'.join(self.chiroptera_by_country_header) + '\r\n')
            for fields in self.chiroptera_by_country_list:
                file.write('\t'.join(fields) + '\r\n')
        #
#         self.get_chiroptera_by_region()
#         region_file = pathlib.Path(dirpath, 'redlist_chiroptera_by_regions.txt') 
#         with region_file.open('w') as file:
#             file.write('\t'.join(self.chiroptera_by_region_header) + '\r\n')
#             for fields in self.chiroptera_by_region_list:
#                 file.write('\t'.join(fields) + '\r\n')
   
    def load_all(self, dirpath='.'):
        """ """ 
        # Version.
        version_file = pathlib.Path(dirpath, 'redlist_version.txt') 
        with version_file.open('r') as file:
            self.version = file.read()
        
        # Checklist for Chiroptera. Taxonid and scientific_name.
        self.chiroptera_checklist = {} 
        checklist_file = pathlib.Path(dirpath, 'redlist_chiroptera_checklist.txt') 
        with checklist_file.open('r') as file:
            for index, row in enumerate(file):
                if index > 0:
                    parts = row.strip().split('\t')
                    if len(parts) > 1:
                        self.chiroptera_checklist[parts[0]] = int(parts[1]) # taxonid
        
        # Available countries.
        self.country_dict = {}
        version_file = pathlib.Path(dirpath, 'redlist_countries.txt') 
        with version_file.open('r') as file:
            for index, row in enumerate(file):
                if index > 0:
                    parts = row.strip().split('\t')
                    if len(parts) > 1:
                        self.country_dict[parts[0]] = parts[1]
        
        # Countries and species match list.
        self.chiroptera_by_country_list = {}
        version_file = pathlib.Path(dirpath, 'redlist_chiroptera_by_countries.txt') 
        with version_file.open('r') as file:
            for index, row in enumerate(file):
                if index > 0:
                    parts = row.strip().split('\t')
                    if len(parts) > 1:
                        self.chiroptera_by_country_list.append(parts)
        
   
    def get_version(self):
        """ Get IUCN version. """ 
        if not self.api_token:
            return
        #
        url = 'http://apiv3.iucnredlist.org/api/v3/version' + \
              '?token=' + self.api_token
        with urllib.request.urlopen(url) as response:  
            response_binary = response.read()
            if response_binary:
                response_json = json.loads(response_binary.decode('utf-8'))
                self.version = response_json.get('version', '')
        #
        if self.debug:
            print('DEBUG: version: ' + str(self.version))
    
    def get_chiroptera_species(self):
        """ Get IUCN species list and store species where order = Chiroptera. """    
        if not self.api_token:
            return
        #
        # http://apiv3.iucnredlist.org/api/v3/species/page/<page_number>?token=<YOUR TOKEN>
        page_number = 0
#         while (page_number is not None) and (page_number < 20):
        self.chiroptera = {} 
        self.chiroptera_checklist = {} 
        while (page_number is not None) and (page_number < 100):
            url = 'http://apiv3.iucnredlist.org/api/v3/species/page/' + str(page_number) + \
                  '?token=' + self.api_token
            with urllib.request.urlopen(url) as response:  
                response_binary = response.read()
                if not response_binary:
                    page_number = None
                else:
                    response_json = json.loads(response_binary.decode('utf-8'))
                    if response_json.get('count', 0) == 0:
                        page_number = None
                    else:
                        for row_dict in response_json.get('result', []):
                            if row_dict['order_name'] == 'CHIROPTERA':
                                self.chiroptera_count += 1
                                self.chiroptera_dict[row_dict['scientific_name']] = row_dict
                                self.chiroptera_checklist[row_dict['scientific_name']] = int(row_dict['taxonid'])
            #
            if self.debug:
                print('DEBUG: Page: ' + str(page_number) + 
                      '   Chiroptera acc. counter: ' + str(self.chiroptera_count))
            #
            if (page_number is not None):
                page_number += 1
                # page_number = None # For test.
        #
        if self.debug:
            print('DEBUG: Chiroptera total count: ' + str(self.chiroptera_count))
    
    def get_chiroptera_info(self):
        """ Iterate over countries and store Chiroptera species for each country. """ 
        if not self.api_token:
            return
        #
        for taxonid in list(self.chiroptera_checklist.values()):
            # http://apiv3.iucnredlist.org/api/v3/species/id/:id?token='YOUR TOKEN' 
            url = 'http://apiv3.iucnredlist.org/api/v3/species/id/' + str(taxonid) + \
                  '?token=' + self.api_token
            with urllib.request.urlopen(url) as response:  
                response_binary = response.read()
                if response_binary:
                    response_json = json.loads(response_binary.decode('utf-8'))
                    for row_dict in response_json.get('result', []):
                        scientific_name = row_dict['scientific_name']
                        self.chiroptera_info_dict[scientific_name] = row_dict
                        #
                        if self.debug:
                            print('DEBUG: Get info: ' + scientific_name)

    
    def get_countries(self):
        """ Get IUCN list of countries. """ 
        if not self.api_token:
            return
        #
        # http://apiv3.iucnredlist.org/api/v3/country/list?token=<YOUR TOKEN>   
        url = 'http://apiv3.iucnredlist.org/api/v3/country/list' + \
              '?token=' + self.api_token
        with urllib.request.urlopen(url) as response:  
            response_binary = response.read()
            if response_binary:
                response_json = json.loads(response_binary.decode('utf-8'))
                if response_json.get('count', 0) > 0:
                    for row_dict in response_json.get('results', []):
                        self.country_count += 1
                        self.country_dict[row_dict['isocode']] = row_dict['country']
    
    def get_chiroptera_by_country(self):
        """ Iterate over countries and store Chiroptera species for each country. """ 
        if not self.api_token:
            return
        #
        checklist_taxonids = list(self.chiroptera_checklist.values())
           
        for country_isocode in self.country_dict.keys():
#         for country_isocode in ['SE']: # For test. 
            if self.debug:
                print('DEBUG: Taxa in country: ' + country_isocode)

            # http://apiv3.iucnredlist.org/api/v3/country/getspecies/<country>?token=<YOUR TOKEN>  
            url = 'http://apiv3.iucnredlist.org/api/v3/country/getspecies/' + country_isocode.lower() + \
                  '?token=' + self.api_token
            with urllib.request.urlopen(url) as response:  
                response_binary = response.read()
                if response_binary:
                    response_json = json.loads(response_binary.decode('utf-8'))
                    for row_dict in response_json.get('result', []):
                        taxonid = row_dict['taxonid']
                        if taxonid in checklist_taxonids:
                            self.chiroptera_by_country_count += 1
                            self.chiroptera_by_country_list.append((country_isocode, 
                                                                    str(taxonid), 
                                                                    row_dict['scientific_name'], 
                                                                    row_dict['category']))

#
# === Regions does not work as expected.  Chiroptera not included. ===
#
#     def get_regions(self):
#         """ Get IUCN list of regions. """ 
#         # http://apiv3.iucnredlist.org/api/v3/country/list?token=<YOUR TOKEN>   
#         url = 'http://apiv3.iucnredlist.org/api/v3/region/list' + \
#               '?token=' + self.api_token
#         with urllib.request.urlopen(url) as response:  
#             response_binary = response.read()
#             if response_binary:
#                 response_json = json.loads(response_binary.decode('utf-8'))
#                 if response_json.get('count', 0) > 0:
#                     for row_dict in response_json.get('results', []):
#                         self.region_count += 1
#                         self.region_dict[row_dict['identifier']] = row_dict['name']
#         #
#         if self.debug:
#             for key in self.region_dict.keys():
#                 print('DEBUG: region: ' + key + '    name: ' + self.region_dict[key])
#             print('DEBUG: Region count: ' + str(self.region_count))
    
#     def get_chiroptera_by_region(self):
#         """ Iterate over regions and store Chiroptera species for each region. """    
#         if not self.api_token:
#             return
#         checklist_taxonids = list(self.chiroptera_checklist.values())   
# #         for region_id in self.region_dict.keys():
#         for region_id in ['eastern_africa']: # TODO: For test only. 
#             if self.debug:
#                 print('DEBUG: Taxa in region: ' + region_id)
#             #
#             page_number = 0    
#             while (page_number is not None) and (page_number < 100):
#                 # http://apiv3.iucnredlist.org/api/v3/species/region/<region>/page/0?token=<YOUR TOKEN>  
#                 url = 'http://apiv3.iucnredlist.org/api/v3/species/region/' + \
#                       region_id + \
#                       '/page/' + str(page_number) + \
#                       '?token=' + self.api_token
#                 with urllib.request.urlopen(url) as response:  
#                     response_binary = response.read()
#                     if not response_binary:
#                         page_number = None
#                     else:
#                         response_json = json.loads(response_binary.decode('utf-8'))
#                         
#                         if self.debug:
#                             print('Page: ', page_number, '   Count: ',  response_json.get('count', '-'))
#                         
#                         if response_json.get('count', 0) > 0:
#                             for row_dict in response_json.get('result', []):
#                                     taxonid = row_dict['taxonid']
#                                     if taxonid in checklist_taxonids:
#                                         self.chiroptera_by_region_count += 1
#                                         self.chiroptera_by_region_list.append((region_id, 
#                                                                                str(taxonid), 
#                                                                                row_dict['scientific_name'], 
#                                                                                row_dict['category']))
#                         else:
#                             page_number = None
#                 #
#                 if (page_number is not None):
#                     page_number += 1
                    


### Main. ###
if __name__ == "__main__":
    """ """
    redlist = IucnRedlist(api_token='', # Replace with your token.
                          debug = True)
    
#     redlist.load_all()
    
    redlist.get_all()
    
    redlist.save_all()
    
    print(redlist.redlist_citation())
    
