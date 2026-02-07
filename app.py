"""
Aplicación Flask para búsqueda de lugares de interés con OpenStreetMap
Permite buscar gasolineras, hospitales, restaurantes y otros puntos de interés
"""

from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Configuración de la API de Nominatim
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "FlaskGeoApp/1.0 (Educational Project)"

@app.route('/')
def index():
    """
    Ruta principal que muestra la página de búsqueda
    """
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """
    Procesa la búsqueda del lugar ingresado por el usuario
    Retorna las coordenadas y el nombre del lugar encontrado
    """
    # Obtener datos del formulario
    lugar = request.form.get('lugar', '')
    tipo_lugar = request.form.get('tipo', '')
    
    if not lugar:
        return render_template('index.html', error="Por favor ingresa un lugar")
    
    # Construir la consulta según el tipo de lugar
    if tipo_lugar and tipo_lugar != 'general':
        query = f"{tipo_lugar} en {lugar}"
    else:
        query = lugar
    
    # Parámetros para la API de Nominatim
    params = {
        'q': query,
        'format': 'json',
        'limit': 10,  # Obtener múltiples resultados
        'addressdetails': 1
    }
    
    headers = {
        'User-Agent': USER_AGENT
    }
    
    try:
        # Realizar la petición a la API
        response = requests.get(NOMINATIM_URL, params=params, headers=headers)
        response.raise_for_status()
        
        resultados = response.json()
        
        if not resultados:
            return render_template('index.html', 
                                 error=f"No se encontraron resultados para '{query}'")
        
        # Preparar los datos para el mapa
        lugares_encontrados = []
        for resultado in resultados:
            lugar_info = {
                'nombre': resultado.get('display_name', 'Sin nombre'),
                'lat': float(resultado.get('lat', 0)),
                'lon': float(resultado.get('lon', 0)),
                'tipo': resultado.get('type', 'desconocido'),
                'categoria': resultado.get('class', 'general')
            }
            lugares_encontrados.append(lugar_info)
        
        # Renderizar la página del mapa con los resultados
        return render_template('map.html', 
                             lugares=lugares_encontrados,
                             busqueda=query,
                             tipo_seleccionado=tipo_lugar)
    
    except requests.exceptions.RequestException as e:
        return render_template('index.html', 
                             error=f"Error al conectar con el servicio: {str(e)}")

@app.route('/api/search')
def api_search():
    """
    Endpoint API para búsquedas AJAX (opcional para futuras mejoras)
    """
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'Consulta vacía'}), 400
    
    params = {
        'q': query,
        'format': 'json',
        'limit': 5
    }
    
    headers = {
        'User-Agent': USER_AGENT
    }
    
    try:
        response = requests.get(NOMINATIM_URL, params=params, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Ejecutar la aplicación en modo debug
    app.run(debug=True, host='0.0.0.0', port=5000)