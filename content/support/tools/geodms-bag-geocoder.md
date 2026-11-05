---
title: GeoDMS BAG-Geocoder
description: With the GeoDMS-BAG geocoding configuration, you can make snapshots from and geocode against the Dutch Basic Administration of Addresses and Buildings (BAG) on your own computer,...
updated: '2018-11-05'
---

With the GeoDMS-BAG geocoding configuration, you can make snapshots from and geocode against the [Dutch Basic Administration of Addresses and Buildings (BAG)](http://www.kadaster.nl/web/Themas/Registraties/BAG/BAGartikelen/Wat-is-de-BAG.htm) on your own computer, for free. The BAG is a database with actual and historic information about addresses and buildings. It is very useful for lots of purposes (e.g. geocoding, determining building types, calculating accessibility indicators). It is open data and is available as a set of XML files.

We have co-developed this tool with [Object Vision B.V.](http://www.objectvision.nl), who maintain and further develop the GeoDMS software. Using this tool, you can geocode your own csv-files with address data on your own local computer. Next to the advantages that these local calculations are much faster than via a web service, especially for large datasets and the fact that it’s for free, you also get lots of meta-information about the geocode-level of your data (we have included no less than 16 different levels). Both main addresses and secondary addresses (‘nevenadres’ in BAG-terminology, relates to an object with multiple entrances), are included in our BAG-snapshot data.

The manual describes all necessary steps to geocode your own data. If you have any questions, or you have suggestions for further developing the tooling, feel free to contact Jasper Dekkers from SPINlab. Since the configuration is open source, you are free to develop it further by yourself. We kindly request you to share your developments with the community, so that others may profit from it as well.

If you want to be informed about future updates to this tool, follow Jasper Dekkers on Twitter or send Jasper an email.

## Minimum hardware requirements

The BAG is a large dataset and the geocode tool uses many aggregations. Therefore the tool needs sufficient internal memory. We experienced that on machines with 4Gb internal memory the tool becomes slow and might result in memory allocation errors. We therefore advise to use the tool on 64 bits machines, with 64 bits versions of the GeoDMS and 16Gb internal memory or more. This also applies to the Xml2FSS and MakeSnapshot projects. Additionally, running the configuration on a Solid State Disk (SSD0 instead of a regular rotating hard disk will speed up the calculations as well.

- [Licensing, citing and referring](#lic)
- [Downloads](#downl)

![geodms_bag](/files/2016/09/geodms_bag.jpg)

## Licensing, citing and referring

The GeoDMS software is available under the following license conditions: [www.objectvision.nl/geodms/software/license-and-disclaimer](http://www.objectvision.nl/geodms/software/license-and-disclaimer). The BAG-Geocoding configuration is available under GNU-GPL version 3 license, see [www.gnu.org/licenses/gpl-3.0.html](http://www.gnu.org/licenses/gpl-3.0.html) for more information.

The included CBS shapefiles with administrative region boundaries of municipalities, quarters and neighbourhoods (in Dutch the ‘Wijk en buurtkaart’) are available under CC-BY 3.0 license. When the CBS shapefiles are used to visualize area boundaries or data per region, you are obliged to include the following reference: © Kadaster / Centraal Bureau voor de Statistiek, 2016.
The shapefile containing NVM-regions has been constructed by Jasper Dekkers from SPINlab and may be used without referring.

When you use our geocoding configuration to geocode your data and subsequently use this data in your work, we kindly request you to recognize our work and refer to our geocoding configuration in the following way: **Dekkers, J.E.C. and Van der Beek, M., *Geocoding with the GeoDMS using BAG data. Making Snapshots from and Geocoding against the Dutch Basic Administration of Addresses and Buildings (BAG)*, Vrije Universiteit/Object Vision B.V., Amsterdam, 2017**.

## Downloads

- [Manual Geocoding using the BAG v0.8](/files/2017/04/Manual_Geocoding-using-the-BAG_v08.pdf) (.pdf, version 7 April 2017)
- [GeoDMS software](http://www.objectvision.nl/geodms/software) (install version 7.126 or higher)

### Easy download – One zip-file including tool & source data

- BAG-Geocoding configuration for GeoDMS, BAG-snapshot (addresses only) of 1 January 2017, CBS (2016) and NVM (2015) source data, all in one zip-file (.zip, 489 Mb – version 7 April 2017)
  Extract it to C:\GeoDMS and you are ready to go.

### Advanced download – Tool & source data folders separately

When you already are running other GeoDMS model configurations, like the Land Use Scanner model, you might want to extract the ProjDir-directory and the source data files separately and put them in your own folder structure. The zip-files below are meant for that purpose.  You will need to adjust some path name references in Geocode.dms, Bron.dms and MakeSnapshot.dms when you use other that the default path names, but with some GeoDMS experience this should not be a problem.

- [BAG-Geocoding configuration for GeoDMS](/files/2017/04/geocode_2017-04-07.zip) (.zip – version 7 April 2017)
- Pre-created BAG-snapshot from 1 January 2017 (.zip, 416 Mb – addresses only)
- CBS source data (municipalities, quarters and neighborhoods, 2016) (.zip)
- Province source data (provinces, 2016) (.zip)
- [NVM housing market regions 2015](/files/2016/09/nvm_2015.zip) (.zip)

#### Older versions of Geocoding-configuration, manuals and BAG-snapshots

- [BAG-Geocoding configuration for GeoDMS](/files/2016/09/geocode_2016-09-16.zip) (.zip – version 16 Sept. 2016)
- [Manual Geocoding using the BAG v0.5](/files/2016/09/Manual_Geocoding-using-the-BAG_v05.pdf) (.pdf, version 16 Sept. 2016)
- Pre-created BAG-snapshot from 1 January 2016 (.zip, 1.2 Gb – full snapshot)
