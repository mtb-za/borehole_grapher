import sys
import numpy as npy
import matplotlib as mpl
from decimal import *
from matplotlib import pyplot
import os
import csv

#These all work with importing and slicing the CSV file(s) we want to import.
def import_csv(filename, verbose=False):
    '''Import a CSV file for further analysis.
    * returns: `records`: a list of dicts, with the header of each column
    being the key.
    '''
    if verbose:
        print ('Importing from' , filename)
    records = []
    with open(sys.argv[1]) as csvfile:
        imported_data = csv.DictReader(csvfile, delimiter = ',')
        for row in imported_data:
            records.append( row )
    return records

def csv_header(records):
    '''
    This function will take in a generator and return the first item.
    Utility here is that it will create a list of the headers of the csv file.
    '''
    tmp = zip(*records)
    header = []
    for i in range ( len (tmp)):
        header.append (tmp[i][0])
    return header

def split_records(records, headers, verbose=False):
    '''This will read in a list of dicts and a list of strings.
    It then steps through the list of headers and will use the strings as keys
    to access the dict values.
    Each set of keys will create a list in a 2D matrix.

    In other words, this will create a 2D matrix based on the headers that you
    have passed/generated. These should be linked to the csv file parsed.
    '''
    split_data, column = [],0

    for col in header:
        split_data.append([])
        for row in range ( len (records) ):
            split_data[column].append (records[row][col])
        column += 1
    if verbose:
        print column, "valid columns found in file", sys.argv[1]
    return split_data

def make_empty_dict (headers):
    '''Takes the list of headers and makes an empty dict with the same headers.
    Utility function.'''
    tmp_list = []
    for i in range(len( headers )):
        tmp_list.append('')
    empty_record = dict()
    for i in headers:
        empty_record [i] = ''
    return empty_record

def split_sublists (records, important_cols, headers, verbose=False):
    '''Takes a list of dicts and splits them according to changes in key value.

    For example, if passing a borehole ID as `item`, when the borehole ID
    changes, then a new list is created.

    Returns a list of lists of dicts.'''
    item = important_cols[0]

    records.append(make_empty_dict(headers))
    #This is only required in order to add the last list of records, which are
    #otherwise ignored.

    all_records = []
    new_record = []
    previous_row = records[0]
    for row in records:
        if previous_row[item] == row[item]:
            new_record.append( row )
        else:
            if verbose:
                print "Appending", len(new_record), "records to all_records"
            if len( new_record ) > 1 and len( important_cols ) > 1:
                if verbose:
                    print "Split according to", item
                    print "Recursing to test", important_cols[1:]
                tmp_list = split_sublists( new_record, important_cols[1:], headers)
                for list_item in tmp_list:
                    all_records.append ( list_item )
            else:
                all_records.append (new_record)
            new_record = []
            new_record.append(row)
            if verbose:
                print "=========================New Test========================="
        previous_row = row
    return all_records

def print_record_summary (records, column):
    '''
    Utility function to print out something about the tests read in.
    Will give the number of readings for each `column` and the total number of
    tests detected.
    '''
    for i in range (len (records)):
        print records[i][0][column], len(records[i])
    print "Total tests:", len (records)

#The following functions do most of the work for presentation.
#This includes things like generating graphs and making marker points.
def getXY_values ( record, xy, verbose=False, make_Y_negative = True):
    '''
    Extracts and returns the values for X and Y for a given test.
    This works on a list of dicts, and should be given for each test.

    Intended to be used for graphing these values.

    *returns: `(X,Y)`: tuple of lists with the X and Y values for each test.
    '''
    X, Y = [], []
    XName, YName = '',''
    for index in range (len (record)):
        if verbose:
            print type (record[index][xy[0]]), record[index][xy[0]]
            print type (float (record[index][xy[0]]) ), float(record[index][xy[0]])
        X.append ( float(record[index][xy[0]]) )
        if make_Y_negative:
            Y.append ( float(record[index][xy[1]]) * -1 )
        else:
            Y.append ( float(record[index][xy[1]]) )
    if verbose:
        print "X:", X
        print "Y:", Y
    return (X, Y)

def make_text (record, text_scheme, text_columns, join=' ', verbose=False):
    '''
    Utility function which replaces numbers in a list with values from a given
    record.
    For example, if passed the following tuple:
    title_pattern = ( [0, 'test in', 2, '\n', 4, ' (', 6, ')'],
            ["Type", "BoreholeID", "Farm", "Owner"] )
    each will then be combined to use the Type, BoreholeID, Farm and Owner
    of each record, filling those values in, in order within the
    overall pattern.

    * returns: `title`: a list of strings with the substituted values.
    '''


    col = 0
    text = text_scheme[:] #This took way too long to work out....
    for index in range(len(text_scheme)-1):
        if verbose:
            print "Length of text_scheme:", len(text_scheme), \
              "| Index for text:", index, "| text_scheme[index]:",\
              text_scheme[index], "|", text_columns[col], "|\ntext_scheme",\
              text_scheme, "| record[text_columns[col]]",\
              record[text_columns[col]]
        if type( text_scheme[index] ) == type(0):
            text[index] = str(record[text_columns[col]])
            col += 1
    if verbose:
        print "Scheme:",text_scheme, "| text", text
    return text

