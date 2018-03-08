'''
author: Md Shaifur Rahman (mdsrahman@cs.stonybrook.edu)
        Stony Brook University, NY.
'''


class CityGML3DBuildingParser(object):
    '''
    Given a citygml file (.gml) this class
        1. parses the 3D building structure and save it
        2. visualize the 3D structures (not recommended for large swathes of area)
        3. calculate the line-of-sight assuming one FSO antenna at the roof-top of everybuilding
        4. calculate coverage assuming one base-station at the ground level of every building
        4. save the above graphs for future flow-level computation of FSONet
    '''
    def __init__(self):
        print "CityGML3DBuildingParser object created.."
        return

    def loadGMLFile(self, input_gml_filepath, citygml_building_namespace):
        return

    def save3DBuildingData(self, output_building_filepath):
        return

    def load3DBuildingData(self, input_building_filepath):
        return

    def visualizeBuildingData(self, input_building_filepath):
        return




if __name__ == '__main__':
    cg3b = CityGML3DBuildingParser()