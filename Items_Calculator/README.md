# 📦 Gestor de Recetas - Black Desert Craft

Sistema de gestión de recetas de crafteo para el videojuego **Black Desert**.  
Permite crear items, definir recetas (con ingredientes y sub-recetas), y calcular automáticamente los materiales necesarios para fabricar una cantidad deseada, teniendo en cuenta el inventario disponible y mostrando la jerarquía completa de producción.

---

## 🧠 ¿Qué hace este programa?

- **CRUD de items** (con categorías, tipos, subtipos y flag `es_fabricable`).
- **CRUD de recetas**: cada receta produce **1 unidad** de un item fabricable y puede usar cualquier otro item como ingrediente (base o fabricable).
- **Cálculo recursivo de materiales**:
  - Dada una receta final y una cantidad, descompone recursivamente todos los niveles de sub‑recetas.
  - Muestra:
    - Materiales base necesarios (sin receta).
    - Productos intermedios a fabricar.
    - Estructura jerárquica completa (árbol de producción).
  - Permite restar **inventario inicial** para ajustar las cantidades finales.
- **Interfaz web amigable**:
  - Formularios con autocompletado (`<datalist>`) para seleccionar items (no `<select>` masivos).
  - Mensajes flash de éxito/error.
  - Label que indica la **última receta creada** en la lista de recetas.
  - Página de inicio con accesos directos.

---

## 🛠️ Tecnologías utilizadas

| Capa          | Tecnología                                        |
|---------------|---------------------------------------------------|
| Backend       | Python 3.14 + Django 4.2                         |
| Base de datos | PostgreSQL 18 (puede cambiarse a SQLite)         |
| ORM           | Django ORM                                        |
| Frontend      | HTML5 + Bootstrap 5 (CDN)                        |
| Autocompletado| Datalist nativo del navegador                    |
| Servidor      | Django `runserver` (desarrollo)                  |

---

## 🚀 Estado actual del proyecto

### ✅ Funcionalidades completadas

- [x] Modelos `Item`, `Recipe`, `Ingredient`, `Category`, `Type`, `Subtype`.
- [x] Vistas CRUD públicas para items y recetas (sin usar el admin de Django).
- [x] Normalización de nombres de items (elimina acentos, puntuación, espacios múltiples y capitaliza).
- [x] Restricción de unicidad en nombres de items y recetas.
- [x] Captura de errores de duplicado con mensajes amigables.
- [x] Campo `es_fabricable` para filtrar qué items pueden ser producidos.
- [x] Cálculo recursivo de materiales con detección de ciclos.
- [x] Inventario inicial (formato "nombre: cantidad" por línea).
- [x] Visualización jerárquica del árbol de producción (HTML generado recursivamente).
- [x] Autocompletado en todos los selects de items (input + datalist).
- [x] Ordenación alfabética en listas y desplegables.
- [x] Mensaje de "última receta creada" almacenado en sesión.
- [x] Página de detalle de receta.

### 🧪 Próximas mejoras planificadas

- [ ] Edición/eliminación de categorías, tipos y subtipos desde la interfaz pública.
- [ ] Búsqueda avanzada en listados.
- [ ] Exportación de resultados de cálculo a PDF o Excel.
- [ ] Soporte para recetas que produzcan más de 1 unidad por lote.
- [ ] Validación de que un item fabricable siempre tenga una receta.
- [ ] Pruebas unitarias y de integración.

---

## 📦 Instalación y ejecución local

### Requisitos previos

- Python 3.10 o superior.
- PostgreSQL (o SQLite para versión portátil).
- Entorno virtual (recomendado).

### Pasos

1. **Clonar el repositorio** (o copiar los archivos).
2. **Crear y activar entorno virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows