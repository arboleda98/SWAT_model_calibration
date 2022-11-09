Low Impact Development practices (.lid): The first 17 lines for a Green Roof, the next *** for a Rain Gargen, the next *** for a CiStern, and the following *** for a Porous paVement
    | Urban land use name
 URHD URMD    | 0=the green roof is inactive (no simulation), 1=active
    0    0    | Month when the green roof became operational (1-12)
    1    1    | Year when the wet pond became operational (e.g. 1980)
 1900 1900    | Fraction of impervious areas where green roofs are installed
    1    1    | 0=Characteristics (FC, WP, and Ksat) of the amended soil are identical to those of the native HRU soil, 1=read user input
    0    0    | Evapotranspiration coefficient
    0    0    | Field capacity of the amended soil (mm/mm)
  0.4  0.4    | Wilting point of the amended soil (mm/mm)
 0.15 0.15    | Saturated hydraulic conductivity of the amended soil layer (mm/hr)
   50   50    | Porosity of the amended soil layer (mm/mm)
  0.5  0.5    | Hydraulic efficiency factor (considering clogging up and anisotropy ratio) (0-1)
  0.5  0.5    | Depth of the amended soil (m)
  0.5  0.5    | A line prepared for additional parameters of the green roof
    0    0    | A line prepared for additional parameters of the green roof
    0    0    | A line prepared for additional parameters of the green roof
    0    0    | A line prepared for additional parameters of the green roof
    0    0    | A line prepared for additional parameters of the green roof
    0    0    | 0=the rain garden is inactive (no simulation), 1=active
    0    0    | Month when the rain garden became operational (1-12)
    1    1    | Year when the wet pond became operational (eg 1980)
 1900 1900    | Fraction of impervious areas draining water to the rain garden
    1    1    | 0=Characteristics (FC, WP, and Ksat) of the amended soil are identical to those of the native HRU soil, 1=read user input
    0    0    | Evapotranspiration coefficient
    0    0    | Field capacity of the amended soil (mm/mm)
  0.4  0.4    | Wilting point of the amended soil (mm/mm)
 0.15 0.15    | Saturated hydraulic conductivity of the amended soil layer (mm/hr)
   50   50    | Porosity of the amended soil layer (mm/mm)
  0.5  0.5    | Hydraulic efficiency factor (considering clogging up and anisotropy ratio) (0-1)
  0.5  0.5    | Depth of the amended soil (m)
  0.5  0.5    | Options for determining the size of the surface storage of the rain garden: 0=the storage dimension is determined based on volume requirement estimated from the drainage areas of the rain garden, assuming the storage depth of 0.1 m, 1=read user input (dim
    0    0    | Fractional area of the rain garden storage surface to the impervious area of an urban HRU (0-1)
    1    1    | (not used yet) Runoff volume required to fill the pool (storage of the rain garden on the soil surface), m3
    0    0    | Depth of the rain garden storage (m)
    1    1    | Diameter of the surface area of the rain garden (m; frustum of a circular cone)
    1    1    | Diameter of the bottom of the rain garden (m; frustum of a circular cone)
    1    1    | Slope of a slant of the rain garden storage (surface side slopes) (m; frustum of a circular cone)
  0.5  0.5    | 0=the orifice drainage is inactive (no simulation), 1=active
    0    0    | Height of the orifice from the bottom of the storage (m)
    0    0    | Diameter of the orifice pipe (m)
    0    0    | A line prepared for additional parameters for the rain garden
    0    0    | A line prepared for additional parameters for the rain garden
    0    0    | A line prepared for additional parameters for the rain garden
    0    0    | A line prepared for additional parameters for the rain garden
    0    0    | A line prepared for additional parameters for the rain garden
    0    0    | 0=the cistern is inactive (no simulation), 1=active
    0    0    | Month when the cistern became operational (1-12)
    1    1    | Year when the cistern became operational (e.g. 1980)
 1900 1900    | 0=the cistern is not connected to the corresponding green roof located in the same HRU, 1=the cistern is connected to the corresponding green roof located in the same HRU
    0    0    | Fraction of impervious areas draining water to the cistern
    1    1    | Runoff volume to fill the cistern (storage of the cistern), m3; If CS_VOL is zero, SWAT calculates the cistern capacity with CS_RDEPTH.
    0    0    | Rainfall depth generated in treated area to fill the cistern (storage of the cistern) (mm); If CS_RDEPTH is zero, SWAT assumes the cistern capacity as 5 m3
   25   25    | A line prepared for additional parameters for the cistern
    0    0    | A line prepared for additional parameters for the cistern
    0    0    | A line prepared for additional parameters for the cistern
    0    0    | A line prepared for additional parameters for the cistern
    0    0    | A line prepared for additional parameters for the cistern
    0    0    | 0=the porous pavement is inactive (no simulation), 1=active
    0    0    | Month when the porous pavement became operational (1-12)
    1    1    | Year when the porous pavement became operational (e.g. 1980)
 1900 1900    | Fraction of impervious areas where the porous pavement is installed
    1    1    | Depth of the gravel bed of porous pavement (mm)
  500  500    | Porosity of the gravel bed of porous pavement (mm/mm)
  0.5  0.5    | 0=Characteristics (FC, WP, and Ksat) of the amended soil are identical to those of the native HRU soil, 1=read user input
    0    0    | Drainage coefficient
    0    0    | Field capacity of the amended soil  (mm/mm)
  0.4  0.4    | Wilting point of the amended soil (mm/mm)
 0.15 0.15    | Saturated hydraulic conductivity of the amended soil layer (mm/hr)
   50   50    | Porosity of the amended soil layer
  0.5  0.5    | Hydraulic efficiency factor (considering clogging up and anisotropy ratio)
  0.5  0.5    | A line prepared for additional parameters for the porous pavement
    0    0    | A line prepared for additional parameters for the porous pavement
    0    0    | A line prepared for additional parameters for the porous pavement
    0    0    | A line prepared for additional parameters for the porous pavement
    0    0    | A line prepared for additional parameters for the porous pavement
    0    0

