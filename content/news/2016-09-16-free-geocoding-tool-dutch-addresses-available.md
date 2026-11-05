---
title: Free Geocoding tool for Dutch addresses available
date: '2016-09-16'
description: The SPINlab is proud to present a free geocoding tool. It can be used to attach X,Y-coordinates to Dutch addresses and uses the Dutch Basic Administration of Addresses and...
themes:
- support
image: /files/2016/09/bag_geodms_structure.jpg
---

![bag_geodms_structure](/files/2016/09/bag_geodms_structure.jpg){: .side }

The SPINlab is proud to present a free geocoding tool. It can be used to attach X,Y-coordinates to Dutch addresses and uses the Dutch Basic Administration of Addresses and Buildings (BAG) as it’s geocoding source.

Using an open source GIS-platform (GeoDMS), which is a small but powerful piece of software, the BAG-XML is transformed into a native GeoDMS-format. After that, it can be used as a local geocoding service.

You simply put a csv-file with address data in a designated directory, click ‘Export file’  in the geocoding tool, and a resulting csv-file is created that includes your original data, supplemented with X,Y-coordinates, BAG-ID (in case of a unique match) and more data.
Also metadata about the geocoding process is provided (i.e. how many addresses on what geocode levels have been processed).

Visit [the tools’ web page](/support/tools/bag-toolkit/) for more information and to download the tool and the source data.
