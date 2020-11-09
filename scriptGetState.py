import matplotlib.pyplot as plt
from geopandas import GeoDataFrame, gpd
from shapely.geometry import box, Point, Polygon, MultiPolygon

def load_geojson_state(df_uri):
    df = gpd.read_file(df_uri)
    return df

def inside_state(point, df):
    info = None
    for index, row in df.iterrows(): 
        inside = point.within(row['geometry'])
        if(inside):
            info = row["admin1code"]
    return info

def inside_state_V2(point, state):
    info = None
    for index, state in state.iterrows(): 
        inside = state['geometry'].contains(point)
        if(inside):
            info = {
                'entidad_nombre': state["entidad_nombre"].strip(),
                'entidad_cvegeo': state["entidad_cvegeo"],
                'admin1code': state["admin1code"]
            }
    return info

def inside_municipality(point, cvegeo, municipalities):
    info = None
    for index, municipalities in municipalities.iterrows(): 
        if municipalities['entidad_cvegeo'] == cvegeo:
            inside = municipalities['geometry'].contains(point)
            if(inside):
                info = {
                    'municipio_nombre': municipalities["municipio_nombre"].strip(),
                    'municipio_cvegeo': municipalities["municipio_cvegeo"]
                }
    
    return info

def bridge(point):
    STATE_GEOJSON = './sources/estados.geojson'
    geodf = load_geojson_state(STATE_GEOJSON)
    state = inside_state(point, geodf)
    return state


def get_geometry_by_state(name, df):
    info = None
    for index, row in df.iterrows(): 
        if(name == row["entidad_nombre"].strip()):
            info = {
               'entidad_nombre': row["entidad_nombre"].strip(),
               'entidad_cvegeo': row["entidad_cvegeo"],
               'geometry': row['geometry'],
               'center': row['geometry'].centroid,
               'boundingbox': row['geometry'].bounds
            }

    return info

def get_geometry_by_code(code, df):
    info = None
    for index, row in df.iterrows(): 
        if(code == row["admin1code"].strip()):
            info = {
               'entidad_nombre': row["entidad_nombre"].strip(),
               'entidad_cvegeo': row["entidad_cvegeo"],
               'geometry': row['geometry'],
               'center': row['geometry'].centroid,
               'boundingbox': row['geometry'].bounds
            }

    return info

if __name__ == '__main__':
    STATE_GEOJSON = './sources/estados.geojson'
    MUNICIPALITY_GEOJSON = './sources/municipios.geojson'

    geodf = load_geojson_state(STATE_GEOJSON)
    geoMundf = load_geojson_state(MUNICIPALITY_GEOJSON)
    point =  Point(-89.08797, 20.60988)
    #point = box(-105.5676132838,24.6029371925,-104.3591171901,25.7760147766)

    state = inside_state_V2(point, geodf)
    if state is not None :
        state['municipality'] = inside_municipality(point, state['entidad_cvegeo'], geoMundf)
        if state is not None :
            print(state)