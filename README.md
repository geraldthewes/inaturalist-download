iNaturalist Image Dataset
=========================

Introduction
------------

Observations from iNaturalist.org, an online social network of people sharing biodiversity information to help each other learn about nature.

Information on how to download the data can be found here

https://www.gbif.org/dataset/50c9509d-22c7-4a22-a47d-8c48425ef4a7

More information on iNaturalist can be found on their [website](https://www.inaturalist.org/)


Preparing the data
------------------

once you download the Zip file, you will have two large CSV files

observations.csv and media.csv

observations.csv contains information on each speciies
media.csv contains teh URL for each image

Since they are large, i recommend you convert them to parquet format for faster operations.
This is best done using the excellent project duckdb.

You can then use duckdb to convert the files

```
COPY (SELECT id,occurrenceID,basisOfRecord,modified,institutionCode,collectionCode,datasetName,informationWithheld,catalogNumber,"references",occurrenceRemarks,recordedBy,recordedByID,identifiedBy,identifiedByID,captive,eventDate,eventTime,verbatimEventDate,verbatimLocality,decimalLatitude,decimalLongitude,coordinateUncertaintyInMeters,geodeticDatum,countryCode,stateProvince,identificationID,dateIdentified,identificationRemarks,taxonID,scientificName,taxonRank,kingdom,phylum,"class","order",family,genus,license,rightsHolder,inaturalistLogin,publishingCountry,sex,lifeStage,reproductiveCondition AS foo
	    FROM read_csv('/mnt/data6/AI/plants/inaturalist/observations.csv',AUTO_DETECT=TRUE))
  TO '/mnt/data6/AI/plants/inaturalist/observations.parquet' (FORMAT 'PARQUET', CODEC 'ZSTD');
```

```
COPY (SELECT id,type,format,identifier,"references",created,creator,publisher,license,rightsHolder,catalogNumber AS foo
	    FROM read_csv('/mnt/data6/AI/plants/inaturalist/media.csv',AUTO_DETECT=TRUE))
  TO '/mnt/data6/AI/plants/inaturalist/media.parquet' (FORMAT 'PARQUET', CODEC 'ZSTD');
```

Then to create a list of images to download execute the following join

```
COPY
    (SELECT M.id, M."identifier",  M."foo", M."format" FROM "observations.parquet" AS O  RIGHT JOIN  "media.parquet" AS M ON O.id = M.id  WHERE O.kingdom = 'Plantae')
    TO 'fetch.parquet'
    (FORMAT 'parquet', COMPRESSION 'zstd', ROW_GROUP_SIZE 100_000);
```

I was interested in only downloading the plant images, but feel free to customize your where clause.

Downloading Images
------------------

use the download.py script, after installing the required dependencies, to donwload as in

```
python download_images.py --parquet your_file.parquet --output output_directory
```

