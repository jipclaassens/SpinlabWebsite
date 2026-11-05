---
title: Land Use Scanner model
description: The Land Use Scanner model – Applications, model development, downloads & exercises VU University Amsterdam has a long-standing experience in integrated land use modelling....
updated: '2023-12-01'
---

**The Land Use Scanner model – Applications, model development, downloads & exercises**

VU University Amsterdam has a long-standing experience in integrated land use modelling.![W_scenarios_midNL_550px](/files/2016/04/W_scenarios_midNL_550px.jpg){: .side } Research is done in both a [national](/publications/land-use-scanner-publications/#NL) and an [international](/publications/land-use-scanner-publications/#EU) context. Applications include studies into the future of agriculture in the Netherlands, deforestation in Surinam, climate impacts and adaptation measures. Most of this research was carried out for and with an operational land use model that integrates urban and non-urban types of land use, the Land Use Scanner.

This integrated GIS-based land use model was first developed in close cooperation with the Netherlands Environmental Assessment Agency (PBL), Geodan and the Agricultural Economics Research Institute (LEI). It has been under constant development since its conception, and most recently by the Netherlands Environmental Assessment Agency (PBL) and Object Vision for several urbanisation studies (e.g. [PBL, 2021](https://www.pbl.nl/publicaties/grote-opgaven-in-een-beperkte-ruimte)).

The [GeoDMS framework](https://github.com/ObjectVision/GeoDMS) underlying *Land Use Scanner* is developed and maintained by the [Object Vision](https://www.objectvision.nl) company and also applied in other spatially explicit models. Examples include a land-use modelling framework for the European Commission that covers all member states of the European Union at a 100-metre resolution ([Lavalle et al., 2011](https://doi.org/10.1007/978-3-642-21928-3_5)) and the 2UP model that simulates urban development and population change around the globe ([Koomen et al., 2023](https://doi.org/10.1016/j.compenvurbsys.2022.101935)). A full account of the original *Land Use Scanner* is provided by [Hilferink and Rietveld (1999)](https://doi.org/10.1007/978-3-642-21928-3_5), whereas recent applications are documented in a book by [Koomen and Borsboom-van Beurden (2011)](https://doi.org/10.1007/978-94-007-1822-7).

This website provides more information on the outline and characteristics of the model. A fully functional demonstration version of the model can be downloaded [here.](/support/tools/landusescanner/)

**Model Outline**

The Land Use Scanner is a GIS-based model that produces simulations of future land use based on the integration of sector-specific inputs from dedicated models. The model is based on demand-supply interaction for land, with sectors competing for allocation within suitability and policy constraints. It uses a comparatively static approach that simulates a future state in a limited number of time steps. Recent applications simulate land-use patterns in three subsequent time steps, whereas initial applications used only one or two.

Unlike many other land-use models, the objective of the Land Use Scanner is not to forecast the ![140710_figuur1_4_550px](/files/2016/04/140710_figuur1_4_550px.jpg)dimension of land-use change but rather to integrate and allocate future land-use demand from different sector-specific models or experts. The next figure presents the basic structure of the Land Use Scanner model.

External regional projections of land-use change, which are usually referred to as demand or claims, are used as input for the model. These are land-use type-specific and can be derived from, for example, sector-specific models of specialised institutes. The predicted land-use changes are considered an additional demand for the different land-use types compared with the present area in use for each land-use type.

The total of the additional demand and the present area for each land-use function is allocated to individual grid cells based on the suitability of the cell. The definition of local suitability may incorporate many spatial datasets referring to the following aspects discussed below: current land use, physical properties, operative policies, and market forces generally expressed in distance relations to nearby land-use functions.

**Model Characteristics**

Some general, characteristic features of the Land Use Scanner are:

|  |  |
| --- | --- |
| *Grid-based* | The model describes for all grids in a system the relative proportions of land to be used for a number of land use types. Model specification and software allow large numbers of grids. The present model version covering the Netherlands uses 100 by-100-meter grid cells. |
| *Integrated* | The model provides an integration framework for sector-specific databases and policy proposals by confronting these inputs in a spatial-analytical context. |
| *Exhaustive* | The model is exhaustive in the sense that all grids in a spatial unit (in most cases, a country) are considered. All types of land use are explicitly considered; thus, no remaining categories are left untreated. The model can be formulated in such a way that transfers of wet grids (sea, lakes) into land are allowed. |
| *Dynamic* | The model deals with changes in land use, taking into account present land use patterns. The suitabilities of the grids for certain types of land use are not assumed constant but may change due to changes in land use over time. Recent applications distinguish up to three timesteps in the simulation. |
| *Satellite structure* | The model is driven by forecasts at a national or regional level in terms of variables such as population, agricultural production, infrastructure, etc. |
| *Policy-oriented* | Several types of sector-specific policies have strong spatial implications. Land Use Scanner makes these implications explicit. The model helps solve questions referring to the types of grids in which major policy conflicts can be expected to emerge. It can also be used to investigate the implications of sector-specific and macro policies for human settlement and land use patterns. |

The property of integration means that the Land Use Scanner can function as a tool to improve communication between analysts working in various fields of land use (for example, urban functions versus agriculture versus natural land use). The model also helps to improve consistency between projections made in these fields. Thus, a potential use of the Land Use Scanner is that is does not only function as a modelling tool but also as a communication tool between analysts in various policy fields.
