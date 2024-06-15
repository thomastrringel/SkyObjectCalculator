"""
SkyObject Tab using Astropy
generates a window using PyQT5 to select location & skyobject
it will calculate RA, DEC, ALT, AZ of the Sky Object

V1.1.00
2024/June/15

Can be started as standalone - Standalone only implemented for testing purposes

"""

# py -m pip install pyqt5-tools
# .venv\Lib\site-packages\qt5_applications\Qt\bin\designer.exe   
# https://realpython.com/qt-designer-python/ 
# https://doc.qt.io/qt-6/qtdesigner-manual.html

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.uic import loadUi
from datetime import datetime

# für Zeitzonen => wir müssen offenbar mit Greenwich TimeZone rechnen
import pytz # py -m pip install pytz

# include libraries for postion calculation of skyobjects
# we will focus in Astropy - other ones are prepared but not yet tested fully
# import mySkyfield
# import myEphem
import myAstropy


# define some relevant cities as a dictionary
# Ein Dictionary ist eine ungeordnete Sammlung von Datenwerten, die als Schlüssel-Wert-Paare verwendet werden. Hier ist jedes Element durch einen Schlüssel repräsentiert, der eindeutig sein muss.
# cities ist ein Dictionary, bei dem jeder Schlüssel (wie ‘noLocation’, ‘Stuttgart’, ‘Botnang’) ein weiteres Dictionary ist, das ‘latitude’, ‘longitude’ und ‘elevation’ als Schlüssel hat.
cities = {
    'noLocation': {'latitude': 0.0000, 'longitude': 0.0000, 'elevation': 0},
    'Stuttgart': {'latitude': 48.7758459, 'longitude': 9.1829321, 'elevation': 150},
    'Botnang': {'latitude': 48.780497, 'longitude': 9.128687, 'elevation': 350}
}



# define some relevant skyobjects as a dictionary. 
# each object has a 
#    TrackingRate and value definition. This is used to send the information to the mount on how to track the Skyobject
#    Skyobject names on how to calculate positions with different libraries:
#       Skyfield uses DE421
#       Ephem uses Barycenters
#       Astropy uses names
#
# dictionary is prepared to use different libraries but Astropy is implemented only
# 
# https://rhodesmill.org/skyfield/planets.html DE421 Database
skyobjects = {
    'noObject': {'TrackingRate': 'NaN', 'value': 99}, 
    'sun': {'TrackingRate': 'solar', 'value': 1, 'DE421': 'SUN', 'ephem': 'sun', 'astropy': 'sun'},   
    'mars': {'TrackingRate': 'solar', 'value': 1, 'DE421': 'MARS BARYCENTER', 'ephem': 'mars', 'astropy': 'mars'},
    'jupiter': {'TrackingRate': 'solar', 'value': 1, 'DE421': 'JUPITER BARYCENTER', 'ephem': 'Jupiter', 'astropy': 'jupiter'},
    'saturn': {'TrackingRate': 'solar', 'value': 1, 'DE421': 'SATURN BARYCENTER', 'ephem': 'saturn', 'astropy': 'saturn'},
    'uranus': {'TrackingRate': 'solar', 'value': 1, 'DE421': 'URANUS BARYCENTER', 'ephem': 'uranus', 'astropy': 'uranus'},
    'moon': {'TrackingRate': 'lunar', 'value': 2, 'DE421': 'MOON', 'ephem': 'moon', 'astropy': 'moon'},
    'andromeda': {'TrackingRate': 'sidereal', 'value': 0, 'DE421': 'M31', 'ephem': 'M31', 'astropy': 'M31'},
    'alpha centaurus': {'TrackingRate': 'sidereal', 'value': 0, 'DE421': 'Alpha Centauri', 'ephem': 'Alpha Centauri', 'astropy': 'Alpha Centauri'}, 
    'antares': {'TrackingRate': 'sidereal', 'value': 0, 'DE421': 'Antares', 'ephem': 'Antares', 'astropy': 'Antares'},
    'arktur': {'TrackingRate': 'sidereal', 'value': 0, 'DE421': 'Arcturus', 'ephem': 'Arcturus', 'astropy': 'Arcturus'},
    'beteigeuze': {'TrackingRate': 'sidereal', 'value': 0, 'DE421': 'Betelgeuse', 'ephem': 'Betelgeuse', 'astropy': 'Betelgeuse'},
    'capella': {'TrackingRate': 'sidereal', 'value': 0, 'DE421': 'Capella', 'ephem': 'Capella', 'astropy': 'Capella'},
    'deneb': {'TrackingRate': 'sidereal', 'value': 0, 'DE421': 'Deneb', 'ephem': 'Deneb', 'astropy': 'Deneb'},
    'dubhe': {'TrackingRate': 'sidereal', 'value': 0, 'DE421': 'Dubhe', 'ephem': 'Dubhe', 'astropy': 'Dubhe'},
    'polaris': {'TrackingRate': 'sidereal', 'value': 0, 'DE421': 'Polaris', 'ephem': 'Polaris', 'astropy': 'Polaris'},
    'pollux': {'TrackingRate': 'sidereal', 'value': 0, 'DE421': 'Pollux', 'ephem': 'Pollux', 'astropy': 'Pollux'},
    'regulus': {'TrackingRate': 'sidereal', 'value': 0, 'DE421': 'Regulus', 'ephem': 'Regulus', 'astropy': 'Regulus'},
    'rigel': {'TrackingRate': 'sidereal', 'value': 0, 'DE421': 'Rigel', 'ephem': 'Rigel', 'astropy': 'Rigel'},
    'sirius': {'TrackingRate': 'sidereal', 'value': 0, 'DE421': 'Sirius', 'ephem': 'Sirius', 'astropy': 'Sirius'},
    'spica': {'TrackingRate': 'sidereal', 'value': 0, 'DE421': 'Spica', 'ephem': 'Spica', 'astropy': 'Spica'},
    'vega': {'TrackingRate': 'sidereal', 'value': 0, 'DE421': 'Vega', 'ephem': 'Vega', 'astropy': 'Vega'},

}



