# NC Commerce Prosperity Zones (https://www.commerce.nc.gov/about-us/nc-prosperity-zones), 100 counties.
# Broad region grouping (Mountains / Piedmont / Coastal Plain) is this analysis's own roll-up of the zones.
ZONES = {
 "Western": "Buncombe Cherokee Clay Graham Haywood Henderson Jackson Macon Madison Polk Rutherford Swain Transylvania",
 "Northwest": "Alexander Alleghany Ashe Avery Burke Caldwell Catawba McDowell Mitchell Watauga Wilkes Yancey",
 "Southwest": "Anson Cabarrus Cleveland Gaston Iredell Lincoln Mecklenburg Rowan Stanly Union",
 "Piedmont-Triad": "Alamance Caswell Davidson Davie Forsyth Guilford Randolph Rockingham Stokes Surry Yadkin",
 "North Central": "Chatham Durham Edgecombe Franklin Granville Harnett Johnston Lee Nash Orange Person Vance Wake Warren Wilson",
 "Sandhills": "Bladen Columbus Cumberland Hoke Montgomery Moore Richmond Robeson Sampson Scotland",
 "Northeast": "Beaufort Bertie Camden Chowan Currituck Dare Gates Halifax Hertford Hyde Martin Northampton Pasquotank Perquimans Pitt Tyrrell Washington",
 "Southeast": "Brunswick Carteret Craven Duplin Greene Jones Lenoir NewHanover Onslow Pamlico Pender Wayne",
}
BROAD = {"Western": "Mountains", "Northwest": "Mountains", "Southwest": "Piedmont", "Piedmont-Triad": "Piedmont",
         "North Central": "Piedmont", "Sandhills": "Coastal Plain", "Northeast": "Coastal Plain", "Southeast": "Coastal Plain"}
COUNTY_ZONE = {}
for z, s in ZONES.items():
    for c in s.split():
        COUNTY_ZONE["NEW HANOVER" if c == "NewHanover" else c.upper()] = z
assert len(COUNTY_ZONE) == 100
