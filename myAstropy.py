"""
Astropy Library
V1.010
20.04.2024 
"""

# Importiere die benötigten Module von astropy 
from astropy import units as u 
from astropy.coordinates import EarthLocation, SkyCoord, solar_system_ephemeris, AltAz
from astropy.coordinates import get_moon 
from astropy.coordinates import get_sun
from astropy.coordinates import get_body  
from astropy.time import Time 

# import other modules
from datetime import datetime

# include own libraries
import myMainVars



def getTimeFromDbl(value, type=None):
    """
    calculates a double variable in Hours, Min, Seconds
    returns stunden, minuten, sekunden, and HMS_Text
    type = HMS => es wird ein Text HH:MM:SS zurückgegeben
    type = DEG => es wird ein Text NN°MM'SS'' zurückgegeben
    """

    # korrigiere negative Werte, denn sonst werden Stunden, Minuten und Sekunden mit einem führenden Minuszeichen versehen
    negative = False
    if value < 0:
        negative = True
        value = abs(value)

    # Umwandlung in Stunden, Minuten und Sekunden
    stunden = int(value)
    minuten = int((value - stunden) * 60)
    sekunden = (value - stunden - minuten/60) * 3600

    # korrigiere die Stunden, wenn der Wert negativ war
    if negative == True:
        stunden = stunden * (-1)

    # and make a string out of it
    # HMSString = "RA-Wert: {ra} Stunden = {stunden} Stunden, {minuten} Minuten und {sekunden:.2f} Sekunden"
    if type == "HMS":
        HMSString = "{:02.0f}".format(stunden) + ":" + "{:02.0f}".format(minuten) + ":" + "{:02.0f}".format(sekunden)
    if type == "DEG":
        HMSString = "{:02.0f}".format(stunden) + "°" + "{:02.0f}".format(minuten) + "'" + "{:02.0f}".format(sekunden) + "''"    

    return stunden, minuten, sekunden, HMSString


def GetDblFromTime(zeit):
        """
        calculates a double variable from a given time
        input zeit = "17:13:44"
        output double = 17,22888888888
        """
        # Dieser Code gibt einen Double-Wert zurück, der die Stunden als Ganzzahl und die Minuten und Sekunden 
        # als Dezimalzahl darstellt. Zum Beispiel repräsentiert 12:30:00 zwölf und ein halb Stunden, 
        # daher gibt die Funktion 12.5 zurück
        stunden, minuten, sekunden = map(int, zeit.split(':'))
        minuten_sekunden = minuten * 60 + sekunden
        return stunden + minuten_sekunden / 3600.0


