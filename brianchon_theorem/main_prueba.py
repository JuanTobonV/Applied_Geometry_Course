import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse

# Configuración de la página
st.set_page_config(page_title="Teorema de Brianchon Interactivo", layout="wide")

st.title("📐 Demostración del Teorema de Brianchon")
st.markdown("""
En cualquier hexágono circunscrito a una sección cónica, las tres diagonales principales 
se intersecan en un solo punto (el **Punto de Brianchon**).

**Teorema:** Si un hexágono está circunscrito a una cónica, entonces las tres diagonales 
que conectan vértices opuestos se intersecan en un único punto.
""")

# --- Barra Lateral (Controles) ---
st.sidebar.header("Configuración")
tipo_conica = st.sidebar.selectbox("Selecciona la Cónica", ["Círculo", "Elipse", "Parábola", "Hipérbola"])

# Parámetros de la cónica
if tipo_conica == "Círculo":
    a = st.sidebar.slider("Radio", 3.0, 8.0, 5.0, 0.5)
    b = a
    p = 1.0  # No usado
elif tipo_conica == "Elipse":
    a = st.sidebar.slider("Semi-eje mayor (a)", 3.0, 8.0, 6.0, 0.5)
    b = st.sidebar.slider("Semi-eje menor (b)", 2.0, 6.0, 3.5, 0.5)
    p = 1.0  # No usado
elif tipo_conica == "Parábola":
    p = st.sidebar.slider("Parámetro focal (p)", 0.5, 3.0, 1.5, 0.1)
    a = p
    b = p
else:  # Hipérbola
    a = st.sidebar.slider("Semi-eje a", 2.0, 6.0, 3.0, 0.5)
    b = st.sidebar.slider("Semi-eje b", 2.0, 6.0, 3.0, 0.5)
    p = 1.0  # No usado

# Sliders para 6 puntos de tangencia móviles (en radianes)
st.sidebar.subheader("Puntos de Tangencia")
st.sidebar.markdown("*Controla la posición de los 6 puntos de tangencia en la cónica*")

# Valores por defecto según el tipo de cónica
if tipo_conica == "Parábola":
    default_angles = [-2.5, -1.5, -0.5, 0.5, 1.5, 2.5]
    t_min, t_max = -3.5, 3.5
elif tipo_conica == "Hipérbola":
    default_angles = [-1.2, -0.7, -0.2, 0.2, 0.7, 1.2]
    t_min, t_max = -1.4, 1.4
else:  # Círculo o Elipse
    default_angles = [0.2, 1.2, 2.0, 3.3, 4.2, 5.5]
    t_min, t_max = 0.0, 2.0 * np.pi

puntos_t = []
for i in range(6):
    if tipo_conica == "Parábola":
        angle = st.sidebar.slider(f"Punto {i+1} (parámetro t)", t_min, t_max, default_angles[i], 0.1)
    else:
        angle = st.sidebar.slider(f"Punto {i+1} (rad/param)", t_min, t_max, default_angles[i], 0.1)
    puntos_t.append(angle)

# Opciones de visualización
st.sidebar.subheader("Opciones de Visualización")
show_tangent_points = st.sidebar.checkbox("Mostrar puntos de tangencia", True)
show_tangent_lines = st.sidebar.checkbox("Mostrar líneas tangentes", True)
show_labels = st.sidebar.checkbox("Mostrar etiquetas", True)

# --- Funciones Matemáticas ---
def get_conic_point(t, a, b, conic_type, p=1.0):
    """Obtiene un punto en la cónica según el parámetro t."""
    if conic_type in ["Círculo", "Elipse"]:
        x = a * np.cos(t)
        y = b * np.sin(t)
    elif conic_type == "Parábola":
        # Parábola: y^2 = 4px, parametrizada como (t^2, 2pt)
        x = t**2 / (4*p)
        y = t
    else:  # Hipérbola
        # Hipérbola: x^2/a^2 - y^2/b^2 = 1
        # Parametrización: x = a*cosh(t), y = b*sinh(t) (rama derecha)
        if abs(t) < 1.5:  # Rama derecha
            x = a * np.cosh(t)
            y = b * np.sinh(t)
        else:  # Rama izquierda
            x = -a * np.cosh(t)
            y = b * np.sinh(t)
    return np.array([x, y])

def get_tangent_line(t, a, b, conic_type, p=1.0):
    """Retorna la línea tangente en forma [A, B, C] donde Ax + By + C = 0."""
    point = get_conic_point(t, a, b, conic_type, p)
    x0, y0 = point[0], point[1]
    
    if conic_type in ["Círculo", "Elipse"]:
        # Ecuación de tangente a elipse: (x*x0)/a^2 + (y*y0)/b^2 = 1
        A = x0 / (a**2)
        B = y0 / (b**2)
        C = -1
    elif conic_type == "Parábola":
        # Tangente a parábola y^2 = 4px en (x0, y0): yy0 = 2p(x + x0)
        # Reescrito: -2p*x + y0*y - 2p*x0 = 0
        if abs(y0) < 0.01:  # Evitar división por cero
            A = 1
            B = 0
            C = -x0
        else:
            A = -2*p / y0
            B = 1
            C = -2*p*x0 / y0
    else:  # Hipérbola
        # Tangente a hipérbola x^2/a^2 - y^2/b^2 = 1 en (x0, y0): xx0/a^2 - yy0/b^2 = 1
        A = x0 / (a**2)
        B = -y0 / (b**2)
        C = -1
    
    return np.array([A, B, C])

