---
title: BAG toolkit
description: Turn the Dutch register of buildings and addresses (BAG) into data you can model with, and geocode your own address files. Open source, on your own computer.
---

The BAG is the Dutch national register of buildings and addresses: every building, address, dwelling and public space in the Netherlands, with its geometry, status and full history. The Kadaster publishes it every month as a free extract of more than 6,000 XML files. That format suits exchange but not analysis, because it holds every change an object ever had and nothing in it is a table.

The [BAG toolkit](https://github.com/ObjectVision/BAG-Tools) converts the extract into compact stores for [GeoDMS](https://www.geodms.nl/). It succeeds the BAG geocoder that SPINlab developed with [Object Vision](https://www.objectvision.nl/), who now develop and maintain the toolkit.

## What it does

| Tool | What you get |
|---|---|
| [Xml2MMD](https://github.com/ObjectVision/BAG-Tools/wiki/BAG20-Xml2MMD) | One compact store per object type, with the full history of the BAG |
| [MakeSnapshot](https://github.com/ObjectVision/BAG-Tools/wiki/How-to-use-the-MakeSnapshot-Script) | The BAG at a date you choose, optionally for part of the country, with relations, classifications, the [type of residential building](https://github.com/ObjectVision/BAG-Tools/wiki/Woonpand-typering), addresses and heights |
| [Geocode](https://github.com/ObjectVision/BAG-Tools/wiki/How-to-use-the-geocode-script) | Your csv file of addresses with coordinates and BAG attributes. It matches through sixteen levels, from a full address down to the place name alone, and [tells you for each record which level it reached](https://github.com/ObjectVision/BAG-Tools/wiki/How-to-interpret-the-GeoCode-results) |

## What you need

- [GeoDMS 20.23.1](https://github.com/ObjectVision/GeoDMS/releases) or later
- 16 GB of memory or more
- about 110 GB of free disk space during the conversion, most of it for the unpacked XML
- the free [BAG 2.0 extract from the Kadaster](https://www.kadaster.nl/zakelijk/producten/adressen-en-gebouwen/bag-2.0-extract)
- for building heights, [Pand Hoogte Nederland](https://github.com/ObjectVision/PandHoogteNederland/wiki)

## Get started

The [toolkit's page on GitHub](https://github.com/ObjectVision/BAG-Tools) has the steps, and the [wiki](https://github.com/ObjectVision/BAG-Tools/wiki) describes each tool, its options and its results. Questions and problems go in the [issues](https://github.com/ObjectVision/BAG-Tools/issues).

The toolkit is available under the GNU GPL version 3.