class AstropyObject():
    """
    initiates an Astropy Object
    myLocation = Location of observer
    myDateTime = Date and Time to watch a Skyobject
    mySkyObject = Skyobject to be watched
    """

    myLocation = None
    myDateTime = None
    mySkyObject = None


    def __init__(self):
        super().__init__()


    def setLocation(self, tmpKoordinaten):
        """
        sets a specific observation location, e. g. Stuttgart
        """
        self.myLocation = EarthLocation(lat=tmpKoordinaten['latitude']*u.deg, lon=tmpKoordinaten['longitude']*u.deg, height=tmpKoordinaten['elevation']*u.m)


    def setTime(self, tmpDateTime: datetime):
        """
        sets a specific observation Date and Time
        parameter: "2024-03-29 18:29:00"
        """
        # Format "2024-02-25 12:55:00"
        tmpText = tmpDateTime.strftime("%Y-%m-%d %H:%M:%S")
        # print(f"TIME{tmpText}")
        self.myDateTime = Time(tmpText)


    def setSkyObject(self, tmpSkyObject):
        """
        sets a specific sky object to be observed
        parameter: "polaris"
        """
        # within astropy for stars and planets there are different function calls
        # this method hides this complexity within this Class, i. e. an external call may just give the name

        # our solar system
        if tmpSkyObject['value'] == 1:
            self.setPlanetPos(tmpSkyObject['astropy'])    

        # moon of the earth
        if tmpSkyObject['value'] == 2:
            self.setPlanetPos(tmpSkyObject['astropy']) 

        # stars and galaxies               
        if tmpSkyObject['value'] == 0:
            self.setStarPos(tmpSkyObject['astropy']) 


    def calcAstrometricPosition(self):
        """
        CHECK  NECESSITY
        """
        # Setzen Sie das Ephemeris auf 'builtin'
        with solar_system_ephemeris.set('builtin'):
            # Holen Sie die Position der Erde zu diesem Zeitpunkt
            erde_position = get_body('earth', self.myDateTime)

            # Holen Sie die Position der Sonne zu diesem Zeitpunkt
            print(self.mytmpName)

            sonne_position = get_body(self.mytmpName, self.myDateTime)

            # Berechnen Sie die Entfernung zwischen Erde und Sonne
            entfernung = erde_position.separation_3d(sonne_position)

            print(f"Die Entfernung zwischen Erde und Objekt am {self.myDateTime.to_datetime()} ist {entfernung:.2f}")

        return entfernung


    def getRaDec_HMS(self):
        # Ausgabe der Rektaszension HH:MM:SS und Deklination in DG:MM:SS
        # Konvertieren Sie die Koordinaten in Grad
        ra = self.mySkyObject.ra 
        dec = self.mySkyObject.dec

        # Zeige die Ergebnisse an
        ra_HMS = ra.to_string(unit=u.hour, sep=':', pad=True, precision=0)
        dec_HMS = dec.to_string(sep=':', pad=True, precision=0)
        # print(f"Die Rektaszension des Objekts ist {ra_HMS}") 
        # print(f"Die Deklination des Objekts ist {dec_HMS}") 

        return ra_HMS, dec_HMS, 0 # 0 for distance
    

    def getRaDec_DEG(self):
        # Ausgabe der Rektaszension in DEG:MM:SS und Deklination in DEG:MM:SS
        # Konvertieren Sie die Koordinaten in Grad
        ra = self.mySkyObject.ra 
        dec = self.mySkyObject.dec

        # Zeige die Ergebnisse an
        # print(f"Die Rektaszension des Objekts ist {ra}") 
        # print(f"Die Deklination des Objekts ist {dec}") 

        return ra, dec, 0 # 0 for distance
      
   
    def getAltAz(self):

        # Standort muss definiert worden sein 
        
        # zeitpunkt muss definiert worden sein

        # Koordinaten des Skyobjects muss definiert worden sein

        # Umwandlung in Altitude und Azimut
        altaz = AltAz(obstime=self.myDateTime, location=self.myLocation)
        mySkyObject_altaz = self.mySkyObject.transform_to(altaz)

        # Berechne die Altitude und den Azimut des Saturn 
        altitude = mySkyObject_altaz.alt
        azimuth = mySkyObject_altaz.az 

        # Zeige die Ergebnisse an 
        # print(f"getAltAz: Die Altitude des Objekts ist {altitude:.2f}") 
        # print(f"getAltAz: Der Azimut des Objekts ist {azimuth:.2f}") 

        return altitude, azimuth, 0 # for distance
    

    def setMoonPos(self):
        # Standort muss definiert worden sein 
        
        # zeitpunkt muss definiert worden sein

        # Koordinaten des Mondes zu diesem Zeitpunkt
        self.mySkyObject = get_moon(self.myDateTime, self.myLocation)

    
    def setSunPos(self):
        # Standort muss definiert worden sein 
        
        # zeitpunkt muss definiert worden sein

        # definiere Objekt
        self.mySkyObject = get_sun(self.myDateTime, self.myLocation)

  
    def setPlanetPos(self, myPlanet):
        # myPlanet =  'moon', 'jupiter', 'saturn', 'venus', 'mars', 'uranus', 'sun'

        # Standort muss definiert worden sein 
        
        # zeitpunkt muss definiert worden sein

        # definiere Planet
        self.mySkyObject = get_body(myPlanet, self.myDateTime, self.myLocation)


    def setStarPos(self, myStar):
        # Standort muss definiert worden sein 
        
        # zeitpunkt muss definiert worden sein

        # Koordinaten Stern / Galaxie
        # andromeda = SkyCoord('00h42m44.3s', '+41d16m9s', frame='icrs')
        # Die Astropy-Bibliothek verwendet das ICRS (Internationales Himmelsreferenzsystem), das auf dem J2000-Äquinoktium basiert.
        self.mySkyObject = SkyCoord.from_name(myStar)


def main():

    myObj = AstropyObject()

    # 1.) Definiere den Standort Stuttgart
    myObj.setLocation(myMainVars.cities['Stuttgart']) 

    # 2.) Definiere lokale Zeit
    # MAN MUSS EINE STUNDE ABZIEHEN => GREENWICH HAT -1H => DANN SCHEINEN DIE WERTE ZU PASSEN
    mySkyDate = '2024-03-29 18:29:00'
    datum_zeit_obj = datetime.strptime(mySkyDate, "%Y-%m-%d %H:%M:%S")
    print (datum_zeit_obj)
    myObj.setTime(datum_zeit_obj)

    # 3.) definiere das Himmelsobjekt
    # myObj.setPlanetPos('sun') # nur für Testzwecke  'moon', 'jupiter', 'saturn', 'venus', 'mars', 'uranus', 'sun'
    myObj.setStarPos('Vega') # nur für Testzwecke  'M31', 'Vega'
    
    ra, dec, distance = myObj.getRaDec_HMS()
    print(f"Die Rektaszension des Objekts ist {ra}") 
    print(f"Die Deklination des Objekts ist {dec}") 

    altitude, azimuth, distance = myObj.getAltAz()
    print(f"getAltAz: Die Altitude des Objekts ist {altitude:.2f}") 
    print(f"getAltAz: Der Azimut des Objekts ist {azimuth:.2f}") 


if __name__ == '__main__':
    main()