def get_intersection(line1, line2):
    """Halla el punto de intersección de dos líneas usando coordenadas homogéneas."""
    # Producto cruz de las dos líneas
    p = np.cross(line1, line2)
    if abs(p[2]) < 1e-10:  # Líneas paralelas
        return None
    return np.array([p[0]/p[2], p[1]/p[2]])

def line_from_points(p1, p2):
    """Crea una línea a partir de dos puntos."""
    return np.cross([p1[0], p1[1], 1], [p2[0], p2[1], 1])

def draw_line_segment(ax, line, xlim, color='black', linestyle='-', linewidth=1, label=None):
    """Dibuja un segmento de línea dentro de los límites especificados."""
    A, B, C = line
    if abs(B) > 1e-10:  # La línea no es vertical
        x_vals = np.array(xlim)
        y_vals = -(A * x_vals + C) / B
    else:  # Línea vertical
        x_vals = np.array([-C/A, -C/A])
        y_vals = np.array([xlim[0], xlim[1]])
    
    ax.plot(x_vals, y_vals, color=color, linestyle=linestyle, linewidth=linewidth, 
            label=label, alpha=0.3)

# --- Lógica de Dibujo ---
fig, ax = plt.subplots(figsize=(10, 10))

# 1. Dibujar la cónica
if tipo_conica == "Círculo":
    circle = Circle((0, 0), a, color='lightblue', fill=False, linestyle='--', linewidth=2)
    ax.add_patch(circle)
elif tipo_conica == "Elipse":
    ellipse = Ellipse((0, 0), 2*a, 2*b, color='lightblue', fill=False, linestyle='--', linewidth=2)
    ax.add_patch(ellipse)
elif tipo_conica == "Parábola":
    # Parábola: y^2 = 4px
    y_vals = np.linspace(-6, 6, 200)
    x_vals = y_vals**2 / (4*p)
    ax.plot(x_vals, y_vals, 'b--', linewidth=2, color='lightblue')
else:  # Hipérbola
    # Hipérbola: x^2/a^2 - y^2/b^2 = 1
    t_vals = np.linspace(-2, 2, 200)
    # Rama derecha
    x_right = a * np.cosh(t_vals)
    y_right = b * np.sinh(t_vals)
    ax.plot(x_right, y_right, 'b--', linewidth=2, color='lightblue')
    # Rama izquierda
    x_left = -a * np.cosh(t_vals)
    y_left = b * np.sinh(t_vals)
    ax.plot(x_left, y_left, 'b--', linewidth=2, color='lightblue')

# 2. Calcular puntos de tangencia
tangent_points = [get_conic_point(t, a, b, tipo_conica, p) for t in puntos_t]

# 3. Calcular líneas tangentes
tangentes = [get_tangent_line(t, a, b, tipo_conica, p) for t in puntos_t]

# 4. Calcular vértices del hexágono (intersecciones de tangentes consecutivas)
vertices = []
for i in range(6):
    v = get_intersection(tangentes[i], tangentes[(i + 1) % 6])
    if v is not None:
        vertices.append(v)
    else:
        st.error("⚠️ Algunas tangentes son paralelas. Ajusta los puntos de tangencia.")
        st.stop()

vertices = np.array(vertices)

# 5. Dibujar líneas tangentes (extendidas)
if show_tangent_lines:
    if tipo_conica == "Parábola":
        xlim_range = [-2, max([p[0] for p in tangent_points]) * 1.5]
    elif tipo_conica == "Hipérbola":
        xlim_range = [-max(a, b)*3, max(a, b)*3]
    else:
        xlim_range = [-max(a, b)*2, max(a, b)*2]
    for i, line in enumerate(tangentes):
        draw_line_segment(ax, line, xlim_range, color='gray', linestyle=':', linewidth=1)

# 6. Dibujar Hexágono
hex_x = np.append(vertices[:, 0], vertices[0, 0])
hex_y = np.append(vertices[:, 1], vertices[0, 1])
ax.plot(hex_x, hex_y, 'b-', label="Hexágono circunscrito", linewidth=2, alpha=0.8)

# Dibujar vértices del hexágono
ax.plot(vertices[:, 0], vertices[:, 1], 'bo', markersize=8, label="Vértices")

# 7. Dibujar puntos de tangencia
if show_tangent_points:
    for i, point in enumerate(tangent_points):
        ax.plot(point[0], point[1], 'rs', markersize=8)
        if show_labels:
            ax.text(point[0], point[1], f'  T{i+1}', fontsize=9, ha='left')

