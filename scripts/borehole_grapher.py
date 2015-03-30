import sys
import numpy as npy
import matplotlib as mpl
from decimal import *
from matplotlib import pyplot
import os
import csv

#These all work with importing and slicing the CSV file(s) we want to import.
def import_csv(filename, verbose=False):
    '''Import a CSV file for further analysis.'''
    if verbose:
        print ('Importing from' , filename)
    records = []
    with open(sys.argv[1]) as csvfile:
        imported_data = csv.DictReader(csvfile, delimiter = ',')
        for row in imported_data:
            records.append( row )
    return records

def csv_header(records):
    '''This function will take in a generator and return the first item.'''
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
    have created/generated.
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

def print_record_summary (records):
    for i in range (len (records)):
        print records[i][0]["BoreholeID"], len(records[i])
    print "Total tests:", len (records)

def getXY_values ( record, xy, verbose=False, make_Y_negative = True):
    X, Y = [], []
    XName, YName = '',''
    for index in range (len (record)):
        if verbose:
            print record[index][xy[0]]
        X.append ( record[index][xy[0]] )
        if make_Y_negative:
            print record[index]["BoreholeID"], record[index][xy[1]]
            Y.append ( 0 - float(record[index][xy[1]]) )
        else:
            Y.append ( record[index][xy[1]] )
    if verbose:
        print "X:", X
        print "Y:", Y
    return (X, Y)

def make_title (record, title_scheme, title_columns, join=' ', verbose=False):
    col = 0
    title = title_scheme[:] #This took way too long to work out....
    for index in range(len(title_scheme)-1):
        if verbose:
            print "Length of title_scheme:", len(title_scheme), \
              "| Index for title:", index, "| title_scheme[index]:",\
              title_scheme[index], "|", title_columns[col], "|\ntitle_scheme",\
              title_scheme, "| record[title_columns[col]]",\
              record[title_columns[col]]
        if type( title_scheme[index] ) == type(0):
            title[index] = record[title_columns[col]]
            col += 1
    if verbose:
        print "Scheme:",title_scheme, "| Title", title
    return join.join(title)

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
        new_xy = getXY_values (records[record], xy)

        #We can repurpose make_title() to define our filename for each graph.
        graph_filename = make_title (records[record][0], graph_file[0],\
          graph_file[1], '')

        #New we will set the axis labels. We search a dict to correlate a
        #Type of test to the unit needed.
        for outer in range (len ( records[record])):
            for index in XLabel:
                if index == records[record][outer]["Type"]:
                    XName = XLabel[index]
        YName = YLabel["Depth"]

        #We call make_title() to get the title for each graph.
        for index in range( len(records[record])):
            graph_title = make_title (records[record][index], title_scheme[0],\
              title_scheme[1])
            if verbose:
                print graph_title

        #And finally, we make and save the plot.
        mpl.pyplot.close()
        mpl.pyplot.xlabel(XName)
        mpl.pyplot.ylabel(YName)
        mpl.pyplot.title( graph_title )
        mpl.pyplot.plot(new_xy[0], new_xy[1])
        mpl.pyplot.savefig(graph_filename, dpi=200)
        #mpl.pyplot.show()

'''def plot_markers (records):
    for index in range( len( records )):
        record_set = set(records[index])
        print record_set'''

if __name__ == "__main__":
    records = import_csv( sys.argv[1] )

    header = csv_header(records)
    record_list = split_records (records, header)
    important_cols = ['BoreholeID', 'Date', 'Type']
    new_lists = split_sublists (records, important_cols, header)

    #print_record_summary(new_lists)
    xy = ("Reading", 'Depth')
    title_pattern = ( [0, 'test in', 2, '\n', 4, ' (', 6, ')'],
        ["Type", "BoreholeID", "Farm", "Owner"] )
    graph_file = ( ['../graphs/', 1 , "_", 3, "_", 5, ".png"],
        ["BoreholeID", "Type", "Date"] )
    YLabel = {"Depth": "Depth below surface (m)"}
    XLabel = {"G-G": "N", "EC": "Siemens per Second"}
    graph_records (new_lists, xy, title_pattern, graph_file, XLabel, YLabel)
    #plot_markers (new_lists)
