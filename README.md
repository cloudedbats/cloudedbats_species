# CloudedBats - Species

This is a part of CloudedBats: http://cloudedbats.org

## taxa4bats

The software library taxa4bats contains taxonomic information for bats (Chiroptera). All data is collected from the IUCN Red List of Threatened Species (https://www.iucnredlist.org) since in covers most of the bats that exists, and the species lists are maintained with two or three published updates each year.

When running the Python script [/taxa4bats/iucn_redlist.py](/taxa4bats/iucn_redlist.py) the API at IUCN Redlist is called and all relevant information for bats is downloaded. The data is then stored in text files as a cache for usage between the published updates. An Excel file is also generated that can be downloaded separately. Note that you need to ask for a Token before you can run the script by yourself. It's free, but they don't like commercial use without written permission.

The main usage for taxa4bats is to serve cloudedbats_desktop_app and cloudedbats_web with taxonomic information. 

But the Excel file can be used directly. It's really good if you want to check the species list for a specific country, just use the filter function in Excel and search for 'SE' in the countries column get the species list for Sweden. If you don't use Excel the free alternative "LibreOffice calc" can be used.

Download the Excel file here: [redlist_chiroptera_2019-1.xlsx](/taxa4bats/redlist_chiroptera_2019-1.xlsx) 

![WURB-A001](CloudedBats_IUCN-Redlist_Excel.png?raw=true  "Swedish species filtered in LibreOffice Calc.")
Swedish species filtered in LibreOffice Calc. CloudedBats.org / [CC-BY](https://creativecommons.org/licenses/by/3.0/)

## Contact

Arnold Andreasson, Sweden.

info@cloudedbats.org
