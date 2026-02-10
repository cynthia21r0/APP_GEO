from flask import Flask, render_template, request
import requests
from math import radians, cos, sin, asin, sqrt

app = Flask(__name__)

def calcular_distancia(lat1, lon1, lat2, lon2):
    """Calcula la distancia en metros entre dos coordenadas"""
    try:
        lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371000
        return c * r
    except:
        return 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    if request.method == 'POST':
        lugar = request.form['lugar']
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": lugar,
            "format": "json",
            "limit": 5,
            "addressdetails": 1,
            "extratags": 1
        }
        headers = {
            "User-Agent": "Flask-Educational-App/1.0"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            data = response.json()
            
            if data and len(data) > 0:
                mejor_resultado = None
                for result in data:
                    tipo = result.get('type', '')
                    clase = result.get('class', '')
                    
                    if tipo in ['city', 'town', 'village', 'municipality', 'hamlet'] or \
                       clase in ['place', 'boundary']:
                        mejor_resultado = result
                        break
                
                if not mejor_resultado:
                    mejor_resultado = data[0]
                
                lat = mejor_resultado['lat']
                lon = mejor_resultado['lon']
                nombre = mejor_resultado['display_name']
                
                return render_template(
                    'map.html',
                    lat=lat,
                    lon=lon,
                    nombre=nombre,
                    mostrar_categorias=True
                )
        except Exception as e:
            print(f"Error en búsqueda: {e}")
    
    return render_template('map.html', error=True)

@app.route('/buscar_cercano', methods=['POST'])
def buscar_cercano():
    lat = float(request.form['lat'])
    lon = float(request.form['lon'])
    nombre = request.form['nombre']
    categoria = request.form['categoria']
    estilo_mapa = request.form.get('estilo', 'satellite')
    
    # Radio fijo de 10km para búsqueda amplia
    radio_busqueda = 10000
    
    categorias_overpass = {
        'restaurant': 'amenity=restaurant',
        'fast_food': 'amenity=fast_food',
        'school': 'amenity=school',
        'hotel': 'tourism=hotel',
        'supermarket': 'shop=supermarket',
        'atm': 'amenity=atm',
        'police': 'amenity=police',
        'park': 'leisure=park',
        'museum': 'tourism=museum',
        'cinema': 'amenity=cinema',
        'gym': 'leisure=fitness_centre',
        'library': 'amenity=library',
        'gas_station': 'amenity=fuel',
        'church': 'amenity=place_of_worship',
        'butcher': 'shop=butcher',
        'electronics': 'shop=electronics'
    }
    
    overpass_tag = categorias_overpass.get(categoria, 'amenity=restaurant')
    
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:25];
    (
      node[{overpass_tag}](around:{radio_busqueda},{lat},{lon});
      way[{overpass_tag}](around:{radio_busqueda},{lat},{lon});
    );
    out body;
    >;
    out skel qt;
    """
    
    lugares_cercanos = []
    
    try:
        response = requests.post(overpass_url, data={'data': query}, timeout=30)
        data = response.json()
        
        processed_ids = set()
        all_nodes = {e['id']: e for e in data.get('elements', []) if e.get('type') == 'node'}
        
        for element in data.get('elements', []):
            if element.get('type') not in ['node', 'way']:
                continue
                
            element_id = element.get('id')
            if element_id in processed_ids:
                continue
            
            tags = element.get('tags', {})
            if not tags:
                continue
                
            nombre_lugar = tags.get('name', '')
            if not nombre_lugar or nombre_lugar == '':
                continue
            
            if element['type'] == 'node':
                lat_lugar = element.get('lat')
                lon_lugar = element.get('lon')
            elif element['type'] == 'way':
                way_nodes = element.get('nodes', [])
                lats = [all_nodes[nid]['lat'] for nid in way_nodes if nid in all_nodes]
                lons = [all_nodes[nid]['lon'] for nid in way_nodes if nid in all_nodes]
                
                if lats and lons:
                    lat_lugar = sum(lats) / len(lats)
                    lon_lugar = sum(lons) / len(lons)
                else:
                    continue
            else:
                continue
            
            if lat_lugar and lon_lugar:
                distancia = calcular_distancia(lat, lon, lat_lugar, lon_lugar)
                
                calle = tags.get('addr:street', '')
                numero = tags.get('addr:housenumber', '')
                ciudad = tags.get('addr:city', '')
                telefono = tags.get('phone', tags.get('contact:phone', ''))
                website = tags.get('website', tags.get('contact:website', ''))
                
                direccion_parts = []
                if calle:
                    if numero:
                        direccion_parts.append(f"{calle} {numero}")
                    else:
                        direccion_parts.append(calle)
                if ciudad:
                    direccion_parts.append(ciudad)
                
                direccion = ', '.join(direccion_parts) if direccion_parts else "Sin dirección"
                
                lugares_cercanos.append({
                    'lat': lat_lugar,
                    'lon': lon_lugar,
                    'nombre': nombre_lugar,
                    'direccion': direccion,
                    'telefono': telefono if telefono else 'No disponible',
                    'website': website,
                    'distancia': round(distancia),
                    'tipo': categoria.replace('_', ' ').title()
                })
                
                processed_ids.add(element_id)
        
        # Ordenar por distancia
        lugares_cercanos.sort(key=lambda x: x['distancia'])
        
        # Limitar a 50 resultados
        lugares_cercanos = lugares_cercanos[:50]
        
    except Exception as e:
        print(f"Error en búsqueda cercana: {e}")
        lugares_cercanos = []
    
    return render_template(
        'map.html',
        lat=lat,
        lon=lon,
        nombre=nombre,
        mostrar_categorias=True,
        categoria_seleccionada=categoria,
        lugares_cercanos=lugares_cercanos,
        estilo_mapa=estilo_mapa
    )

if __name__ == '__main__':
    app.run(debug=True)