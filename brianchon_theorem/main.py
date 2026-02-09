import matplotlib
# Intentar backends interactivos en orden de preferencia
for backend in ['Qt5Agg', 'TkAgg', 'GTK3Agg', 'WXAgg']:
    try:
        matplotlib.use(backend)
        break
    except:
        continue

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons, Slider, CheckButtons
from matplotlib.patches import Ellipse, Circle
import json
from datetime import datetime

class BrianchonInteractive:
    def __init__(self, conic_type='circle'):
        self.conic_type = conic_type
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        plt.subplots_adjust(left=0.25, bottom=0.25, right=0.95, top=0.95)
        
        # Parámetros de las cónicas
        self.conic_params = {
            'circle': {'a': 1.0, 'b': 1.0},
            'ellipse': {'a': 2.0, 'b': 1.0},
            'parabola': {'p': 1.0},
            'hyperbola': {'a': 1.0, 'b': 1.0}
        }
        
        # Inicializar ángulos (4 puntos para cuadrilátero)
        self.angles = np.array([0, np.pi/2, np.pi, 3*np.pi/2])
        
        # Variables para puntos de tangencia
        self.tangent_points = []
        
        # Opciones de visualización
        self.show_tangents = True
        self.show_labels = True
        self.show_info = True
        self.dark_mode = False
        
        # Crear interfaz
        self.setup_ui()
        self.update_plot()
        
    def setup_ui(self):
        # Botones para seleccionar tipo de cónica
        ax_radio = plt.axes([0.02, 0.75, 0.15, 0.20])
        self.radio = RadioButtons(ax_radio, ('Círculo', 'Elipse', 'Parábola', 'Hipérbola'))
        self.radio.on_clicked(self.change_conic)
        
        # Sliders para parámetros de la cónica
        ax_slider_a = plt.axes([0.02, 0.67, 0.15, 0.03])
        self.slider_a = Slider(ax_slider_a, 'Parámetro a', 0.5, 3.0, valinit=1.0)
        self.slider_a.on_changed(self.update_params)
        
        ax_slider_b = plt.axes([0.02, 0.62, 0.15, 0.03])
        self.slider_b = Slider(ax_slider_b, 'Parámetro b', 0.5, 3.0, valinit=1.0)
        self.slider_b.on_changed(self.update_params)
        
        # Sliders para controlar los 4 puntos de tangencia
        self.angle_sliders = []
        slider_positions = [0.54, 0.49, 0.44, 0.39]
        for i, pos in enumerate(slider_positions):
            ax_angle = plt.axes([0.02, pos, 0.15, 0.03])
            slider = Slider(ax_angle, f'Punto {i+1}', 0, 2*np.pi, valinit=self.angles[i])
            slider.on_changed(self.update_angle)
            self.angle_sliders.append(slider)
        
        # Checkboxes para opciones de visualización
        ax_check = plt.axes([0.02, 0.24, 0.15, 0.12])
        self.check = CheckButtons(ax_check, 
            ['Tangentes', 'Etiquetas', 'Info', 'Modo oscuro'],
            [self.show_tangents, self.show_labels, self.show_info, self.dark_mode])
        self.check.on_clicked(self.toggle_options)
        
        # Botones de acción
        ax_reset = plt.axes([0.02, 0.17, 0.15, 0.04])
        self.btn_reset = Button(ax_reset, 'Reset Puntos')
        self.btn_reset.on_clicked(self.reset)
        
        ax_save = plt.axes([0.02, 0.12, 0.15, 0.04])
        self.btn_save = Button(ax_save, 'Guardar PNG')
        self.btn_save.on_clicked(self.save_figure)
        
        ax_export = plt.axes([0.02, 0.07, 0.15, 0.04])
        self.btn_export = Button(ax_export, 'Exportar JSON')
        self.btn_export.on_clicked(self.export_data)
        
    def get_conic_point(self, angle):
        """Obtiene un punto en la cónica según el ángulo paramétrico."""
        if self.conic_type == 'circle':
            a = self.conic_params['circle']['a']
            return np.array([a * np.cos(angle), a * np.sin(angle)])
        
        elif self.conic_type == 'ellipse':
            a = self.conic_params['ellipse']['a']
            b = self.conic_params['ellipse']['b']
            return np.array([a * np.cos(angle), b * np.sin(angle)])
        
        elif self.conic_type == 'parabola':
            # Parábola: x = t, y = t²/(4p)
            p = self.conic_params['parabola']['p']
            t = np.tan(angle - np.pi/2) * 2 * p
            return np.array([t, t**2 / (4*p)])
        
        elif self.conic_type == 'hyperbola':
            # Hipérbola: x²/a² - y²/b² = 1
            a = self.conic_params['hyperbola']['a']
            b = self.conic_params['hyperbola']['b']
            # Parametrización: (a*sec(t), b*tan(t))
            if -np.pi/2 < angle < np.pi/2:
                return np.array([a / np.cos(angle), b * np.tan(angle)])
            else:
                return np.array([-a / np.cos(angle), b * np.tan(angle)])
    
    def get_tangent_line(self, angle):
        """Calcula la línea tangente en un ángulo dado (ax + by + c = 0)."""
        point = self.get_conic_point(angle)
        
        if self.conic_type == 'circle':
            # Tangente al círculo: x*x₀ + y*y₀ = r²
            a = self.conic_params['circle']['a']
            return np.array([point[0], point[1], -a**2])
        
        elif self.conic_type == 'ellipse':
            # Tangente a la elipse: xx₀/a² + yy₀/b² = 1
            a = self.conic_params['ellipse']['a']
            b = self.conic_params['ellipse']['b']
            return np.array([point[0]/a**2, point[1]/b**2, -1])
        
        elif self.conic_type == 'parabola':
            # Tangente a y² = 4px en (x₀,y₀): yy₀ = 2p(x + x₀)
            p = self.conic_params['parabola']['p']
            if abs(point[1]) < 0.01:
                return np.array([1, 0, -point[0]])
            return np.array([-2*p/point[1], 1, 2*p*point[0]/point[1]])
        
        elif self.conic_type == 'hyperbola':
            # Tangente: xx₀/a² - yy₀/b² = 1
            a = self.conic_params['hyperbola']['a']
            b = self.conic_params['hyperbola']['b']
            return np.array([point[0]/a**2, -point[1]/b**2, -1])
    
    def get_intersection(self, line1, line2):
        """Calcula la intersección de dos líneas."""
        p = np.cross(line1, line2)
        if abs(p[2]) < 1e-10:
            return np.array([np.inf, np.inf])
        return p[:2] / p[2]
    
    def line_from_points(self, p1, p2):
        """Crea una línea a partir de dos puntos."""
        return np.cross([p1[0], p1[1], 1], [p2[0], p2[1], 1])
    
    def update_plot(self):
        self.ax.clear()
        
        # Dibujar la cónica
        self.draw_conic()
        
        # Calcular puntos de tangencia
        self.tangent_points = [self.get_conic_point(a) for a in self.angles]
        
        # Calcular líneas tangentes
        tangents = [self.get_tangent_line(a) for a in self.angles]
        
        # Calcular vértices del cuadrilátero
        vertices = []
        for i in range(4):
            v = self.get_intersection(tangents[i], tangents[(i+1)%4])
            if not np.any(np.isinf(v)):
                vertices.append(v)
        
        if len(vertices) == 4:
            vertices = np.array(vertices)
            
            # Dibujar cuadrilátero
            quad_plot = np.vstack([vertices, vertices[0]])
            self.ax.plot(quad_plot[:,0], quad_plot[:,1], 'b-', linewidth=2, label='Cuadrilátero circunscrito')
            
            # Dibujar vértices
            self.ax.plot(vertices[:,0], vertices[:,1], 'bo', markersize=8)
            
            # Calcular diagonales
            diag1 = self.line_from_points(vertices[0], vertices[2])
            diag2 = self.line_from_points(vertices[1], vertices[3])
            
            # Dibujar diagonales
            self.ax.plot([vertices[0,0], vertices[2,0]], [vertices[0,1], vertices[2,1]], 
                        'r--', alpha=0.6, linewidth=1.5, label='Diagonales')
            self.ax.plot([vertices[1,0], vertices[3,0]], [vertices[1,1], vertices[3,1]], 
                        'r--', alpha=0.6, linewidth=1.5)
            
            # Calcular punto de Brianchon (intersección de diagonales)
            intersection_point = self.get_intersection(diag1, diag2)
            
            if not np.any(np.isinf(intersection_point)):
                self.ax.plot(intersection_point[0], intersection_point[1], 'o', 
                           color='green', markersize=12, label='Punto de Brianchon')
                
                self.ax.text(0.02, 0.98, "✓ Diagonales concurrentes", transform=self.ax.transAxes,
                           fontsize=14, verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='green', alpha=0.3))
        
        # Dibujar puntos de tangencia
        for i, point in enumerate(self.tangent_points):
            self.ax.plot(point[0], point[1], 'rs', markersize=10, 
                        label='Puntos tangencia' if i == 0 else '')
            if self.show_labels:
                self.ax.text(point[0], point[1], f'  P{i+1}', fontsize=10, 
                           verticalalignment='bottom')
        
        self.ax.axis('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc='upper right')
        self.ax.set_title(f'Teorema de Brianchon - {self.conic_type.capitalize()}\n'
                         '(Usa los sliders para mover los puntos de tangencia)',
                         fontsize=12)
        
        self.fig.canvas.draw_idle()
    
    def draw_conic(self):
        """Dibuja la cónica seleccionada."""
        if self.conic_type == 'circle':
            a = self.conic_params['circle']['a']
            circle = Circle((0, 0), a, color='lightgrey', fill=False, 
                          linestyle='--', linewidth=2)
            self.ax.add_patch(circle)
            self.ax.set_xlim(-3, 3)
            self.ax.set_ylim(-3, 3)
            
        elif self.conic_type == 'ellipse':
            a = self.conic_params['ellipse']['a']
            b = self.conic_params['ellipse']['b']
            ellipse = Ellipse((0, 0), 2*a, 2*b, color='lightgrey', 
                            fill=False, linestyle='--', linewidth=2)
            self.ax.add_patch(ellipse)
            self.ax.set_xlim(-4, 4)
            self.ax.set_ylim(-3, 3)
            
        elif self.conic_type == 'parabola':
            p = self.conic_params['parabola']['p']
            t = np.linspace(-4, 4, 200)
            x = t
            y = t**2 / (4*p)
            self.ax.plot(x, y, 'grey', linestyle='--', linewidth=2)
            self.ax.set_xlim(-5, 5)
            self.ax.set_ylim(-1, 6)
            
        elif self.conic_type == 'hyperbola':
            a = self.conic_params['hyperbola']['a']
            b = self.conic_params['hyperbola']['b']
            t = np.linspace(-2, 2, 200)
            x_pos = a * np.cosh(t)
            y_pos = b * np.sinh(t)
            x_neg = -a * np.cosh(t)
            self.ax.plot(x_pos, y_pos, 'grey', linestyle='--', linewidth=2)
            self.ax.plot(x_neg, y_pos, 'grey', linestyle='--', linewidth=2)
            self.ax.set_xlim(-5, 5)
            self.ax.set_ylim(-5, 5)
    
    def update_angle(self, val):
        """Actualiza los ángulos cuando los sliders cambian."""
        for i, slider in enumerate(self.angle_sliders):
            self.angles[i] = slider.val
        self.update_plot()
    
    def change_conic(self, label):
        conic_map = {
            'Círculo': 'circle',
            'Elipse': 'ellipse',
            'Parábola': 'parabola',
            'Hipérbola': 'hyperbola'
        }
        self.conic_type = conic_map.get(label, label.lower())
        self.angles = np.array([0, np.pi/2, np.pi, 3*np.pi/2])
        for i, slider in enumerate(self.angle_sliders):
            slider.set_val(self.angles[i])
        self.update_plot()
    
    def update_params(self, val):
        """Actualiza los parámetros de la cónica cuando los sliders cambian."""
        if self.conic_type == 'circle':
            self.conic_params['circle']['a'] = self.slider_a.val
            self.conic_params['circle']['b'] = self.slider_a.val
        elif self.conic_type == 'ellipse':
            self.conic_params['ellipse']['a'] = self.slider_a.val
            self.conic_params['ellipse']['b'] = self.slider_b.val
        elif self.conic_type == 'parabola':
            self.conic_params['parabola']['p'] = self.slider_a.val
        elif self.conic_type == 'hyperbola':
            self.conic_params['hyperbola']['a'] = self.slider_a.val
            self.conic_params['hyperbola']['b'] = self.slider_b.val
        self.update_plot()
    
    def toggle_options(self, label):
        """Maneja los cambios en las opciones de visualización."""
        if label == 'Tangentes':
            self.show_tangents = not self.show_tangents
        elif label == 'Etiquetas':
            self.show_labels = not self.show_labels
        elif label == 'Info':
            self.show_info = not self.show_info
        elif label == 'Modo oscuro':
            self.dark_mode = not self.dark_mode
            if self.dark_mode:
                self.fig.patch.set_facecolor('#2e2e2e')
                self.ax.set_facecolor('#2e2e2e')
                self.ax.spines['bottom'].set_color('white')
                self.ax.spines['top'].set_color('white')
                self.ax.spines['left'].set_color('white')
                self.ax.spines['right'].set_color('white')
                self.ax.tick_params(colors='white')
                self.ax.xaxis.label.set_color('white')
                self.ax.yaxis.label.set_color('white')
                self.ax.title.set_color('white')
            else:
                self.fig.patch.set_facecolor('white')
                self.ax.set_facecolor('white')
                self.ax.spines['bottom'].set_color('black')
                self.ax.spines['top'].set_color('black')
                self.ax.spines['left'].set_color('black')
                self.ax.spines['right'].set_color('black')
                self.ax.tick_params(colors='black')
                self.ax.xaxis.label.set_color('black')
                self.ax.yaxis.label.set_color('black')
                self.ax.title.set_color('black')
        self.update_plot()
    
    def reset(self, event):
        self.angles = np.array([0, np.pi/2, np.pi, 3*np.pi/2])
        for i, slider in enumerate(self.angle_sliders):
            slider.set_val(self.angles[i])
        self.update_plot()
    
    def save_figure(self, event):
        filename = f'brianchon_{self.conic_type}.png'
        self.fig.savefig(filename, dpi=300, bbox_inches='tight')
        print(f'Figura guardada como {filename}')
    
    def export_data(self, event):
        """Exporta la configuración actual a un archivo JSON."""
        data = {
            'timestamp': datetime.now().isoformat(),
            'conic_type': self.conic_type,
            'conic_params': self.conic_params[self.conic_type],
            'angles': self.angles.tolist(),
            'options': {
                'show_tangents': self.show_tangents,
                'show_labels': self.show_labels,
                'show_info': self.show_info,
                'dark_mode': self.dark_mode
            }
        }
        filename = f'brianchon_{self.conic_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f'Datos exportados a {filename}')

# Iniciar la aplicación interactiva
if __name__ == '__main__':
    app = BrianchonInteractive()
    plt.show()