def graph_records (records, xy, title_scheme, graph_file, XLabel, YLabel, \
  make_Y_negative = True, verbose=False):
    '''
    Generates a graph of each record. The filenames and the titles are
    generated from the data.

    make_Y_negative is optional, but it will make the Y-axis plot such that 0
    is at the top. If your depths are given with negatives already, this should
    be false. That is, if you have depths: 32, 33, 34 then you want -32, -33,
    -34 in order to see the profile from surface in a more intuituve manner.
    '''
    for record in range( len(records)):
        if len (records[record]) == 1:
            continue
        if verbose:
            print record

        #We need to get a list of the X and Y values. getXY_values() does this.
        new_xy = getXY_values (records[record], xy, verbose)

        #We can repurpose make_text() to define our filename for each graph.
        graph_filename = ''.join(make_text (records[record][0], graph_file[0],\
          graph_file[1], verbose))

        #New we will set the axis labels. We search a dict to correlate a
        #Type of test to the unit needed.
        for outer in range (len ( records[record])):
            for index in XLabel:
                if index == records[record][outer]["Type"]:
                    XName = XLabel[index]
        YName = YLabel["Depth"]

        #We call make_text() to get the title for each graph.
        graph_title = ' '.join(make_text (records[record][0], title_scheme[0],\
          title_scheme[1], verbose))
        if verbose:
            print graph_title

        #And finally, we make and save the plot.
        mpl.pyplot.close()
        mpl.pyplot.xlabel(XName)
        mpl.pyplot.ylabel(YName)
        mpl.pyplot.title( graph_title )
        mpl.pyplot.plot(new_xy[0], \
          new_xy[1])
        mpl.pyplot.savefig(graph_filename, dpi=200)
        #mpl.pyplot.show()

def plot_markers (records, marker_text, popup_text, verbose=False):
    '''
    Generates a locations.js file, which records the locations of each record.
    These comprise a popup marker, with selected information on it.

    There is a known bug in that it will add multiple markers if there are
    multiple tests.
    '''
    with open("locations.js", "wt") as out_file: #Clear the existing file.
        out_file.write( '' )
    for record in range( len(records)):


        text = make_text (records[record][0], marker_text[0],\
          marker_text[1], verbose)
        if verbose:
            print text

        for index in range ( len( text)):
            if text[index] == 'report_field':
                report_loc = ''.join(['<a href="../text/',
                  records[record][0]["BoreholeID"],
                '" target="_blank">Click for further information, </br>',
                  "such as graphs, previous visits, photos &c.</a>"])
                text[index] = report_loc
                if verbose:
                    print "Adding report link:", report_loc

        text = ' '.join(text)

        location = str ( round(float(records[record][0]["Latitude"]),5) * -1),\
          str ( round(float(records[record][0]["Longitude"]),5) )
        print location
        if verbose:
            print records[record][0]["BoreholeID"], "location:", location
        popup_template = make_text (records[record][0], popup_text[0],\
          popup_text[2], verbose )
        for index in range ( len( popup_template)):
            if verbose:
                print "Adding additional fields: text and report link.", popup_template[index]
            if popup_template[index] == 'user_text':
                popup_template[index] = text

        marker_template = make_text (records[record][0], popup_text[1],\
          popup_text[2], verbose)
        loc_col = 0
        for index in range ( len( marker_template)):
            if verbose:
                print "Adding additional fields: text and report link.", marker_template[index]
            if marker_template[index] == 'user_text':
                marker_template[index] = location[loc_col]
                loc_col += 1
                if verbose:
                    print "Adding location data."

        popup_template = ''.join(popup_template)
        marker_template = ''.join(marker_template)

        with open("locations.js", "at") as out_file:
            out_file.write( popup_template )
            out_file.write( marker_template )

        if verbose:
            print "Marker for", records[record][0]["BoreholeID"], "generated."

def get_surface_reading(record, xy, make_Y_negative=True, verbose=False):
    X, Y = '',''
    if verbose:
        print type (record[xy[0]]), record[xy[0]]
        print type (float (record[xy[0]]) ), float(record[xy[0]])
    X = float(record[xy[0]])
    if make_Y_negative:
        Y = float(record[xy[1]]) * -1
    else:
        Y = float(record[xy[1]])
    if verbose:
        print "X:", X
        print "Y:", Y
    return (X, Y)

