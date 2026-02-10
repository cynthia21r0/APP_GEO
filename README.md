# Buscador de Lugares

Una aplicación web simple desarrollada con Flask que permite buscar ubicaciones en todo el mundo y encontrar lugares cercanos de interés como restaurantes, gasolineras, hoteles y mucho más.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)

## Url del Resultado en Render

## Características

- 🔍 **Búsqueda Global**: Encuentra cualquier ubicación en el mundo usando OpenStreetMap
- 📍 **Lugares Cercanos**: Descubre restaurantes, hospitales, hoteles, bancos y más
- 🗺️ **Múltiples Estilos de Mapa**: Vista satelital, estándar, terreno y modo oscuro
- 📱 **Responsive**: Funciona perfectamente en dispositivos móviles y escritorio
- ⚡ **Resultados Rápidos**: Búsqueda optimizada con hasta 50 resultados

## Uso

### Búsqueda Básica

1. Ingresa el nombre de una ciudad, dirección o lugar en el buscador
2. Haz clic en "Buscar"
3. Selecciona la categoría de lugar que deseas encontrar
4. Elige el estilo de mapa de tu preferencia
5. Haz clic en "Buscar lugares"

### Categorías Disponibles

#### 🍽️ Comida
- Restaurantes
- Comida Rápida

#### 🎓 Educación
- Escuelas
- Bibliotecas

#### 🛒 Compras
- Supermercados
- Electrónica

## Tecnologías Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Mapas**: Leaflet.js
- **APIs**:
  - OpenStreetMap Nominatim (Geocodificación)
  - Overpass API (Búsqueda de lugares)
- **Fuentes**: Google Fonts (Poppins)

## Configuración

### Radio de Búsqueda

Por defecto, la aplicación busca lugares en un radio de 10 km. Puedes modificar esto en `app.py`:

```python
# Línea 81
radio_busqueda = 10000  # en metros
```

### Límite de Resultados

Por defecto se muestran hasta 50 resultados. Puedes cambiarlo en `app.py`:

```python
# Línea 188
lugares_cercanos = lugares_cercanos[:50]
```