# 8. Calcular y dibujar las tres diagonales principales (vértices opuestos)
diag_col = ['red', 'green', 'orange']
diagonal_lines = []

for i in range(3):
    ax.plot([vertices[i, 0], vertices[i+3, 0]], 
            [vertices[i, 1], vertices[i+3, 1]], 
            color=diag_col[i], linestyle='-', linewidth=2, alpha=0.7,
            label=f"Diagonal {i+1}")
    
    # Guardar la línea de la diagonal
    diag_line = line_from_points(vertices[i], vertices[i+3])
    diagonal_lines.append(diag_line)

# 9. Calcular el Punto de Brianchon (intersección de las diagonales)
# Intersectar diagonal 1 con diagonal 2
brianchon_point = get_intersection(diagonal_lines[0], diagonal_lines[1])

if brianchon_point is not None:
    # Verificar que la tercera diagonal también pase por este punto
    dist_to_line3 = abs(np.dot(diagonal_lines[2], [brianchon_point[0], brianchon_point[1], 1]))
    
    if dist_to_line3 < 0.1:  # Tolerancia para considerar concurrencia
        ax.plot(brianchon_point[0], brianchon_point[1], 'go', markersize=15, 
                label='Punto de Brianchon', zorder=5)
        ax.plot(brianchon_point[0], brianchon_point[1], 'g*', markersize=20, zorder=6)
        
        st.success(f"✅ **Las diagonales son concurrentes!** Punto de Brianchon: ({brianchon_point[0]:.2f}, {brianchon_point[1]:.2f})")
        st.metric("Distancia a la 3ª diagonal", f"{dist_to_line3:.6f}")
    else:
        ax.plot(brianchon_point[0], brianchon_point[1], 'ro', markersize=12, 
                label='Intersección D1-D2')
        st.warning(f"⚠️ Pequeña desviación detectada. Distancia: {dist_to_line3:.6f}")
else:
    st.error("❌ No se pudo calcular el punto de Brianchon (diagonales paralelas)")

# 10. Etiquetas de vértices
if show_labels:
    for i, v in enumerate(vertices):
        ax.text(v[0], v[1], f'  V{i+1}', fontsize=10, fontweight='bold', ha='left')

# 11. Estética del gráfico
if tipo_conica == "Parábola":
    # Para parábola, ajustar límites basados en los vértices
    x_coords = [v[0] for v in vertices]
    y_coords = [v[1] for v in vertices]
    x_margin = (max(x_coords) - min(x_coords)) * 0.3
    y_margin = (max(y_coords) - min(y_coords)) * 0.3
    ax.set_xlim(min(x_coords) - x_margin, max(x_coords) + x_margin)
    ax.set_ylim(min(y_coords) - y_margin, max(y_coords) + y_margin)
elif tipo_conica == "Hipérbola":
    plot_limit = max(a, b) * 3.5
    ax.set_xlim(-plot_limit, plot_limit)
    ax.set_ylim(-plot_limit, plot_limit)
else:
    plot_limit = max(a, b) * 2.5
    ax.set_xlim(-plot_limit, plot_limit)
    ax.set_ylim(-plot_limit, plot_limit)
ax.set_aspect('equal')
ax.grid(True, which='both', linestyle='--', alpha=0.3)
ax.axhline(y=0, color='k', linewidth=0.5, alpha=0.3)
ax.axvline(x=0, color='k', linewidth=0.5, alpha=0.3)
ax.legend(loc='upper right', fontsize=9)
ax.set_title(f'Teorema de Brianchon - {tipo_conica}', fontsize=14, fontweight='bold')

st.pyplot(fig)

# --- Información adicional ---
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Información")
    st.write(f"**Tipo de cónica:** {tipo_conica}")
    if tipo_conica == "Parábola":
        st.write(f"**Parámetro focal:** p = {p:.2f}")
        st.write(f"**Ecuación:** y² = {4*p:.2f}x")
    elif tipo_conica == "Hipérbola":
        st.write(f"**Parámetros:** a = {a:.2f}, b = {b:.2f}")
        st.write(f"**Ecuación:** x²/{a**2:.2f} - y²/{b**2:.2f} = 1")
    elif tipo_conica == "Círculo":
        st.write(f"**Radio:** r = {a:.2f}")
        st.write(f"**Ecuación:** x² + y² = {a**2:.2f}")
    else:
        st.write(f"**Parámetros:** a = {a:.2f}, b = {b:.2f}")
        st.write(f"**Ecuación:** x²/{a**2:.2f} + y²/{b**2:.2f} = 1")
    st.write(f"**Número de vértices:** {len(vertices)}")

with col2:
    st.subheader("🎯 Sobre el Teorema")
    st.markdown("""
    - El teorema es el dual proyectivo del **Teorema de Pascal**
    - Funciona para cualquier sección cónica (círculo, elipse, parábola, hipérbola)
    - Las diagonales conectan los vértices opuestos del hexágono
    - El punto de concurrencia se llama **Punto de Brianchon**
    """)