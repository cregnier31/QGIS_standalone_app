# 3D point class
class Point:
    
    # class constructor
    def __init__(self, x, y, z=0.0):
        
        self.x = x
        self.y = y
        self.z = z


    # calculate euclidean distance between two points
    def distance(self, pt):

        return sqrt((self.x - pt.x)**2 + (self.y - pt.y)**2 + (self.z - pt.z)**2)
    
    
    # create a new point shifted by given amount
    def movedby(self, sx, sy, sz=0.0):
    
        return Point( self.x + sx , self.y + sy, self.z + sz )        


    # set driver format
    def set_driverShortName(self, raster_driver):
    
        self.driver_shortname = raster_driver
   
   
    # get driver format
    def get_driverShortName(self):
   
        return self.driver_shortname


    # set data type
    def set_dataType(self, data_type):

        self.datatype = data_type
   
   
    # get data type
    def get_dataType(self):
   
        return self.datatype


    # set nodata value
    def set_noDataValue(self, nodataval):

        self.nodatavalue = nodataval
   
   
    # get nodata value
    def get_noDataValue(self):
   
        return self.nodatavalue


    # set projection
    def set_projection(self, proj):

        self.projection = proj
   
   
    # get projection
    def get_projection(self):
   
        return self.projection


    # set topleftX value
    def set_topLeftX(self, topleftX):

        self.topleftX = topleftX
   
   
    # get topleftX value
    def get_topLeftX(self):
   
        return self.topleftX


    # set topleftY value
    def set_topLeftY(self, topleftY):

        self.topleftY = topleftY
   
   
    # get topleftY value
    def get_topLeftY(self):
   
        return self.topleftY


    # set pixsizeEW value
    def set_pixSizeEW(self, pixsizeEW):

        self.pixsizeEW = pixsizeEW
   
   
    # get pixsizeEW value
    def get_pixSizeEW(self):
   
        return self.pixsizeEW


    # set pixsizeNS value
    def set_pixSizeNS(self, pixsizeNS):

        self.pixsizeNS = pixsizeNS
   
   
    # get pixsizeNS value
    def get_pixSizeNS(self):
   
        return self.pixsizeNS
        
        
    # set rows number
    def set_rows(self, rows):
        
        self.rows = rows
   
   
    # get rows number
    def get_rows(self):
   
        return self.rows


    # set cols number
    def set_cols(self, cols):

        self.cols = cols
   
   
    # get cols number
    def get_cols(self):
   
        return self.cols


    # set rotationA value
    def set_rotationA(self, rotationA):

        self.rotationA = rotationA
   
    # get rotationA value
    def get_rotationA(self):
        
        return self.rotationA
        
        
    # set rotationB value
    def set_rotationB(self, rotationB):
        
        self.rotationB = rotationB
   
   
    # get rotationB value
    def get_rotationB(self):
   
        return self.rotationB
     
     
    # check absence of axis rotations or pixel size differences
    def check_params(self, tolerance = 1e-06):
        
        # check if pixel size can be considered the same in the two axis directions
        if abs(abs(self.pixsizeEW) - abs(self.pixsizeNS))/abs(self.pixsizeNS) > tolerance :
            return False, 'Pixel sizes in x and y directions are different in raster' 
            
        # check for the absence of axis rotations
        if abs(self.rotationA) > tolerance or abs(self.rotationB) > tolerance:
            raise False, 'There should be no axis rotation in raster' 
        
        return True, 'OK'


    # checks equivalence between the geographical parameters of two grids
    def geo_equiv(self, other, tolerance=1.0e-6): 

        if 2*(self.get_topLeftX() - other.get_topLeftX())/(self.get_topLeftX() + other.get_topLeftX()) > tolerance or \
            2*(self.get_topLeftY() - other.get_topLeftY())/(self.get_topLeftY() + other.get_topLeftY()) > tolerance or \
            2*(abs(self.get_pixSizeEW()) - abs(other.get_pixSizeEW()))/(abs(self.get_pixSizeEW()) + abs(other.get_pixSizeEW())) > tolerance or \
            2*(abs(self.get_pixSizeNS()) - abs(other.get_pixSizeNS()))/(abs(self.get_pixSizeNS()) + abs(other.get_pixSizeNS())) > tolerance or \
            self.get_rows() != other.get_rows() or self.get_cols() != other.get_cols() or \
            self.get_projection() != other.get_projection():    
            return False
        else:
            return True
            
