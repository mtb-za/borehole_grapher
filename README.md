# Borehole Grapher

This script takes a CSV file as input.

The CSV file is structured as such, although it is not hard-coded to be (any more).

Borehole Number,	Farm,	Owner,	Longitude,	Latitude,	Elevation,	Water Level,	Date,	Depth,	Reading,	Type

These are as follows:

* Borehole Number
  - Unique ID code for a given borehole. Used to split tests, and in filename of graph.
* Farm
  - The name of the farm. Not used except as output.
* Owner
  - The name of the farm's owner. Not used except as output.
* Longitude
  - Longitude in decimal degree format. Used to locate markers on final map.
* Latitude
  - Latitude in decimal degree format. Used to locate markers on final map.
* Elevation
  - The height of the borehole above mean sea level. Not used except as output.
* Water Level
  - This is the starting depth for a profile.
* Date
  - The date when the test was performed. Used in graph filename.
* Depth
  - The depth associated with a particular reading.
* Reading
  - This is the value read at a particular depth.
* Type
  - This is the type of test. It will generate the suffix used in the graph file.

##  How it works
The script reads in the values in the CSV file.
It creates a graph for each test, located at `graphs/<borehole number>_<type>_<date>.png`

A test is defined by having a different date, different borehole number or test type.
If any of these is different to the previous test, a new graph is created.

If a folder with photos is located at `photos/<borehole number>`, then a note is made that photos are available.

The various information is written to a `text/<borehole number>.html` file.
This is in the following format:
`<em>Borehole:</em> BH000</br>
<em>Farm:</em> FarmName</br>
<em>Owner:</em> Owner</br>
<em>Elevation:</em> 000.0</br></br>
<em>Date Visited:</em> 1970-01-01</br>
<em>Water Level:</em> 00.0</br>`

If a graph has been generated, it is added to the end:
`<img src="../graphs/BH000_EC_1970-01-01.png" width=50%></img></br>`

Likewise if a folder of photos is present:
`</br><a href="../photos/BH000">Photos available.</a>`

If an additional test is recorded, then it is added to the end.

Once this is done, a file compatible with leaflet.js is created.
This contains a marker for each test, with the co-ordinates for each borehole recorded, named `locations.js`.
In addition, this makes a pop-up which includes the basic information for the borehole.

##  Directory Structure

* `photos`
Contains folders with photos for each borehole. Subfolders need to be named `borehole number`.
* `scripts`
These are the main files to make things work. Includes the script, a `index.html` file template which will display a map, and `locations.js`.
* `text`
An .html file is created for each borehole, as detailed above. Each borehole will have one of these files which will open in a new tab when selected.
* `graphs`
A .png file is created for each test detected.

##  Generating text
In order to generate text, such as in the report or the marker, two lists are used.

The first list contains numbers or specific text to be replaced.
The second list contains the keys for which the value is placed into the text.

    ["Borehole: ", 0,
    "</br>Farm: ", 1,
    "</br>Owner: ", 2,
    "</br>Elevation: ", 3,
    "</br>Date visited: ", 4,
    "report_field", "<br/>"],
    [
    "BoreholeID",
    "Farm",
    "Owner",
    "Elevation",
    "Date"
    ]

Some methods use an additional key (such as the above `report_field`) in order to fill in a value that is not one in a column. The above generates a string similar to the following:

Borehole:  BH003 </br>Farm:  Vlakte </br>Owner:  Jim </br>Elevation:  452 </br>Date visited:  2015-03-12 <br/><a href="../text/BH003.html" target="_blank">Click for further information, </br>such as graphs, previous visits, photos &c.</a> <br/>

##  License

This code is licensed under a CC-BY license.

The existing test data is synthetic, based on an area where similar work is being undertaken.