def generate_report(records, file_ID, report_template, graph_file, XLabel,
  verbose=False):
    '''Will create a html file for each borehole.'''
    for record in range( len ( records )):
        html_path = ''.join(["../text/", records[record][0][file_ID], ".html"])
        if verbose:
            print html_path

        report_text = make_text (records[record][0], report_template[0],\
          report_template[1])

        photo_loc = ''.join(['../photos/', records[record][0][file_ID]])
        full_photo_loc = ''.join(['<a href="../photos/',
          records[record][0][file_ID],'>Photos available</a>'])
        if verbose:
            print photo_loc, full_photo_loc
        graph_loc = ''.join(make_text (records[record][0], graph_file[0],\
          graph_file[1], verbose))
        full_graph_loc = ''.join(['<img src="', graph_loc, '" width=50%></img>'])
        if verbose:
            print graph_loc, full_graph_loc
        for index in range ( len( report_text)):
            if verbose:
                print "Replacing missing fields: photos and graphs",\
                  report_text[index]
            if report_text[index] == 'photographs':
                if verbose:
                    print "Trying to add photos:"
                if os.path.exists( photo_loc ):
                    report_text[index] = full_photo_loc
                    if verbose:
                        print "adding photos:", photo_loc
                else:
                    report_text[index] = ""
                    if verbose:
                        print "No photos, skipping."
            elif report_text[index] == 'graph':
                if os.path.exists( graph_loc ):
                    report_text[index] = full_graph_loc
                    if verbose:
                        print "adding graph:", graph_loc
                else:
                    if verbose:
                        print "No graph, adding surface reading."
                    xy = ("Reading", "Depth")
                    surface_reading = get_surface_reading(records[record][0],
                    xy, True, verbose )
                    print surface_reading
                    surface_reading = ' '.join (["Water level:",
                      str( surface_reading[1] ), "Surface reading:",
                      str( surface_reading[0]) ], XLabel)
                    report_text[index] = surface_reading
        report_text = ''.join(report_text)
        if verbose:
            print report_text
        if os.path.exists( html_path ): #This will append, since the file exists.
            with open(html_path, "at") as out_file:
                out_file.write( report_text )
        else:
            with open(html_path, "wt") as out_file:
                out_file.write( report_text )

if __name__ == "__main__":
    records = import_csv( sys.argv[1] )

    header = csv_header(records)
    record_list = split_records (records, header)
    important_cols = ['BoreholeID', 'Date', 'Type']
    new_lists = split_sublists (records, important_cols, header)
    print_record_summary(new_lists, "BoreholeID")

    #print_record_summary(new_lists)
    xy = ("Reading", 'Depth') #Choose the columns to use as X and Y.
    #This is the pattern that make_text() will use to generate the title for
    #each graph.
    title_pattern = ( [0, 'test in', 2, '\n', 4, ' (', 6, ')'],
        ["Type", "BoreholeID", "Farm", "Owner"] )
    #These are possible labels. As you have more test types, the values of the
    #X-axis will be different. The Y-axis is anticipated to be depth,
    #regardless of what is tested.
    YLabel = {"Depth": "Depth below surface (m)"}
    XLabel = {"G-G": "N", "EC": "Siemens per Second"}
    #Pattern for filename for each graph.
    graph_file = ( ['../graphs/', 1 , "_", 3, "_", 5, ".png"],
    ["BoreholeID", "Type", "Date"] )
    graph_records (new_lists, xy, title_pattern, graph_file, XLabel, YLabel)

    #Pattern which will be used for creating popup markers.
    popup_pattern = (
    [ "var ", 1,
    " = L.popup({maxWidth:600, maxHeight:600}).setContent('",
    "user_text",
    "')\n\n"
    ],
    ["L.marker([",
    "user_text", ',', "user_text", "],{riseOnHover: true,title:'", 0,
    "', opacity:0.5})\n\t.addTo(map)\n\t.bindPopup(", 1, ")\n\n"
    ],
    ["BoreholeID",
    "BoreholeID"
    ]
    )

    #Pattern to be used for the text on a popup marker.
    marker_text_pattern = (
    ["Borehole:", 0,
    "</br>Farm:", 1,
    "</br>Owner:", 2,
    "</br>Elevation:", 3,
    "</br>Date visited:", 4,
    "report_field", "<br/>"],
    [
    "BoreholeID",
    "Farm",
    "Owner",
    "Elevation",
    "Date"
    ]
    )

    plot_markers (new_lists, marker_text_pattern, popup_pattern, True)

    report_text_pattern = (
    ["</br></br>Borehole:", 0,
    "</br>Farm:", 1,
    "</br>Owner:", 2,
    "</br>Elevation:", 3,
    "</br>Date visited:", 4,"<br/>",
    "photographs", "<br/>",
    "graph",''],
    [
    "BoreholeID",
    "Farm",
    "Owner",
    "Elevation",
    "Date"
    ]
    )
    generate_report (new_lists, "BoreholeID", report_text_pattern, graph_file, XLabel, True)
