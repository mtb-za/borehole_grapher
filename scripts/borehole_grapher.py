import sys
import numpy as npy
import matplotlib as mpl
from decimal import *
from matplotlib import pyplot
import os
import csv
from collections import Counter

class boreholes (object):
    def __init__(self, filename):
        self.filename = filename
        self._length  = None
        self._counter = None
        self._header = None
        self._columns = None

    def __len__(self):
        if self._length is None:
            for row in self: continue # Read the data for length and counter
        return self._length

    def __iter__(self):
        self._length  = 0
        self._counter = Counter()
        with open(self.filename, 'rU') as data:
            csvreader  = csv.DictReader(data)
            self._columns = zip (*csvreader)
            self._length = len(self._columns)
            for row in csvreader:
                # Save the statistics
                self._length  += 1
                self._counter[row['Borehole Number']] += 1
                yield row

    @property
    def import_columns(self):
        self._header = {}
        self._columns = []
        with open(self.filename, 'rU') as data:
            csvreader  = csv.DictReader(data)
            for row in csvreader:
                print type (row), row["Depth"]
                self._columns[row] = row
        print "Columns is", type(self._columns)

    @property
    def header (self):
        for col in range( len ( (self._columns) )):
            self._header.append ( self._columns[col][0] )
            print self._columns[col[0]]
        return self._header

    @property
    def columns (self):
        return self._columns

    @property
    def counter(self):
        if self._counter is None:
            for row in self: continue # Read the data for length and counter
        return self._counter

    @property
    def unique_boreholes(self):
        return self.counter.keys()

    def reset(self):
        """
        In case of partial seeks (e.g. breaking in the middle of the read)
        """
        self._length  = None
        self._counter = None

#These all work with importing and slicing the CSV file(s) we want to import.
def import_csv(filename):
    '''Import a CSV file for further analysis.'''
    print ('Importing from ' + filename)
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

def split_records(records, headers):
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

def split_sublists (records, important, headers):
    '''Takes a list of dicts and splits them according to changes in key value.

    For example, if passing a borehole ID as `item`, when the borehole ID
    changes, then a new list is created.

    Returns a list of lists of dicts. This could be better.'''
    item = important[0]
    print "Splitting according to", item

    records.append(make_empty_dict(headers))

    all_records = []
    new_record = []
    previous_row = records[0]
    for row in records:
        #print row[item], previous_row[item]
        #for item in important:
        if previous_row[item] == row[item]:
            new_record.append( row )
            print row[item]
        else:
            all_records.append (new_record)
            print "Appending", len(new_record), "records to all_records"
            #print new_record
            new_record = []
            new_record.append(row)
            print "=========================New Row========================="
        previous_row = row
    return all_records

def split_records_list (records, item):
    new_record = []
    previous_record = records[0]

if __name__ == "__main__":
    records = import_csv( sys.argv[1] )
    print type (records), type (records[0])

    header = csv_header(records)
    print header
    record_list = split_records (records, header)
    important_cols = ['BoreholeID', 'Date', 'Type']
    new_lists = split_sublists (records, important_cols, header)
    print "========="

    for i in range (len (new_lists)):
        print len(new_lists[i])
    print len (new_lists)
    print type (new_lists), type(new_lists[0]), type (new_lists[0][0])
    print "========="

    new_lists1 = split_sublists (new_lists[1], important_cols, header)
    for i in range (len (new_lists1)):
        print len(new_lists1[i])
    print len (new_lists1)
    print type (new_lists1), type(new_lists1[0]), type (new_lists1[0][0])
