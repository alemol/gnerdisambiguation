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
            info = {
               'entidad_nombre': row["entidad_nombre"].strip(),
               'entidad_cvegeo': row["entidad_cvegeo"]
            }

    return info

if __name__ == '__main__':
    STATE_GEOJSON = './sources/estados.geojson'
    geodf = load_geojson_state(STATE_GEOJSON)
    point =  Point(-89.08797, 20.60988)
    state = inside_state(point, geodf)
    if state is not None :
        print(state)