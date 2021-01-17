import folium
from folium.plugins import FloatImage
import pandas as pd


def adjust_str(string):
    # handling the online database's string flaws
    if string in ["","nan"]:
        return ""
    while string[0] in ' .,':
        string=string[1:]
    return string.replace('‡','<br>').replace('.','<br>').replace(',','<br>')

def add_to_fg(fg, lt, ln, name, dfee, nfee, comm, color, icon):
    """
    created a folium marker and adds to the Frame Group
    inputs:
    fg - Frame Group
    lt, ln, name, dfee, nfee, comm - characteristics of the parking lot
    color, icon - according to the discount
    """
    html=html_base % (lt, ln, name)
    temp=adjust_str(str(dfee))
    if temp!="":
        html+=html_day % (temp)
    temp=adjust_str(str(nfee))
    if temp!="":
        html+=html_night % (temp)
    temp=adjust_str(str(comm))
    if temp!="":
        html+=html_comment % (temp)
    iframe = folium.IFrame(html=html, width=300, height=200)
    fg.add_child(folium.Marker(location=(lt,ln),icon=folium.Icon(color=color,prefix='fa',icon=icon),popup=folium.Popup(iframe)))

url = 'https://api.tel-aviv.gov.il'
parking = f'{url}/parking/stations'
df = pd.read_excel('parks.xlsx')

m=folium.Map(location=[32.081220, 34.775343], zoom_start=13, tiles = None)
folium.TileLayer("Stamen Terrain", name="Tel-Aviv").add_to(m)

# html parts of the marker popup
html_base="""<a href="waze://?ll=%s,%s&navigate=yes"><img src="https://github.com/iRusek/ParkInTLV/blob/main/images/wazeicon.jpg?raw=true" height="30" width="30" align='left'></a><h2 align='right' style='font-family:david'>%s</h2>
"""
html_day="""<h4 style="font-family:david;margin:10" align='right'>מחיר לשעות היום</h4>
<p style='font-family:david;margin:10' dir="ltr" align='right'>%s</p>"""
html_night="""<h4 style='font-family:david;margin:10' align='right'>מחיר לשעות הערב</h4>
<p style='font-family:david;margin:10' dir="ltr" align='right'>%s</p>"""
html_comment="""<h4 style='font-family:david;margin:10' align='right'>הערות</h4>
<p style='font-family:david;margin:10' dir="ltr" align='right'>%s</p>"""

free="ללא תשלום"
discount="בחניון זה ניתנת הנחת תושב"
fg_discount=folium.FeatureGroup(name="חניונים בהנחה לתושבים")
fg_none=folium.FeatureGroup(name="חניונים בתשלום מלא")

# start adding parking lots to the Frame Groups
for lt,ln,name,dfee,nfee,comm in zip(df['GPSLattitude'],df['GPSLongitude'],df['Name'],df['DaytimeFee'],df['NighttimeFee'],df['FeeComments']):
    if free in str(dfee):
        # free parking
        add_to_fg(fg_discount, lt, ln, name, dfee, nfee, comm, "lightgreen", "star")
    elif str(comm)=='nan':
        # no comment at all
        add_to_fg(fg_none, lt, ln, name, dfee, nfee, "", "orange", "shekel")
    elif discount not in comm:
        # comment without discount
        add_to_fg(fg_none, lt, ln, name, dfee, nfee, comm, "orange", "shekel")
    elif '75' in comm:
        # comment with discount 75%
        add_to_fg(fg_discount, lt, ln, name, dfee, nfee, comm, "green", "star-half-o")
    elif '50' in comm:
        # comment with discount 50%
        add_to_fg(fg_discount, lt, ln, name, dfee, nfee, comm, "darkgreen", "star-o")

m.add_child(fg_discount)
m.add_child(fg_none)
m.add_child(folium.LayerControl())
# add the legend
folium.plugins.FloatImage('https://github.com/iRusek/ParkInTLV/blob/main/images/legend.png?raw=true',bottom=10, left=1).add_to(m)

m.save("ParkInTLV1.html")