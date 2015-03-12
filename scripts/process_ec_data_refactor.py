import sys
import numpy as npy
import matplotlib as mpl
from decimal import *
from matplotlib import pyplot
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os

class Input(QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        
        nameLabel = QLabel("Name")
        self.nameLine = QLineEdit()
        self.submitButton = QPushButton("Submit")
        
        buttonLayout1 = QVBoxLayout()
        buttonLayout1.addWidget(nameLabel)
        buttonLayout1.addWidget(self.nameLine)
        buttonLayout1.addWidget(self.submitButton)
        
        self.submitButton.clicked.connect(self.submitContact)
        
        mainLayout = QGridLayout()
        mainLayout.addLayout(buttonLayout1, 0, 1)
        
        self.setLayout(mainLayout)
        self.setWindowTitle("Hello Qt")
        
        
def ImportCSV(*args, **kwargs):
	'''Import a CSV file for further analysis.'''
	try:
		if args[0]:
			print 'Importing from ' + args[0]
			data = npy.genfromtxt(args[0], delimiter=',', names=True, dtype=None)
			print 'Data imported'
			return data
		else:
			print 'Importing from standard file'
			data = npy.genfromtxt('ec_profiles.csv', delimiter=',', names=True, dtype=None)
			print 'Data imported'
			return data
	except IOError:
		print 'File not found.'

def SplitCSV(data, *args, **kwargs):
	'''Breaks the .csv file into a series of lists.

	The .csv file is formatted as following:
	Borehole Number,	Farm,	Owner,	Longitude,	Latitude,	Elevation,	Water Level,	Date,	Depth,	Reading'''
	Reading = [Decimal( i[9]/10 ) for i in data]	#Note conversion from mS/cm to mS/m is done automatically
	Depth = [Decimal( -i[8] ) for i in data]		#We want a depth below surface, so take it as negative.
	Borehole = [i[0] for i in data]
	FarmName,OwnerName = [i[1] for i in data],[i[2] for i in data]
	Lat, Long = [Decimal( -i[4] ) for i in data],[Decimal( i[3] ) for i in data]
	Elev, WaterLev, Date = [i[5] for i in data],[i[6] for i in data],[i[7] for i in data]
	Type = [i[10] for i in data]
	print 'Splitting CSV file into arrays.'
	return [Borehole, FarmName, OwnerName, Lat, Long, Elev, WaterLev, Date, Depth, Reading, Type]

def CreateSublists(data, *args, **kwargs):
	'''This takes a list of lists.
	Each sublist comprises the values associated with a particular Borehole ID.
	Everything but the readings is Borehole-level data, so this is only recorded once.'''
	#Unpack the incoming data list of lists.
	Borehole, FarmName, OwnerName, Lat, Long, Elev, WaterLev, Date, Depth, Reading, Type = data[:]
	#Create needed variables
	tmpX,tmpY = [],[]
	Set,i,Graphing = 0,0,0		#Set is the index for the current borehole. i is an index for the tmp array, at which we will insert a value.
	X,Y = [],[]
	BHList, FarmList, OwnerList = [],[],[]	#These will be used for titles when making the graphs.
	East,South = [],[]	#This is a list of each co-ordinate. Maybe this is better done as a list of tuples? In any case, it works.
	BHElev, BHWaterLev, TestDate = [],[],[]
	TestType = []
	GraphDone = []

	#Cycle through the Borehole list and break when the Borehole Number changes.
	#Then add the (sub)list of values to the list which will be passed to matplotlib.
	#This will also create lists which the marker in leaflet needs to display.
	print 'Creating sublists. ' + str(len(Borehole)) + ' readings to process.'
	for pos in range(len(Borehole)):
		#print 'Currently processing reading ' + str(pos)
		if pos + 1 == len(Borehole):	#Prevent over-run error from checking if the next borehole ID matches the current one.
			print 'End of list.'
			break
		elif Borehole[pos] == Borehole[pos+1] and Type[pos] == Type[pos+1] and Date[pos] == Date[pos+1]:
				#This checks for the next borehole id. If it is the same as the current one, add the values at the current index to a tmp array.
				#We also want things from a different test to be split out, so that they do not get graphed together.
				#print "Adding values to tmpX, tmpY"
				tmpX.insert(i, Reading[pos])
				tmpY.insert(i, Depth[pos])
		elif Borehole[pos] != Borehole[pos+1]:
			print "New borehole located"
			Set = Set + 1
			i,Graphing = 0,0
			#Add the tmp (sub)lists to the list of variables to be graphed.
			X.append(tmpX)
			Y.append(tmpY)
			#We also want to have a list of unique borehole numbers, farm names, and owners.
			#These are added here, rather than by creating a new set because there is no guarantee that they are sorted in any sensible way.
			AppendSet( pos, BHList, FarmList, OwnerList, East, South, BHElev, BHWaterLev, TestDate, Set,
			 TestType, Borehole, FarmName, OwnerName, Lat, Long, Elev, WaterLev, Date, Depth, Reading, Type )
			'''BHList.append(Borehole[pos])
			FarmList.append(FarmName[pos])
			OwnerList.append(OwnerName[pos])
			South.append(Lat[pos])
			East.append(Long[pos])
			BHElev.append(Elev[pos])
			BHWaterLev.append(WaterLev[pos])
			TestDate.append(Date[pos])
			TestType.append(Type[pos])
			if Graphing == 1:
				GraphDone.append('1')
			else:
				GraphDone.append('0')
			#Reinitialise the tmp lists for the new set.'''
			tmpX,tmpY = [],[]	#Clear the placeholders.
		elif Type[pos] != Type[pos+1]:
			print "New test located"
			#If the next test type, then we need to create a new set, so that we can carry on listing. Need to keep the same farm details though.
			Set = Set + 1
			i,Graphing = 0,0
			#Add the tmp (sub)lists to the list of variables to be graphed.
			X.append(tmpX)
			Y.append(tmpY)
			#We also want to have a list of unique borehole numbers, farm names, and owners.
			#These are added here, rather than by creating a new set because there is no guarantee that they are sorted in any sensible way.
			AppendSet( pos, BHList, FarmList, OwnerList, East, South, BHElev, BHWaterLev, TestDate, Set,
			TestType, Borehole, FarmName, OwnerName, Lat, Long, Elev, WaterLev, Date, Depth, Reading, Type )

			#Reinitialise the tmp lists for the new set.
			tmpX,tmpY = [],[]
		elif Date[pos] != Date[pos+1]:
			print "New testing date"
			Set = Set + 1
			i=0
			#Add the tmp (sub)lists to the list of variables to be graphed.
			X.append(tmpX)
			Y.append(tmpY)
			#We also want to have a list of unique borehole numbers, farm names, and owners.
			#These are added here, rather than by creating a new set because there is no guarantee that they are sorted in any sensible way.
			AppendSet( pos, BHList, FarmList, OwnerList, East, South, BHElev, BHWaterLev, TestDate, Set,
			TestType, Borehole, FarmName, OwnerName, Lat, Long, Elev, WaterLev, Date, Depth, Reading, Type )

			#Reinitialise the tmp lists for the new set.
			tmpX,tmpY = [],[]
		else:
			print "not in loop"
	#print 'Finished splitting data. ' + str(pos) + ' readings processed.'
	return [X, Y, BHList, FarmList, OwnerList, East, South, BHElev, BHWaterLev, TestDate, Set, TestType, GraphDone]

def AppendSet( Position, BHList, FarmList, OwnerList, East, South, BHElev, BHWaterLev, TestDate, Set, TestType,
 Borehole, FarmName, OwnerName, Lat, Long, Elev, WaterLev, Date, Depth, Reading, Type ):
	#Borehole, FarmName, OwnerName, Lat, Long, Elev, WaterLev, Date, Depth, Reading, Type = data[:]
	pos = Position
	BHList.append(Borehole[pos])
	FarmList.append(FarmName[pos])
	OwnerList.append(OwnerName[pos])
	South.append(Lat[pos])
	East.append(Long[pos])
	BHElev.append(Elev[pos])
	BHWaterLev.append(WaterLev[pos])
	TestDate.append(Date[pos])
	TestType.append(Type[pos])
	return BHList, FarmList, OwnerList, East, South, BHElev, BHWaterLev, TestDate, Set, TestType

#We have now created a number of lists of sublists. These are as follows:
#X = [[borehole 1 Readings], [borehole 2 Readings], [borehole 3 Readings], ... , [borehole n Readings]]
#Y = [[borehole 1 Depths], [borehole 2 Depths], [borehole 3 Depths], ... , [borehole n Depths]]
#BHList = [borehole 1 number, borehole 2 number, borehole 3 number, ... , borehole n number]
#FarmList = [borehole 1 FarmName, borehole 2 FarmName, borehole 3 FarmName, ... , borehole n FarmName]
#OwnerList = [borehole 1 OwnerName, borehole 2 OwnerName, borehole 3 OwnerName, ... , borehole n Ownername]

def CreateMarkers(data, overwrite = False, suffix='', *args, **kwargs):
	'''This takes a heavily-nested list of lists.
	These are written to a text string which is appended to a locations.js file which can be handled by leaflet.'''
	#Set a number of arrays up using the data provided.
	X, Y, BHList, FarmList, OwnerList, East, South, BHElev, BHWaterLev, TestDate, Set, Type, GraphDone = data[:]
	with open("locations.js", "wt") as out_file:	#This will clear the existing locations.js file.
		out_file.write( "" )
	if overwrite:
		print 'Overwrite set, clearing existing html files.'
		for i in range(Set):
			with open("../text/" + BHList[i] + ".html", "wt") as out_file:	#This will clear the existing html file.
				out_file.write( "" )
	for i in range(Set):
		suffix = Type[i]
		print 'Generating location marker of ' + BHList[i] + ' (' + str(i+1) + ' of ' + str(Set) + ')'
		location = str(round(South[i],5)) + ',' + str(round(East[i],5))	#Generate the string that leaflet expects for co-ordinates
		'''This is the text that will be displayed on the pop-up box of the marker:
		"Borehole: <ID>
		Farm: <FarmName>
		Owner: <OwnerName>
		Elevation: <Elev>
		Water Level: <WaterLev>
		Date Visited: <TestDate>"

		If photos and graphs are available, this will be made apparent.'''
		# Set the path to potential photos, graphs and html files.
		photoPath = '../photos/' + BHList[i]
		graphPath = '../graphs/' + BHList[i] + '_' + suffix + '_' + str(TestDate[i]) + '.png'
		htmlPath = '../text/' + BHList[i] + '.html'

		text = "<em>Borehole:</em> " + BHList[i] + "</br><em>Farm:</em> " + FarmList[i] + "</br><em>Owner:</em> " + OwnerList[i] + \
		"</br><em>Elevation:</em> " + str(BHElev[i]) + "</br><em>Water Level:</em> " + str(BHWaterLev[i]) + \
		"</br><em>Date Visited:</em> " + str(TestDate[i]) + '</br><a href="../text/' + BHList[i] +\
		'.html" target="_blank">Click for further information, such as graphs.</html>'
		#we also need to create the html version, which is a separate page.
		#This section of text will be shown in all cases:
		htmlText = "<em>Borehole:</em> " + BHList[i] + "</br>\n<em>Farm:</em> " + FarmList[i] + "</br>\n<em>Owner:</em> " + OwnerList[i] + \
		"</br>\n<em>Elevation:</em> " + str(BHElev[i]) + "</br>"

		#Now, we want to distinguish between a few cases:
		#Either there is an existing graph or not. There may also be an existing html file or not.

		#First we deal with a case of an existing graph, but no html file.
		if not os.path.exists( htmlPath ) and os.path.exists( graphPath ) :
			#print "New file, existing graph."
			htmlText = htmlText + "</br>\n<em>Date Visited:</em> " + str(TestDate[i]) + \
			"</br>\n<em>Water Level:</em> " + str(BHWaterLev[i]) + \
			'</br>\n\n<img src="../graphs/' + BHList[i] + '_' + suffix + '_' + str(TestDate[i]) + '.png" width=50%></img></br>'
		#Or, if we have an existing html file, then we have the farm data already, so we only need to write anything new to it.
		#This new stuff is the stuff that relates to a particular graph.
		if os.path.exists( htmlPath ) and os.path.exists( graphPath ) : #The file exists, and we have a new graph.
			#print "Existing file, existing graph."
			htmlText = "</br>\n<em>Date Visited:</em> " + str(TestDate[i]) + \
			"</br>\n<em>Water Level:</em> " + str(BHWaterLev[i]) + \
			'</br>\n\n<img src="../graphs/' + BHList[i] + '_' + suffix + '_' + str(TestDate[i]) + '.png" width=50%></img></br>'
		#The graph is not present, but we do have a file. (Maybe we only have a surface reading?)
		if not os.path.exists ( graphPath ) and os.path.exists( htmlPath ):
			#print "Existing file, new graph."
			htmlText = "</br>\n<em>Date Visited:</em> " + str(TestDate[i]) + \
			"</br>\n<em>Water Level:</em> " + str(BHWaterLev[i]) + "<br/>"
		#Nothing is present, so we want to include everything.
		if not os.path.exists ( graphPath ) and not os.path.exists( htmlPath ):
			#print "New file, no graph."
			htmlText = htmlText + "</br>\n<em>Date Visited:</em> " + str(TestDate[i]) + \
			"</br>\n<em>Water Level:</em> " + str(BHWaterLev[i]) + "<br/>"

		#And now we want a link to the photos, which will be added to the start, but only if the file does not already exist.
		#The assumption is that they already have been included. If false, just delete and rerun on all the data.
		if os.path.exists( photoPath ) and not os.path.exists ( htmlPath ): #Put a link to the photos on the marker pop-up and the page.
			htmlText = htmlText + '\n\n</br><a href="../photos/' + BHList[i] + '">Photos available.</a>'
			text = text + '</br><a href="../photos/' + BHList[i] + '" target="_blank">Photos available.</a>'


		#This adds the bits of javascript wrapping needed for the above string to create a marker object in leaflet.
		PopupTemplate = "var " + BHList[i] + " = L.popup({maxWidth:600, maxHeight:600}).setContent('" + text + "')\n\n"
		MarkerTemplate = "L.marker([" + location + "],{riseOnHover: true,title:'" + BHList[i] + \
		"', opacity:0.5})\n\t.addTo(map)\n\t.bindPopup(" + BHList[i] + ")\n\n"

		#Append the whole construct to the location.js file that leaflet is expecting.
		with open("locations.js", "at") as out_file:
			out_file.write( PopupTemplate )
			out_file.write( MarkerTemplate )

		if os.path.exists( htmlPath ): #This will append, since the file exists.
			with open("../text/" + BHList[i] + ".html", "at") as out_file:
				out_file.write( htmlText )
		else:
			with open("../text/" + BHList[i] + ".html", "wt") as out_file:
				out_file.write( htmlText )
		#htmlText,text = '',''
	print 'All markers written.'

def CreateGraphs(data, XName, YName, All = 0, suffix = '', *args, **kwargs):
	'''In order to plot the graphs, we take the whole dataset, along with what we want to have on the X and Y axis.
 
     If there is a test-type given, it will be used as a suffix on the file name, as well as '''
	#unpack data list.
	X, Y, BHList, FarmList, OwnerList, East, South, BHElev, BHWaterLev, TestDate, Set, Type, Graphs = data[:]
	'''
	Possibly a useful debug feature:
	print BHList
	print FarmList
	print OwnerList
	print Type
	'''
	for i in range (Set):
		print "Processing " + Type[i] + " test"
		suffix = Type[i]
		if X[i] != []:
			#if X[i] != []:
			mpl.pyplot.close()
			mpl.pyplot.plot(X[i], Y[i])
			#Title comprises Borehole name, FarmName and OwnerName
			mpl.pyplot.title( suffix + ' test in ' + BHList[i] + '\n' + FarmList[i] + ' (' + OwnerList[i] + ')' )
			print 'Generating graph of ' + BHList[i] + ' [ ' + BHList[i] + '_' + suffix + '.png ] (' + str(i+1) + ' of ' + str(Set) + ')'
			if Type[i] == 'EC':
				XName = 'mS/s'
			elif Type[i] == 'G-G':
				XName = 'n'
			else:
				XName = 'Unknown Units'
			mpl.pyplot.xlabel(XName)
			mpl.pyplot.ylabel(YName)
			mpl.pyplot.savefig('../graphs/' + BHList[i] + '_' + suffix + '_' + str(TestDate[i]) + '.png', dpi=200)
		else:
			print 'No graphable values for ' + BHList[i] + ' [ ' + BHList[i] + '_' + suffix + '.png ] (' + str(i+1) + ' of ' + str(Set) + ')'
	print 'All graphs generated.'

	if All == 1:
		#We then run through it again and create a graph with all the graphs plotted on the same axis.
		for i in range (Set):
			mpl.pyplot.plot(X[i], Y[i], label=BHList[i])
			mpl.pyplot.title('All boreholes')
			print 'Generating graph of all Boreholes: ' + str(i+1) + ' of ' + str(Set)
			mpl.pyplot.xlabel('mS/m')
			mpl.pyplot.ylabel('Depth below surface (m)')
			mpl.pyplot.savefig('../graphs/' + 'all.png', dpi=200)

if __name__ == "__main__":
	data = ImportCSV(sys.argv[1])
else:
	data = ImportCSV('c:\Users\s214382818\Desktop\hydro census\scripts\\test_data.csv')
split_data = SplitCSV(data)
Processed_Data = CreateSublists(split_data)
print str(Processed_Data[10]) + ' datasets.'
CreateGraphs(Processed_Data, 'mS/m', 'Depth below surface (m)', 1, "EC")
CreateMarkers(Processed_Data)
#print split_data

print 'Complete. Load index.html in a web browser to view the information.'