class TabContentSkyObject(QWidget, object):

    """
    Tab SkyObject Calculations with Astropy
    """

    mco = None # Main Object for exchange data between objects

    # Main Object for exchange data between objects
    # myMainObject = None

    nowDateTime = datetime
    nowLocation = 'NaN'
    nowSkyObject = 'NaN'
    ra = None
    dec = None
    alt = None
    az = None
    nowLibName = "astropy" # 'ephem' 'skyfield' => Change Code in on_cboSkyObject_changed 
    nowLibSkyObjectName = 'NaN' # depending on library different names are required "JUPITER BARYCENTER" or "jupiter"
    greenwich = None # greenwich time will be stored automatically depending on local time


    def __init__(self, myCommunicationObject):
        super().__init__()

        if myCommunicationObject == None:
            print("SINGLE START NO DEBUGGING")              
        else:            
            self.mco = myCommunicationObject

        loadUi("TAB_Settings.ui", self)

        # load data for cities in cboLocation
        for stadt, koordinaten in cities.items():
            print(f"loading city {stadt} hat die Koordinaten {koordinaten['latitude']}, {koordinaten['longitude']}")
            self.cboLocation.addItem(stadt)

        # load data for skyobjects in cboSkyObjects
        for skyobj, tracking in skyobjects.items():
            print(f"loading skyObject {skyobj} with {tracking['TrackingRate']}, {tracking['value']}")
            self.cboSkyObjects.addItem(skyobj)

        # connect functionalities
        # self.pushButton.clicked.connect(self.GiveInfo)
        self.cboLocation.currentIndexChanged.connect(self.on_cboLocation_changed)
        self.cboSkyObjects.currentIndexChanged.connect(self.on_cboSkyObject_changed)

        #start timer for clock
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)

        # # Erstellen Sie ein timezone-Objekt für Greenwich
        self.greenwich = pytz.timezone('Greenwich')


    def on_cboLocation_changed(self):
        # get selected city
        selected_city = self.cboLocation.currentText()
        self.nowLocation = selected_city
        # get coordinates of cities
        coords = cities[selected_city]
        text_longitude = str(coords['longitude'])
        text_latitude = str(coords['latitude'])

        # show data
        self.lcd_longitude.display(text_longitude)
        self.lcd_latitude.display(text_latitude)


    def on_cboSkyObject_changed(self):

        # get selected SkyObject
        selectedSkyObject = self.cboSkyObjects.currentText()
        # get DE421 Data
        self.nowLibSkyObjectName = skyobjects[selectedSkyObject]

        myObj = myAstropy.AstropyObject() # für myAstropy        
        # myObj = mySkyfield.SkyfieldObject()
        # myObj = myEphem.EphemObject() # für Ephem

        # datum_zeit_obj = datetime.strptime(self.nowDateTime, "%Y-%m-%d %H:%M:%S")
        myObj.setLocation(cities[self.nowLocation])
        myObj.setTime(datetime.now(self.greenwich)) 
        myObj.setSkyObject(self.nowLibSkyObjectName)

        ra, dec, distance = myObj.getRaDec_HMS()
        self.ra = ra
        self.dec = dec
        alt, az, distance = myObj.getAltAz()

        f_alt = "{:.2f}".format(alt)
        self.tedAltitude.setText(f_alt)

        f_az = "{:.2f}".format(az)
        self.tedAzimut.setText(f_az)

        # RA und DEC sind bereits Texte
        self.tedRektaszension.setText(ra)
        self.tedDeklination.setText(dec)

        # self.lcdRektaszension.display(str(ra))
        # self.lcdDeklination.display(str(dec))

        # self.lcdAltitude.display(str(alt))
        # self.lcdAzimut.display(str(az))

        self.lcdDistance.display(str(distance))

        if alt > 0:   # .degrees für Skyfield ? warum => ist altitude nicht der Winkel?
            self.lblAboveHorizon.setStyleSheet("background-color: green;")
        else:
             self.lblAboveHorizon.setStyleSheet("background-color: red;")               


    def GiveInfo(self):
        print ("BUTTON GEDRÜCKT")


    def showTime(self):
        # self.nowDateTime = datetime.now()

        nowTime = datetime.now(self.greenwich).strftime("%H:%M:%S") # save time
        self.lcd_time.display(nowTime)

        nowDate = datetime.now(self.greenwich).strftime("%Y-%m-%d") # save date
        self.lcd_date.display(nowDate)


def main():
    app = QApplication([])
    window = TabContentSkyObject(None)
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()


