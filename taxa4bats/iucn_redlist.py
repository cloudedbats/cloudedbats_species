#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018-present Arnold Andreasson
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import json
import urllib.request
import xlsxwriter


class IucnRedlist(object):
    """ """

    def __init__(self, api_token=None, debug=False):
        """ """
        self.api_token = api_token
        self.debug = debug
        #
        self.clear()
        #
        self.define_headers()

    def clear(self):
        """ """
        self.version = ""
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
        self.chiroptera_summary_header = [
            "family",
            "genus",
            "scientific_name",
            "main_common_name",
            "category",
            "countries",
        ]
        #
        self.chiroptera_checklist_header = [
            "scientific_name",
            "taxonid",
        ]
        #
        self.chiroptera_info_header = [
            "scientific_name",
            "taxonid",
            "kingdom",
            "phylum",
            "class",
            "order",
            "family",
            "genus",
            "main_common_name",
            "authority",
            "published_year",
            "category",
            "criteria",
            "marine_system",
            "freshwater_system",
            "terrestrial_system",
            "aoo_km2",
            "eoo_km2",
            "elevation_upper",
            "elevation_lower",
            "depth_upper",
            "depth_lower",
            "assessor",
            "reviewer",
            "errata_flag",
            "errata_reason",
            "amended_flag",
            "amended_reason",
        ]
        #
        self.country_header = [
            "isocode",
            "country",
        ]
        #
        self.chiroptera_by_country_header = [
            "country_isocode",
            "taxonid",
            "scientific_name",
            "category",
        ]

    def get_redlist_version(self):
        """ """
        return self.version

    def get_redlist_citation(self):
        """ """
        citation_string = "IUCN <YEAR>. IUCN Red List of Threatened Species. Version <VERSION> <www.iucnredlist.org>"
        citation_string = citation_string.replace("<YEAR>", self.version[0:4])
        citation_string = citation_string.replace("<VERSION>", self.version)
        return citation_string

    def get_chiroptera_info_dict(self):
        """ """
        return self.chiroptera_info_dict

    def get_country_dict(self):
        """ """
        return self.country_dict

    def get_chiroptera_by_country_list(self):
        """ """
        return self.chiroptera_by_country_list

    def get_all_from_api(self):
        """ """
        if not self.api_token:
            return
        #
        self.rest_get_version()
        #
        self.rest_get_chiroptera_species()
        #
        self.rest_get_chiroptera_info()
        #
        self.rest_get_countries()
        #
        self.rest_get_chiroptera_by_country()

    def save_all(self, dirpath="data"):
        """ """
        #
        if not pathlib.Path(dirpath).exists():
            pathlib.Path(dirpath).mkdir()
        #
        version_file = pathlib.Path(dirpath, "redlist_version.txt")
        with version_file.open("w") as file:
            file.write(self.version)
        #
        checklist_file = pathlib.Path(dirpath, "redlist_chiroptera_checklist.txt")
        with checklist_file.open("w") as file:
            file.write("\t".join(self.chiroptera_checklist_header) + "\r\n")
            for species_dict in self.chiroptera_dict.values():
                file.write(
                    species_dict["scientific_name"]
                    + "\t"
                    + str(species_dict["taxonid"])
                    + "\r\n"
                )
        #
        info_file = pathlib.Path(dirpath, "redlist_chiroptera_info.txt")
        with info_file.open("w") as file:
            file.write("\t".join(self.chiroptera_info_header) + "\r\n")
            for key in sorted(self.chiroptera_info_dict.keys()):
                species_dict = self.chiroptera_info_dict[key]
                row = []
                for item in self.chiroptera_info_header:
                    value = str(species_dict.get(item, ""))
                    if value == "None":
                        value = ""
                    row.append(value)
                file.write("\t".join(row) + "\r\n")
        #
        country_file = pathlib.Path(dirpath, "redlist_countries.txt")
        with country_file.open("w") as file:
            file.write("\t".join(self.country_header) + "\r\n")
            for key in sorted(self.country_dict.keys()):
                file.write(key + "\t" + self.country_dict[key] + "\r\n")
        #
        country_file = pathlib.Path(dirpath, "redlist_chiroptera_by_countries.txt")
        with country_file.open("w") as file:
            file.write("\t".join(self.chiroptera_by_country_header) + "\r\n")
            for fields in self.chiroptera_by_country_list:
                file.write("\t".join(fields) + "\r\n")

    def load_all(self, dirpath="data"):
        """ """
        # Version.
        version_file = pathlib.Path(dirpath, "redlist_version.txt")
        with version_file.open("r") as file:
            self.version = file.read()

        # Checklist for Chiroptera. Taxonid and scientific_name.
        self.chiroptera_checklist = {}
        checklist_file = pathlib.Path(dirpath, "redlist_chiroptera_checklist.txt")
        with checklist_file.open("r") as file:
            for index, row in enumerate(file):
                if index > 0:
                    parts = row.strip().split("\t")
                    if len(parts) > 1:
                        self.chiroptera_checklist[parts[0]] = int(parts[1])  # taxonid

        # Chiroptera info.
        self.chiroptera_checklist = {}
        info_file = pathlib.Path(dirpath, "redlist_chiroptera_info.txt")
        with info_file.open("r") as file:
            for index, row in enumerate(file):
                if index == 0:
                    header = row.strip().split("\t")
                else:
                    parts = row.strip().split("\t")
                    species_dict = dict(zip(header, parts))
                    if len(parts) > 1:
                        self.chiroptera_info_dict[parts[0]] = species_dict

        # Available countries.
        self.country_dict = {}
        version_file = pathlib.Path(dirpath, "redlist_countries.txt")
        with version_file.open("r") as file:
            for index, row in enumerate(file):
                if index > 0:
                    parts = row.strip().split("\t")
                    if len(parts) > 1:
                        self.country_dict[parts[0]] = parts[1]

        # Countries and species match list.
        self.chiroptera_by_country_list = []
        version_file = pathlib.Path(dirpath, "redlist_chiroptera_by_countries.txt")
        with version_file.open("r") as file:
            for index, row in enumerate(file):
                if index > 0:
                    parts = row.strip().split("\t")
                    if len(parts) > 1:
                        self.chiroptera_by_country_list.append(parts)

    def rest_get_version(self):
        """ Get IUCN version. """
        if not self.api_token:
            return
        #
        url = "https://apiv3.iucnredlist.org/api/v3/version" + "?token=" + self.api_token
        with urllib.request.urlopen(url) as response:
            response_binary = response.read()
            if response_binary:
                response_json = json.loads(response_binary.decode("utf-8"))
                self.version = response_json.get("version", "")
        #
        if self.debug:
            print("DEBUG: version: " + str(self.version))

    def rest_get_chiroptera_species(self):
        """ Get IUCN species list and store species where order = Chiroptera. """
        if not self.api_token:
            return
        #
        # https://apiv3.iucnredlist.org/api/v3/species/page/<page_number>?token=<YOUR TOKEN>
        page_number = 0
        #         while (page_number is not None) and (page_number < 20):
        self.chiroptera = {}
        self.chiroptera_checklist = {}
        while (page_number is not None) and (page_number < 100):
            url = (
                "https://apiv3.iucnredlist.org/api/v3/species/page/"
                + str(page_number)
                + "?token="
                + self.api_token
            )
            with urllib.request.urlopen(url) as response:
                response_binary = response.read()
                if not response_binary:
                    page_number = None
                else:
                    response_json = json.loads(response_binary.decode("utf-8"))
                    if response_json.get("count", 0) == 0:
                        page_number = None
                    else:
                        for row_dict in response_json.get("result", []):
                            if row_dict["order_name"] == "CHIROPTERA":
                                self.chiroptera_count += 1
                                self.chiroptera_dict[
                                    row_dict["scientific_name"]
                                ] = row_dict
                                self.chiroptera_checklist[
                                    row_dict["scientific_name"]
                                ] = int(row_dict["taxonid"])
            #
            if self.debug:
                print(
                    "DEBUG: Page: "
                    + str(page_number)
                    + "   Chiroptera acc. counter: "
                    + str(self.chiroptera_count)
                )
            #
            if page_number is not None:
                page_number += 1
                # page_number = None # For test.
        #
        if self.debug:
            print("DEBUG: Chiroptera total count: " + str(self.chiroptera_count))

    def rest_get_chiroptera_info(self):
        """ Iterate over countries and store Chiroptera species for each country. """
        if not self.api_token:
            return
        #
        for taxonid in list(self.chiroptera_checklist.values()):
            # https://apiv3.iucnredlist.org/api/v3/species/id/:id?token='YOUR TOKEN'
            url = (
                "https://apiv3.iucnredlist.org/api/v3/species/id/"
                + str(taxonid)
                + "?token="
                + self.api_token
            )
            with urllib.request.urlopen(url) as response:
                response_binary = response.read()
                if response_binary:
                    response_json = json.loads(response_binary.decode("utf-8"))
                    for row_dict in response_json.get("result", []):
                        scientific_name = row_dict["scientific_name"]
                        self.chiroptera_info_dict[scientific_name] = row_dict
                        #
                        if self.debug:
                            print("DEBUG: Get info: " + scientific_name)

    def rest_get_countries(self):
        """ Get IUCN list of countries. """
        if not self.api_token:
            return
        #
        # https://apiv3.iucnredlist.org/api/v3/country/list?token=<YOUR TOKEN>
        url = (
            "https://apiv3.iucnredlist.org/api/v3/country/list"
            + "?token="
            + self.api_token
        )
        with urllib.request.urlopen(url) as response:
            response_binary = response.read()
            if response_binary:
                response_json = json.loads(response_binary.decode("utf-8"))
                if response_json.get("count", 0) > 0:
                    for row_dict in response_json.get("results", []):
                        self.country_count += 1
                        self.country_dict[row_dict["isocode"]] = row_dict["country"]

    def rest_get_chiroptera_by_country(self):
        """ Iterate over countries and store Chiroptera species for each country. """
        if not self.api_token:
            return
        #
        checklist_taxonids = list(self.chiroptera_checklist.values())

        for country_isocode in self.country_dict.keys():
            #         for country_isocode in ['SE']: # For test.
            if self.debug:
                print("DEBUG: Taxa in country: " + country_isocode)

            # https://apiv3.iucnredlist.org/api/v3/country/getspecies/<country>?token=<YOUR TOKEN>
            url = (
                "https://apiv3.iucnredlist.org/api/v3/country/getspecies/"
                + country_isocode.lower()
                + "?token="
                + self.api_token
            )
            with urllib.request.urlopen(url) as response:
                response_binary = response.read()
                if response_binary:
                    response_json = json.loads(response_binary.decode("utf-8"))
                    for row_dict in response_json.get("result", []):
                        taxonid = row_dict["taxonid"]
                        if taxonid in checklist_taxonids:
                            self.chiroptera_by_country_count += 1
                            self.chiroptera_by_country_list.append(
                                (
                                    country_isocode,
                                    str(taxonid),
                                    row_dict["scientific_name"],
                                    row_dict["category"],
                                )
                            )

    def create_excel(self, dirpath="."):
        """ Export to Excel. """
        #
        excel_filepathname = pathlib.Path(
            dirpath, "redlist_chiroptera_" + self.get_redlist_version() + ".xlsx"
        )
        # Create Excel document.
        workbook = xlsxwriter.Workbook(str(excel_filepathname))

        # Add worksheets.
        summary_worksheet = workbook.add_worksheet("Chiroptera summary")
        info_worksheet = workbook.add_worksheet("Chiroptera info")
        countries_worksheet = workbook.add_worksheet("Countries")
        species_by_country_worksheet = workbook.add_worksheet("Chiroptera by country")
        citation_worksheet = workbook.add_worksheet("Citation")
        about_worksheet = workbook.add_worksheet("About")

        # Create cell formats.
        self.bold_format = workbook.add_format({"bold": True})

        # === Sheet: Chiroptera summary. ===
        # Header.
        summary_worksheet.write_row(
            0, 0, self.chiroptera_summary_header, self.bold_format
        )
        # Rows.
        row_nr = 1
        for key in sorted(self.chiroptera_info_dict.keys()):
            species_dict = self.chiroptera_info_dict[key]
            row = []
            for item in self.chiroptera_summary_header:
                value = str(species_dict.get(item, ""))
                if value == "None":
                    value = ""
                elif item == "family":
                    value = value.capitalize()
                elif item == "countries":
                    countries = []
                    taxonid = species_dict.get("taxonid", "")
                    for country_row in self.chiroptera_by_country_list:
                        if country_row[1] == taxonid:
                            countries.append(country_row[0])
                    value = ", ".join(sorted(countries))
                #
                row.append(value)
            #
            summary_worksheet.write_row(row_nr, 0, row)
            row_nr += 1

        # === Sheet: Chiroptera info. ===
        # Header.
        info_worksheet.write_row(0, 0, self.chiroptera_info_header, self.bold_format)
        # Rows.
        row_nr = 1
        for key in sorted(self.chiroptera_info_dict.keys()):
            species_dict = self.chiroptera_info_dict[key]
            row = []
            for item in self.chiroptera_info_header:
                value = str(species_dict.get(item, ""))
                if value == "None":
                    value = ""
                row.append(value)
            #
            info_worksheet.write_row(row_nr, 0, row)
            row_nr += 1

        # === Sheet: Countries. ===
        # Header.
        countries_worksheet.write_row(0, 0, self.country_header, self.bold_format)
        # Rows.
        row_nr = 1
        for key in sorted(self.country_dict.keys()):
            countries_worksheet.write_row(row_nr, 0, [key, self.country_dict[key]])
            row_nr += 1

        # === Sheet: Chiroptera by country. ===
        # Header.
        species_by_country_worksheet.write_row(
            0, 0, self.chiroptera_by_country_header, self.bold_format
        )
        # Rows.
        row_nr = 1
        for row in sorted(self.chiroptera_by_country_list):
            species_by_country_worksheet.write_row(row_nr, 0, row)
            row_nr += 1

        # === Sheet: Citation. ===
        # Header.
        citation_worksheet.write_row(0, 0, ["IUCN Redlist citation"], self.bold_format)
        # Rows.
        readme_text = [
            [""],
            ["IUCN Redlist citation:"],
            [""],
            ["    " + self.get_redlist_citation()],
            [""],
        ]
        #
        row_nr = 1
        for row in readme_text:
            citation_worksheet.write_row(row_nr, 0, row)
            row_nr += 1

        # === Sheet: Source code. ===
        # Header.
        about_worksheet.write_row(0, 0, ["About"], self.bold_format)
        # Rows.
        readme_text = [
            [""],
            ["This Excel file is a part of the open source "],
            ["project CloudedBats.org: http://cloudedbats.org "],
            [""],
            ["Source code to generate the Excel file can be "],
            ["found in this GitHub repository: "],
            ["- https://github.com/cloudedbats/cloudedbats_species "],
            [""],
            ["Notes: "],
            ["- You must ask IUCN for a personal token to access "],
            ["  their API: https://apiv3.iucnredlist.org/api/v3/token "],
            ["- Commercial use of the Red List API is not allowed. "],
            ["- Do not forget the acknowledgement and citation text "],
            ["  when using it. "],
            [""],
        ]
        #
        row_nr = 1
        for row in readme_text:
            about_worksheet.write_row(row_nr, 0, row)
            row_nr += 1

        # === Adjust column width. ===
        summary_worksheet.set_column("A:B", 20)
        summary_worksheet.set_column("C:D", 40)
        summary_worksheet.set_column("E:E", 10)
        summary_worksheet.set_column("F:F", 40)

        info_worksheet.set_column("A:A", 40)

        countries_worksheet.set_column("A:A", 20)
        countries_worksheet.set_column("B:B", 40)

        species_by_country_worksheet.set_column("A:B", 20)
        species_by_country_worksheet.set_column("C:C", 40)
        species_by_country_worksheet.set_column("D:D", 20)

        citation_worksheet.set_column("A:A", 100)
        about_worksheet.set_column("A:A", 100)

        # === Done. Close the Excel document. ===
        workbook.close()


### Main. ###
if __name__ == "__main__":
    """ """

    token = "<TOKEN>"  # Replace with your token.

    redlist = IucnRedlist(api_token=token, debug=True)
    if len(token) > 10:
        # Update from IUCN Red list. This will take some time
        # since all taxa must be checked to find out if they
        # belongs to Chiroptera.
        redlist.get_all_from_api()
        redlist.save_all(dirpath="taxa4bats/data")

    # Load from cache if token not given.
    redlist.clear()
    redlist.load_all(dirpath="taxa4bats/data")

    redlist.create_excel()

    print("Done. ", redlist.get_redlist_citation())

