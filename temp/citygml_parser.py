'''
author: Md Shaifur Rahman (mdsrahman@cs.stonybrook.edu)
        Stony Brook University, NY.
'''
from lxml import etree

class CityGML3DBuildingParser(object):
    '''
    Given a citygml file (.gml), this class parses the 3D building structure and save it

    '''
    def __init__(self):
        print "CityGML3DBuildingParser object created.."

        self.map_name = None
        self.input_gml_filepath = None
        self.citygml_building_namespace = None
        self.gml_namespace = "http://www.opengis.net/gml"

        self.output_building_filepath = None
        self.center_x = None
        self.center_y = None
        self.spread_x = None
        self.spread_y = None
        self.min_gml_x = float('inf')
        self.max_gml_x = -float('inf')
        self.min_gml_y = float('inf')
        self.max_gml_y = -float('inf')
        self.min_gml_z = float('inf')
        self.max_gml_z = -float('inf')

        self.max_allowed_gml_x =  float('inf')
        self.min_allowed_gml_x = -float('inf')

        self.max_allowed_gml_y =  float('inf')
        self.min_allowed_gml_y = -float('inf')

        self.max_allowed_building = float('inf')
        self.max_allowed_surface = float('inf')

        # self.max_allowed_gml_z =  float('inf')
        # self.min_allowed_gml_z = -float('inf')

        self.total_building = 0
        self.total_surface = 0

        return

    def updateMaxMinAllowedGML_XY(self):
        if      self.center_x is not None \
            and self.spread_x is not None \
            and self.center_y is not None \
            and self.spread_y is not None:
            self.max_allowed_gml_x = self.center_x + self.spread_x
            self.min_allowed_gml_x = self.center_x - self.spread_x
            self.max_allowed_gml_y = self.center_y + self.spread_y
            self.min_allowed_gml_y = self.center_y - self.spread_y
        return

    def parsePosList(self, posListText):
        X, Y, Z = [], [], []
        c = 0
        isSurfaceWithinRange = True
        posList = posListText.split()
        for value in posList:
            value = float(value)
            if c % 3 == 0:
                X.append(value)
            elif c % 3 == 1:
                Y.append(value)
            else:
                Z.append(value)
            c += 1
            if c > len(posList) - 3:
                break
        min_surf_x, min_surf_y =  min(X), min(Y)
        max_surf_x, max_surf_y =  max(X), max(Y)
        if     min_surf_x < self.min_allowed_gml_x \
            or min_surf_y < self.min_allowed_gml_y \
            or max_surf_x > self.max_allowed_gml_x \
            or max_surf_y > self.max_allowed_gml_y:
            return None
        #else do this
        return list(zip(X, Y, Z))

    def getBoundingBox(self, surfaceList, updateGlobalBoundary = False):
        surf_count = 0
        min_x = min_y = min_z =  float('inf')
        max_x = max_y = max_z = -float('inf')

        surf_count = len(surfaceList)
        for cur_surf in surfaceList:
            for x,y,z in cur_surf:
                min_x, min_y, min_z =  min(min_x, x), min(min_y, y), min(min_z, z)
                max_x, max_y, max_z =  max(max_x, x), max(max_y, y), max(max_z, z)

        if updateGlobalBoundary:
            self.max_gml_x = max( self.max_gml_x, max_x)
            self.max_gml_y = max( self.max_gml_y, max_y)
            self.max_gml_z = max( self.max_gml_z, max_z)

            self.min_gml_x = min( self.min_gml_x, min_x)
            self.min_gml_y = min( self.min_gml_y, min_y)
            self.min_gml_z = min( self.min_gml_z, min_z)

        return surf_count, min_x, max_x, min_y, max_y, min_z, max_z


    def getOutputBuildingFileText(self, surfaceList):
        surf_count, min_x, max_x, min_y, max_y, min_z, max_z = self.getBoundingBox(surfaceList, updateGlobalBoundary=True)
        self.total_building += 1
        self.total_surface += surf_count
        fileText = str(self.total_building)+', '+str(surf_count)+"\n"
        fileText = fileText+str(min_x)+', '+str(max_x)+"; "\
                           +str(min_y)+', '+str(max_y)+'; '\
                           +str(min_z)+', '+str(max_z)+'\n'

        for cur_surf in surfaceList:
            for idx, (x,y,z) in enumerate(cur_surf):
                if idx >0:
                    fileText = fileText+'; '
                fileText = fileText+str(x)+", "+str(y)+", "+str(z)
            fileText = fileText + "\n"
        return fileText


    def isObjectCountExceeded(self):
        if self.total_surface >= self.max_allowed_surface:
            return  True
        if self.total_building >= self.max_allowed_building:
            return True
        return False

    def writeStatFile(self):
        with open(self.output_building_filepath+'.stat' ,'w') as statFile:
            ftext = self.map_name+", "+str(self.total_building)+", "+str(self.total_surface)+"\n"
            ftext += str(self.min_gml_x)+", "+str(self.max_gml_x)
            ftext += '; '+ str(self.min_gml_y)+", "+str(self.max_gml_y)
            ftext += '; '+ str(self.min_gml_z)+", "+str(self.max_gml_z)
            statFile.write(ftext)
        return

    def clearIterParseElement(self, elem):
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
        return

    def iterativeParse3DBuildingData(self):
        context = etree.iterparse(self.input_gml_filepath, events=('start', 'end'))
        with open(self.output_building_filepath+'.bldg', "w") as output_bldg_file:
            for event, elem in context:
                if event == 'end' and elem.tag == "{%s}Building" % self.citygml_building_namespace:
                    isBuildingIncluded = True
                    cur_building_surface_list = []
                    for surfaceType in ['WallSurface', 'RoofSurface', 'OuterFloorSurface', 'OuterCeilingSurface', 'ClosureSurface', 'GroundSurface']:
                        xpath_str = './/{'+self.citygml_building_namespace+'}'+surfaceType
                        for wall in elem.findall(xpath_str):
                            for posList in wall.findall(".//{%s}posList" % self.gml_namespace):
                                surf_points = self.parsePosList( posList.text )
                                if surf_points is None:
                                    isBuildingIncluded = False
                                    break # no more surface list
                                else:
                                    cur_building_surface_list.append(surf_points)
                            if not isBuildingIncluded:
                                break #no more of this-type surface
                        if not isBuildingIncluded:
                            break  # no more of any-type surface
                    if isBuildingIncluded:
                        output_bldg_file.write( self.getOutputBuildingFileText(cur_building_surface_list) )
                        if self.isObjectCountExceeded():
                            break
                    self.clearIterParseElement(elem)
        self.writeStatFile()
        return

    def parse3DBuildingData(self,
                            map_name,
                            input_gml_filepath,
                            citygml_building_namespace,
                            output_building_filepath,
                            center_x=  None,
                            center_y = None,
                            spread_x = None,
                            spread_y = None,
                            max_allowed_building = None,
                            max_allowed_surface = None
                            ):
        self.map_name = map_name
        self.input_gml_filepath = input_gml_filepath
        self.citygml_building_namespace = citygml_building_namespace
        self.output_building_filepath = output_building_filepath
        self.center_x = center_x
        self.center_y = center_y
        self.spread_x = spread_x
        self.spread_y = spread_y
        self.max_allowed_building = max_allowed_building
        self.max_allowed_surface = max_allowed_surface

        self.updateMaxMinAllowedGML_XY()
        self.iterativeParse3DBuildingData()
        return

def driverCityGML3DBuildingParser():
    input_gml_filepath = "../data/DA_WISE_GMLs/DA12_3D_Buildings_Merged.gml"
    citygml_building_namespace = "http://www.opengis.net/citygml/building/1.0"
    output_building_filepath = './world_trade_center'
    center_x = 980567.517053
    center_y = 198976.869809
    spread_x = 1000
    spread_y = 1000
    max_allowed_building = 20
    max_allowed_surface = 20000

    cg3b = CityGML3DBuildingParser()
    cg3b.parse3DBuildingData(
                            map_name = 'NYC:EPSG:2263',
                            input_gml_filepath = input_gml_filepath,
                            citygml_building_namespace = citygml_building_namespace,
                            output_building_filepath = output_building_filepath,
                            center_x=  center_x,
                            center_y = center_y,
                            spread_x = spread_x,
                            spread_y = spread_y,
                            max_allowed_building=max_allowed_building,
                            max_allowed_surface=max_allowed_surface)

if __name__ == '__main__':
    driverCityGML3DBuildingParser()
