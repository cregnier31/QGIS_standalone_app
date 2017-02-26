import numpy as np
import sys
from Point import Point
import numpy.ma as ma
# check array input
def arr_check(curr_array):
    if len(curr_array.shape) != 3 and \
        curr_array.shape[2] != 2:
        return False
    return True

class Grid:
    # alternative class constructor
    def __init__(self, grid_params = None, grid_data = None): 
                
        if grid_params is not None:
            # define lower-left corner as initial point
            pt_init = Point( grid_params.get_topLeftX(), grid_params.get_topLeftY() - abs(grid_params.get_pixSizeNS())*grid_params.get_rows() )             
            # define top-right corner as end point
            pt_end = Point( grid_params.get_topLeftX() + abs(grid_params.get_pixSizeEW())*grid_params.get_cols(), grid_params.get_topLeftY() )  
                    
            self.grid_domain = SpatialDomain(pt_init, pt_end)
        else:
            self.grid_domain = None
        self.grid_data = grid_data
        
    # set grid domain
    def set_grid_domain(self, pt_init, pt_end):
        self.grid_domain = SpatialDomain(pt_init, pt_end)


    # get grid domain
    def get_grid_domain(self):
        return self.grid_domain
        
        
    # set grid data
    def set_grid_data(self, data_array, level=None):
        try:
            if level is None:
                self.grid_data = data_array
            elif level == 0 or level == 1:
                self.grid_data[:,:, level] = data_array
            else:
                raise Raster_Parameters_Errors, 'Provided level for data array must be 0 or 1'
        except:
            raise Raster_Parameters_Errors, 'Unable to set grid data (function set_grid_data error)'
       
       
    # get grid data
    def get_grid_data(self, level=None):        
        try:
            if level is None:
                return self.grid_data
            elif level == 0 or level == 1:
                return self.grid_data[:,:, level]
            else:
                raise Raster_Parameters_Errors, 'Provided level for data array extraction must be 0 or 1'
        except:
            raise Raster_Parameters_Errors, 'Unable to extract grid data (function get_grid_data error)'            
        
        
    # get row number of the grid domain
    def get_ylines_num(self):
        return np.shape(self.grid_data)[0]        


    # column number of the grid domain         
    def get_xlines_num(self):
        return np.shape(self.grid_data)[1]        
            
            
    # returns the cell size of the gridded dataset in the x direction 
    def get_cellsize_x(self):
        return self.grid_domain.get_xrange()/float(self.get_xlines_num())


    # returns the cell size of the gridded dataset in the y direction 
    def get_cellsize_y(self):
        return self.grid_domain.get_yrange()/float(self.get_ylines_num())
            
            
    # returns the mean horizontal cell size 
    def get_cellsize_horiz_mean(self):
        return (self.get_cellsize_x()+self.get_cellsize_y())/2.0
  
  
    # converts from geographic to grid coordinates
    def geog2gridcoord(self, curr_Pt):
        currArrCoord_grid_i = (self.get_grid_domain().get_end_point().y - curr_Pt.y )/self.get_cellsize_y()
        currArrCoord_grid_j = (curr_Pt.x - self.get_grid_domain().get_start_point().x)/self.get_cellsize_x()
        return ArrCoord(currArrCoord_grid_i, currArrCoord_grid_j)


    # converts from grid to geographic coordinates
    def grid2geogcoord(self, currArrCoord):
        currPt_geogr_y = self.get_grid_domain().get_end_point().y - currArrCoord.i*self.get_cellsize_y()
        currPt_geogr_x = self.get_grid_domain().get_start_point().x + currArrCoord.j*self.get_cellsize_x()
        return Point(currPt_geogr_x, currPt_geogr_y)
        
      
    # calculates magnitude 
    def magnitude(self):
        if not arr_check(self.grid_data):
            raise FunInp_Err, 'input requires data array with three dimensions and 2-level third dimension'
        vx = self.grid_data[:,:,0]
        vy = self.grid_data[:,:,1]
        magnitude = np.sqrt(vx**2 + vy**2)
        magnitude_fld = Grid()
        magnitude_fld.set_grid_domain(self.get_grid_domain().get_start_point(), self.get_grid_domain().get_end_point())
        magnitude_fld.set_grid_data(magnitude)
        
        return magnitude_fld


    # calculates orientations 
    def orientations(self):        

        if not arr_check(self.grid_data):
            raise FunInp_Err, 'input requires data array with three dimensions and 2-level third dimension'
                     
        vx, vy = self.grid_data[:,:,0], self.grid_data[:,:,1]

        orientations = np.degrees(np.arctan2(vx, vy))
        orientations = np.where(orientations < 0.0, orientations + 360.0, orientations)
        
        orientations_fld = Grid()
        orientations_fld.set_grid_domain(self.get_grid_domain().get_start_point(), self.get_grid_domain().get_end_point())
        orientations_fld.set_grid_data(orientations)
        
        return orientations_fld
        

    # calculates magnitude gradient along x axis
    def grad_xaxis(self):    

        if not arr_check(self.grid_data):
            raise FunInp_Err, 'input requires data array with three dimensions and 2-level third dimension'
                      
        vx, vy = self.grid_data[:,:,0], self.grid_data[:,:,1]
        
        dir_array = np.arctan2(vx, vy)
        
        vect_magn = np.sqrt(vx**2 + vy**2)
        dm_dy, dm_dx = np.gradient(vect_magn)
        
        vect_xgrad_fld = Grid()
        vect_xgrad_fld.set_grid_domain(self.get_grid_domain().get_start_point(), self.get_grid_domain().get_end_point())
        vect_xgrad_fld.set_grid_data(dm_dx/self.get_cellsize_horiz_mean())
        
        return vect_xgrad_fld
        
 
    # calculates magnitude gradient along y axis
    def grad_yaxis(self):    

        if not arr_check(self.grid_data):
            raise FunInp_Err, 'input requires data array with three dimensions and 2-level third dimension'
                      
        vx, vy = self.grid_data[:,:,0], self.grid_data[:,:,1]
        
        dir_array = np.arctan2(vx, vy)
        
        vect_magn = np.sqrt(vx**2 + vy**2)
        dm_dy, dm_dx = np.gradient(vect_magn)
        dm_dy = - dm_dy
        
        vect_ygrad_fld = Grid()
        vect_ygrad_fld.set_grid_domain(self.get_grid_domain().get_start_point(), self.get_grid_domain().get_end_point())
        vect_ygrad_fld.set_grid_data(dm_dy/self.get_cellsize_horiz_mean())
        
        return vect_ygrad_fld
        

 
    # returns the velocity components interpolated using the bilinear interpolation        
    def interpolate_level_bilinear(self, level, curr_Pt_gridcoord):
 
        try:
            v_00 = self.get_grid_data(level)[floor(curr_Pt_gridcoord.i - 0.5), floor(curr_Pt_gridcoord.j - 0.5)]
            v_10 = self.get_grid_data(level)[floor(curr_Pt_gridcoord.i - 0.5), ceil(curr_Pt_gridcoord.j - 0.5)]
            v_01 = self.get_grid_data(level)[ceil(curr_Pt_gridcoord.i - 0.5), floor(curr_Pt_gridcoord.j - 0.5)]    
            v_11 = self.get_grid_data(level)[ceil(curr_Pt_gridcoord.i - 0.5), ceil(curr_Pt_gridcoord.j - 0.5)]
        except:
            raise Raster_Parameters_Errors, 'Error in get_grid_data() function'
            
        delta_j_grid = curr_Pt_gridcoord.j - int(curr_Pt_gridcoord.j)
        
        assert delta_j_grid >= 0 and delta_j_grid < 1
        
        if delta_j_grid >= 0.5:
            delta_j_grid = delta_j_grid - 0.5
        else:
            delta_j_grid = 0.5 + delta_j_grid             
        
        v_y0 = v_00 + (v_10-v_00)*delta_j_grid
        v_y1 = v_01 + (v_11-v_01)*delta_j_grid
        

        delta_i_grid = curr_Pt_gridcoord.i - int(curr_Pt_gridcoord.i)
        
        assert delta_i_grid >= 0 and delta_i_grid < 1
        
        if delta_i_grid >= 0.5:
            delta_i_grid = delta_i_grid - 0.5
        else:
            delta_i_grid = 0.5 + delta_i_grid
            
        interp_v = v_y0 + (v_y1-v_y0)*delta_i_grid
                
        return interp_v  


    # check if a point pathline can be evaluated
    def include_point_location(self, currPoint): 
                    
        curr_Pt_gridcoord = self.geog2gridcoord(currPoint)
        
        if curr_Pt_gridcoord.i < 0.5 or curr_Pt_gridcoord.j < 0.5 or \
           curr_Pt_gridcoord.j > (self.get_xlines_num() - 0.5) or curr_Pt_gridcoord.i > (self.get_ylines_num() - 0.5):
            return False
 
        if len(self.grid_data.shape) != 3 and \
            self.grid_data.shape[2] != 2:
            raise FunInp_Err, 'input requires data array with three dimensions and 2-level third dimension'
                    
        for n in range(2):
            if np.isnan(self.get_grid_data(n)[floor(curr_Pt_gridcoord.i - 0.5), floor(curr_Pt_gridcoord.j - 0.5)]) or \
               np.isnan(self.get_grid_data(n)[ceil(curr_Pt_gridcoord.i - 0.5), floor(curr_Pt_gridcoord.j - 0.5)]) or \
               np.isnan(self.get_grid_data(n)[floor(curr_Pt_gridcoord.i - 0.5), ceil(curr_Pt_gridcoord.j - 0.5)]) or \
               np.isnan(self.get_grid_data(n)[ceil(curr_Pt_gridcoord.i - 0.5), ceil(curr_Pt_gridcoord.j - 0.5)]):
                return False
                
        return True
 

    def point_velocity( self, currpoint ):
        """
        return the velocity components of a point in a velocity field
        """
        
        if not self.include_point_location( currpoint ): 
            return None, None 
            
        currpoint_gridcoord = self.geog2gridcoord( currpoint )            
        currpoint_vx = self.interpolate_level_bilinear( 0, currpoint_gridcoord )
        currpoint_vy = self.interpolate_level_bilinear( 1, currpoint_gridcoord )
        
        return currpoint_vx, currpoint_vy
        
        
         
    # writes ESRI ascii grid
    def write_esrigrid(self, outgrid_fn, esri_nullvalue = -99999, level = 0):

        outgrid_fn = str(outgrid_fn)
        
        # checking existence of output slope grid
        if os.path.exists(outgrid_fn):
            raise Output_Errors, "Output grid '%s' already exists" % outgrid_fn

        try:
            outputgrid = open(outgrid_fn, 'w') #create the output ascii file
        except:
            raise Output_Errors, "Unable to create output grid '%s'" % outgrid_fn
       
        if outputgrid is None:
            raise Output_Errors, "Unable to create output grid '%s'" % outgrid_fn

        # writes header of grid ascii file
        outputgrid.write('NCOLS %d\n' % self.get_xlines_num())
        outputgrid.write('NROWS %d\n' % self.get_ylines_num())
        outputgrid.write('XLLCORNER %.8f\n' % self.grid_domain.get_start_point().x)
        outputgrid.write('YLLCORNER %.8f\n' % self.grid_domain.get_start_point().y)
        outputgrid.write('CELLSIZE %.8f\n' % self.get_cellsize_horiz_mean())
        outputgrid.write('NODATA_VALUE %d\n' % esri_nullvalue)

        esrigrid_outvalues = np.where(np.isnan(self.grid_data), esri_nullvalue, self.grid_data)
        
        #output of results
        if len(self.grid_data.shape) == 3:
            for i in range(0, self.get_ylines_num()):
                    for j in range(0, self.get_xlines_num()):
                            outputgrid.write('%.8f ' % (esrigrid_outvalues[i,j,level]))
                    outputgrid.write('\n')
        elif len(self.grid_data.shape) == 2:
            for i in range(0, self.get_ylines_num()):
                    for j in range(0, self.get_xlines_num()):
                            outputgrid.write('%.8f ' % (esrigrid_outvalues[i,j]))
                    outputgrid.write('\n')
                    
        outputgrid.close()

        
        return True        

###################################
# Rectangular spatial domain class
class SpatialDomain:
   
    
    # class constructor
    def __init__(self, pt_init, pt_end): 
   
        self.pt_init = pt_init # lower-left corner of the domain, class: Point
        self.pt_end = pt_end # top-right corner of the domain, class: Point


    # get start point
    def get_start_point(self):

        return self.pt_init


    # get end point
    def get_end_point(self):

        return self.pt_end
    
    
    # get x range of spatial domain
    def get_xrange(self):
    
        return self.pt_end.x-self.pt_init.x


    # get y range of spatial domain
    def get_yrange(self):

        return self.pt_end.y-self.pt_init.y


    # get z range of spatial domain
    def get_zrange(self):

        return self.pt_end.z-self.pt_init.z


    # get horizontal area of spatial domain
    def get_horiz_area(self):

        return self.get_xrange()*self.get_yrange()

