import numpy as np
import matplotlib.pyplot as plt

def get_intersection(line1, line2):
    """Calcula la intersección de dos líneas usando producto cruz (coordenadas homogéneas)."""
    p = np.cross(line1, line2)

    return p[:2] / p[2]

def get_tangent(angle):
    """Retorna la línea tangente al círculo unitario en un ángulo dado (ax + by + c = 0)."""
    # Punto de tangencia: (cos(a), sin(a))
    # Ecuación: cos(a)x + sin(a)y - 1 = 0 -> Coeficientes: [cos(a), sin(a), -1]

    return np.array([np.cos(angle), np.sin(angle), -1])


# 1. Generar 6 ángulos aleatorios y ordenarlos para formar un hexágono convexo
angles = np.sort(np.random.uniform(0, 2*np.pi, 6))

# 2. Obtener las 6 líneas tangentes
tangents = [get_tangent(a) for a in angles]

# 3. Calcular los vértices del hexágono (intersección de tangentes consecutivas)
vertices = []

for i in range(6):
    v = get_intersection(tangents[i], tangents[(i+1)%6])

    vertices.append(v)

vertices = np.array(vertices)

# 4. Definir las 3 diagonales principales: (V0-V3), (V1-V4), (V2-V5)
def line_from_points(p1, p2):
    return np.cross([p1[0], p1[1], 1], [p2[0], p2[1], 1])

diag1 = line_from_points(vertices[0], vertices[3])
diag2 = line_from_points(vertices[1], vertices[4])
diag3 = line_from_points(vertices[2], vertices[5])

# 5. Verificar concurrencia: el punto de intersección de diag1 y diag2 debe estar en diag3
intersection_point = get_intersection(diag1, diag2)
is_on_diag3 = np.isclose(np.dot(diag3, [intersection_point[0], intersection_point[1], 1]), 0)

print(f"¿Las diagonales son concurrentes?: {is_on_diag3}")

# Visualización
plt.figure(figsize=(8,8))
circle = plt.Circle((0, 0), 1, color='lightgrey', fill=False, linestyle='--')
plt.gca().add_patch(circle)

# Dibujar hexágono
hex_plot = np.vstack([vertices, vertices[0]])
plt.plot(hex_plot[:,0], hex_plot[:,1], 'b-', label='Hexágono circunscrito')

# Dibujar diagonales
plt.plot([vertices[0,0], vertices[3,0]], [vertices[0,1], vertices[3,1]], 'r--', alpha=0.6)
plt.plot([vertices[1,0], vertices[4,0]], [vertices[1,1], vertices[4,1]], 'r--', alpha=0.6)
plt.plot([vertices[2,0], vertices[5,0]], [vertices[2,1], vertices[5,1]], 'r--', alpha=0.6)

# Punto de concurrencia
plt.plot(intersection_point[0], intersection_point[1], 'ko', label='Punto de Brianchon')

plt.axis('equal')
plt.legend()
plt.title("Verificación del Teorema de Brianchon")
plt.savefig('brianchon_theorem.png', dpi=300, bbox_inches='tight')
print("Figura guardada como 'brianchon_theorem.png'")