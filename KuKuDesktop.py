import sys
import os
import random
import keyboard
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QGridLayout, QFrame, QLineEdit, 
                             QDialog, QStackedWidget, QTextBrowser, QComboBox)
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtGui import QFont, QCloseEvent
# Componentes nativos de audio
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput 
from PyQt6.QtMultimedia import QSoundEffect

# --- CONFIGURACIÓN Y CONTROL PARENTAL ---
class PanelConfiguracion(QDialog):
    def __init__(self, ruta_pin, parent=None):
        super().__init__(parent)
        self.ruta_pin = ruta_pin
        self.setWindowTitle("Configuración Parental")
        self.setFixedSize(340, 280)
        self.setStyleSheet("background-color: #FFFFFF; border-radius: 15px;")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.layout_principal = QVBoxLayout()
        
        # Estado de la ventana: False = Validando acceso, True = Dentro de los ajustes
        self.acceso_concedido = False 
        
        # Título / Instrucciones
        self.label_titulo = QLabel("🔒 Área Protegida\nIngresa el PIN actual para entrar:")
        self.label_titulo.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.label_titulo.setStyleSheet("color: #2C3E50; background: transparent;") 
        self.label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_principal.addWidget(self.label_titulo)
        
        # Casilla para ingresar contraseñas
        self.input_texto = QLineEdit()
        self.input_texto.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_texto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_texto.setFont(QFont("Arial", 14))
        self.input_texto.setPlaceholderText("PIN Actual")
        self.input_texto.setStyleSheet("border: 2px solid #BDC3C7; padding: 5px; border-radius: 5px; color: #2C3E50; margin: 10px 0px;")
        self.layout_principal.addWidget(self.input_texto)
        
        # Botonera de acción principal
        self.botones_layout = QHBoxLayout()
        self.btn_accion = QPushButton("Entrar")
        self.btn_accion.setStyleSheet("background-color: #34495E; color: white; padding: 8px; font-weight: bold; border-radius: 5px;")
        self.btn_accion.clicked.connect(self.procesar_boton_principal)
        
        self.btn_cancelar = QPushButton("Cerrar")
        self.btn_cancelar.setStyleSheet("background-color: #7F8C8D; color: white; padding: 8px; font-weight: bold; border-radius: 5px;")
        self.btn_cancelar.clicked.connect(self.reject)
        
        self.botones_layout.addWidget(self.btn_accion)
        self.botones_layout.addWidget(self.btn_cancelar)
        self.layout_principal.addLayout(self.botones_layout)
        
        self.setLayout(self.layout_principal)
        
    def obtener_pin_actual(self):
        try:
            if os.path.exists(self.ruta_pin):
                with open(self.ruta_pin, "r", encoding="utf-8") as f:
                    return f.read().strip()
        except Exception:
            pass
        return "1234"
        
    def procesar_boton_principal(self):
        """Maneja el flujo del panel dependiendo de si está validando o guardando."""
        if not self.acceso_concedido:
            # FASE 1: Verificar antes de mostrar ajustes
            if self.input_texto.text() == self.obtener_pin_actual():
                self.mostrar_menu_ajustes()
            else:
                self.label_titulo.setText("❌ PIN Incorrecto.\nIntenta de nuevo:")
                self.label_titulo.setStyleSheet("color: #E74C3C; font-weight: bold;")
                self.input_texto.clear()
        else:
            # FASE 2: Si ya está adentro, este botón sirve para guardar el nuevo PIN
            self.guardar_nuevo_pin()

    def mostrar_menu_ajustes(self):
        """Transforma la interfaz gráfica en el menú de configuración."""
        self.acceso_concedido = True
        self.input_texto.clear()
        self.input_texto.setPlaceholderText("Escribe el NUEVO PIN")
        
        self.label_titulo.setText("⚙️ Panel de Configuración\nIngresa tu nueva contraseña:")
        self.label_titulo.setStyleSheet("color: #2980B9; font-weight: bold;")
        
        self.btn_accion.setText("💾 Guardar PIN")
        self.btn_accion.setStyleSheet("background-color: #27AE60; color: white; padding: 8px; font-weight: bold; border-radius: 5px;")

    def guardar_nuevo_pin(self):
        nuevo_pin = self.input_texto.text().strip()
        if len(nuevo_pin) >= 4:
            try:
                with open(self.ruta_pin, "w", encoding="utf-8") as f:
                    f.write(nuevo_pin)
                self.label_titulo.setText("✅ ¡Contraseña actualizada!")
                self.label_titulo.setStyleSheet("color: #27AE60; font-weight: bold;")
                self.input_texto.setVisible(False)
                self.btn_accion.setVisible(False)
                QTimer.singleShot(1500, self.accept) 
            except Exception:
                self.label_titulo.setText("Error al escribir el archivo.")
        else:
            self.label_titulo.setText("⚠️ El PIN debe tener 4 dígitos o más:")
            self.label_titulo.setStyleSheet("color: #E67E22; font-weight: bold;")

# --- DIÁLOGO RÁPIDO PARA SALIR ---
class DialogoSalir(QDialog):
    def __init__(self, ruta_pin, parent=None):
        super().__init__(parent)
        self.ruta_pin = ruta_pin
        self.setFixedSize(300, 200)
        self.setStyleSheet("background-color: #FFFFFF; border-radius: 15px;")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        
        layout = QVBoxLayout()
        self.label = QLabel("Ingresa el PIN para salir:")
        self.label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.label.setStyleSheet("color: #2C3E50;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        self.input_pin = QLineEdit()
        self.input_pin.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_pin.setFont(QFont("Arial", 14))
        
        # CORRECCIÓN: Agregamos "color: #2C3E50;" para forzar a que los puntos sean visibles
        self.input_pin.setStyleSheet("border: 2px solid #BDC3C7; padding: 5px; border-radius: 5px; color: #2C3E50; background-color: #FFFFFF;")

        layout.addWidget(self.input_pin)
        
        botones = QHBoxLayout()
        btn_ok = QPushButton("Salir")
        btn_ok.setStyleSheet("background-color: #E74C3C; color: white; padding: 8px; font-weight: bold; border-radius: 5px;")
        btn_ok.clicked.connect(self.verificar_y_salir)
        
        btn_cancel = QPushButton("Volver")
        btn_cancel.setStyleSheet("background-color: #BDC3C7; color: #2C3E50; padding: 8px; font-weight: bold; border-radius: 5px;")
        btn_cancel.clicked.connect(self.reject)
        
        botones.addWidget(btn_ok)
        botones.addWidget(btn_cancel)
        layout.addLayout(botones)
        self.setLayout(layout)
        
    def verificar_y_salir(self):
        try:
            with open(self.ruta_pin, "r", encoding="utf-8") as f:
                pin_correcto = f.read().strip()
        except Exception:
            pin_correcto = "1234"
            
        if self.input_pin.text() == pin_correcto:
            self.accept()
        else:
            self.label.setText("❌ PIN Incorrecto:")
            self.label.setStyleSheet("color: #E74C3C; font-weight: bold;")
            self.input_pin.clear()

# --- COMPONENTE INTERNO: JUEGO DE LA MEMORIA ---
class MemoriaGame(QWidget):
    def __init__(self, callback_volver):
        super().__init__()
        layout_principal = QVBoxLayout()
        
        btn_volver = QPushButton("⬅ Volver al Menú")
        btn_volver.setFixedSize(180, 50)
        btn_volver.setStyleSheet("background-color: #607D8B; color: white; font-size: 16px; font-weight: bold; border-radius: 15px;")
        btn_volver.clicked.connect(callback_volver)
        layout_principal.addWidget(btn_volver, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.label_estado = QLabel("¡Encuentra las parejas de animales! 🐾")
        self.label_estado.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        self.label_estado.setStyleSheet("color: #2C3E50; margin-bottom: 10px; background: transparent;")
        self.label_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_principal.addWidget(self.label_estado)
        
        self.grilla_tablero = QGridLayout()
        layout_principal.addLayout(self.grilla_tablero)
        
        self.btn_reiniciar = QPushButton("🔄 Reiniciar Juego")
        self.btn_reiniciar.setFixedSize(200, 50)
        self.btn_reiniciar.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px; font-weight: bold; border-radius: 12px;")
        self.btn_reiniciar.clicked.connect(self.iniciar_juego)
        layout_principal.addWidget(self.btn_reiniciar, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout_principal)
        
        self.botones = []
        self.valores = []
        self.primera_carta = None
        self.segunda_carta = None
        self.bloqueo_tablero = False
        
        self.timer_ocultar = QTimer()
        self.timer_ocultar.setSingleShot(True)
        self.timer_ocultar.timeout.connect(self.ocultar_pareja)
        
        self.iniciar_juego()

    def iniciar_juego(self):
        for btn in self.botones:
            self.grilla_tablero.removeWidget(btn)
            btn.deleteLater()
        
        self.botones = []
        self.primera_carta = None
        self.segunda_carta = None
        self.bloqueo_tablero = False
        self.label_estado.setText("¡Encuentra las parejas de animales! 🐾")
        self.label_estado.setStyleSheet("color: #2C3E50; margin-bottom: 10px; background: transparent;")
        
        emojis = ["🐱", "🐶", "🦁", "🐸", "🐵", "🦊", "🐼", "🐷"] * 2
        random.shuffle(emojis)
        self.valores = emojis
        
        posiciones = [(r, c) for r in range(4) for c in range(4)]
        for row, col in posiciones:
            btn = QPushButton("❓")
            btn.setFixedSize(110, 110)
            btn.setFont(QFont("Arial", 28))
            btn.setStyleSheet("""
                QPushButton { 
                    background-color: #34495E; color: white; 
                    border-radius: 20px; border: 4px solid white; 
                }
                QPushButton:hover { background-color: #2C3E50; }
            """)
            btn.clicked.connect(lambda checked, b=btn: self.carta_pulsada(b))
            
            self.grilla_tablero.addWidget(btn, row, col, alignment=Qt.AlignmentFlag.AlignCenter)
            self.botones.append(btn)

    def update_style(self, btn, style):
        btn.setStyleSheet(style)

    def carta_pulsada(self, btn_actual):
        if self.bloqueo_tablero:
            return
        
        if btn_actual.text() != "❓" or btn_actual == self.primera_carta:
            return
            
        idx = self.botones.index(btn_actual)
        btn_actual.setText(self.valores[idx])
        btn_actual.setStyleSheet("background-color: #FFFFFF; color: black; border-radius: 20px; border: 4px solid #4A90E2;")
        
        if not self.primera_carta:
            self.primera_carta = btn_actual
        else:
            self.segunda_carta = btn_actual
            self.verificar_pareja()

    def verificar_pareja(self):
        idx1 = self.botones.index(self.primera_carta)
        idx2 = self.botones.index(self.segunda_carta)
        
        if self.valores[idx1] == self.valores[idx2]:
            estilo_correcto = "background-color: #A2F3A4; color: black; border-radius: 20px; border: 4px solid #2ECC71;"
            self.primera_carta.setStyleSheet(estilo_correcto)
            self.segunda_carta.setStyleSheet(estilo_correcto)
            
            self.primera_carta = None
            self.segunda_carta = None
            
            if all(btn.text() != "❓" for btn in self.botones):
                self.label_estado.setText("🎉 ¡Felicidades! ¡Ganaste! 🎉")
                self.label_estado.setStyleSheet("color: #2ECC71; font-weight: bold; margin-bottom: 10px; background: transparent;")
        else:
            self.bloqueo_tablero = True
            self.timer_ocultar.start(800)

    def ocultar_pareja(self):
        estilo_oculto = "background-color: #34495E; color: white; border-radius: 20px; border: 4px solid white;"
        self.primera_carta.setText("❓")
        self.primera_carta.setStyleSheet(estilo_oculto)
        self.segunda_carta.setText("❓")
        self.segunda_carta.setStyleSheet(estilo_oculto)
        
        self.primera_carta = None
        self.segunda_carta = None
        self.bloqueo_tablero = False


# --- COMPONENTE INTERNO: JUEGO TRES EN RAYA ---
class TresEnRayaGame(QWidget):
    def __init__(self, callback_volver):
        super().__init__()
        layout_principal = QVBoxLayout()
        
        btn_volver = QPushButton("⬅ Volver al Menú")
        btn_volver.setFixedSize(180, 50)
        btn_volver.setStyleSheet("background-color: #607D8B; color: white; font-size: 16px; font-weight: bold; border-radius: 15px;")
        btn_volver.clicked.connect(callback_volver)
        layout_principal.addWidget(btn_volver, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.label_estado = QLabel("Turno de: ❌")
        self.label_estado.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.label_estado.setStyleSheet("color: #2C3E50; margin-bottom: 15px; background: transparent;")
        self.label_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_principal.addWidget(self.label_estado)
        
        self.grilla_tablero = QGridLayout()
        layout_principal.addLayout(self.grilla_tablero)
        
        self.btn_reiniciar = QPushButton("🔄 Reiniciar Partida")
        self.btn_reiniciar.setFixedSize(200, 50)
        self.btn_reiniciar.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px; font-weight: bold; border-radius: 12px;")
        self.btn_reiniciar.clicked.connect(self.iniciar_juego)
        layout_principal.addWidget(self.btn_reiniciar, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout_principal)
        
        self.botones = []
        self.turno = "❌"
        self.juego_activo = True
        
        self.iniciar_juego()

    def iniciar_juego(self):
        for btn in self.botones:
            self.grilla_tablero.removeWidget(btn)
            btn.deleteLater()
            
        self.botones = []
        self.turno = "❌"
        self.juego_activo = True
        self.label_estado.setText("Turno de: ❌")
        self.label_estado.setStyleSheet("color: #2C3E50; margin-bottom: 15px; background: transparent;")
        
        for row in range(3):
            for col in range(3):
                btn = QPushButton("")
                btn.setFixedSize(130, 130)
                btn.setFont(QFont("Arial", 36, QFont.Weight.Bold))
                btn.setStyleSheet("""
                    QPushButton { 
                        background-color: #FFFFFF; color: #2C3E50; 
                        border-radius: 15px; border: 3px solid #BDC3C7; 
                    }
                    QPushButton:hover { background-color: #ECF0F1; }
                """)
                btn.clicked.connect(lambda checked, b=btn: self.casilla_pulsada(b))
                self.grilla_tablero.addWidget(btn, row, col, alignment=Qt.AlignmentFlag.AlignCenter)
                self.botones.append(btn)

    def casilla_pulsada(self, btn):
        if not self.juego_activo or btn.text() != "":
            return
            
        btn.setText(self.turno)
        if self.turno == "❌":
            btn.setStyleSheet("background-color: #FFF0F0; color: #E74C3C; border-radius: 15px; border: 3px solid #E74C3C; font-size: 36px; font-weight: bold;")
        else:
            btn.setStyleSheet("background-color: #F0F8FF; color: #3498DB; border-radius: 15px; border: 3px solid #3498DB; font-size: 36px; font-weight: bold;")
            
        if self.verificar_ganador():
            self.label_estado.setText(f"🎉 ¡El jugador {self.turno} ha ganado! 🎉")
            self.label_estado.setStyleSheet("color: #2ECC71; font-weight: bold; margin-bottom: 15px; background: transparent;")
            self.juego_activo = False
            return
            
        if all(b.text() != "" for b in self.botones):
            self.label_estado.setText("🤝 ¡Es un empate! 🤝")
            self.label_estado.setStyleSheet("color: #7F8C8D; font-weight: bold; margin-bottom: 15px; background: transparent;")
            self.juego_activo = False
            return
            
        self.turno = "⭕" if self.turno == "❌" else "❌"
        self.label_estado.setText(f"Turno de: {self.turno}")

    def verificar_ganador(self):
        combinaciones = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], 
            [0, 3, 6], [1, 4, 7], [2, 5, 8], 
            [0, 4, 8], [2, 4, 6]             
        ]
        for c in combinaciones:
            if self.botones[c[0]].text() == self.botones[c[1]].text() == self.botones[c[2]].text() != "":
                return True
        return False

# --- COMPONENTE INTERNO: PIANO MUSICAL REALISTA ---
class PianoMusical(QWidget):
    def __init__(self, callback_volver):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(950, 550)
        
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(30, 30, 30, 30)
        
        btn_volver = QPushButton("⬅ Volver al Menú")
        btn_volver.setFixedSize(180, 50)
        btn_volver.setStyleSheet("background-color: #607D8B; color: white; font-size: 16px; font-weight: bold; border-radius: 15px;")
        btn_volver.clicked.connect(callback_volver)
        layout_principal.addWidget(btn_volver, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.label_estado = QLabel("🎹 ¡Mi Piano de Colores! ✨\n(Usa el mouse o los números del 1 al 8)")
        self.label_estado.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        self.label_estado.setStyleSheet("color: #2C3E50; margin-bottom: 25px; background: transparent;")
        self.label_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_principal.addWidget(self.label_estado)
        
        self.contenedor_teclado = QWidget()
        layout_rejilla = QGridLayout(self.contenedor_teclado)
        layout_rejilla.setSpacing(6)  
        layout_rejilla.setContentsMargins(10, 10, 10, 10)
        
        # Corrección: El color de DO+ se redujo a 6 dígitos válidos (#E91E62)
        self.notas_config = [
            {"nombre": "DO\n(1)", "archivo": "do.wav", "es_negra": False, "color": "#FF6B6B"},
            {"nombre": "RE\n(2)", "archivo": "re.wav", "es_negra": False, "color": "#FF9244"},
            {"nombre": "MI\n(3)", "archivo": "mi.wav", "es_negra": False, "color": "#FFC93C"},
            {"nombre": "FA\n(4)", "archivo": "fa.wav", "es_negra": False, "color": "#4E9F3D"},
            {"nombre": "SOL\n(5)", "archivo": "sol.wav", "es_negra": False, "color": "#1976D2"},
            {"nombre": "LA\n(6)", "archivo": "la.wav", "es_negra": False, "color": "#00BCD4"},
            {"nombre": "SI\n(7)", "archivo": "si.wav", "es_negra": False, "color": "#9C27B0"},
            {"nombre": "DO+\n(8)", "archivo": "do_alto.wav", "es_negra": False, "color": "#E91E62"},
            
            {"nombre": "DO#", "archivo": "do_sost.wav", "es_negra": True, "pos_bloque": 0},
            {"nombre": "RE#", "archivo": "re_sost.wav", "es_negra": True, "pos_bloque": 1},
            {"nombre": "FA#", "archivo": "fa_sost.wav", "es_negra": True, "pos_bloque": 3},
            {"nombre": "SOL#", "archivo": "sol_sost.wav", "es_negra": True, "pos_bloque": 4},
            {"nombre": "LA#", "archivo": "la_sost.wav", "es_negra": True, "pos_bloque": 5}
        ]

        ruta_base = os.path.dirname(os.path.abspath(__file__))
        self.ruta_piano = os.path.join(ruta_base, "Musica_KuKuDesktop")
        self.canales_audio = {}
        self.botones_teclas = {}
        
        indice_blanca = 0
        for nota in self.notas_config:
            if not nota["es_negra"]:
                btn = QPushButton(nota["nombre"])
                btn.setFixedHeight(340)      
                btn.setMinimumWidth(95)      
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {nota['color']}; color: white;
                        border: none;
                        border-radius: 20px;
                        font-size: 16px; font-weight: bold;
                    }}
                """)
                
                efecto = QSoundEffect()
                ruta_nota = os.path.join(self.ruta_piano, nota["archivo"])
                if os.path.exists(ruta_nota):
                    efecto.setSource(QUrl.fromLocalFile(ruta_nota))
                    efecto.setVolume(0.9)
                
                self.canales_audio[nota["nombre"]] = efecto
                self.botones_teclas[nota["nombre"]] = btn
                
                btn.clicked.connect(lambda checked, n=nota["nombre"]: self.tocar_nota(n))
                layout_rejilla.addWidget(btn, 0, indice_blanca * 3, 2, 3)
                indice_blanca += 1

        for nota in self.notas_config:
            if nota["es_negra"]:
                btn = QPushButton(nota["nombre"])
                btn.setFixedHeight(200)      
                btn.setMinimumWidth(55)      
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2F3640; color: #FFFFFF;
                        border: 3px solid white;
                        border-radius: 15px;
                        font-size: 11px; font-weight: bold;
                    }
                """)
                
                efecto = QSoundEffect()
                ruta_nota = os.path.join(self.ruta_piano, nota["archivo"])
                if os.path.exists(ruta_nota):
                    efecto.setSource(QUrl.fromLocalFile(ruta_nota))
                    efecto.setVolume(0.8)
                
                self.canales_audio[nota["nombre"]] = efecto
                self.botones_teclas[nota["nombre"]] = btn
                
                btn.clicked.connect(lambda checked, n=nota["nombre"]: self.tocar_nota(n))
                
                columna_negra = (nota["pos_bloque"] * 3) + 2
                layout_rejilla.addWidget(btn, 0, columna_negra, 1, 2, Qt.AlignmentFlag.AlignTop)
                btn.raise_()

        layout_principal.addWidget(self.contenedor_teclado, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_principal.addStretch()
        self.setLayout(layout_principal)

    def tocar_nota(self, nombre_nota):
        if nombre_nota in self.canales_audio:
            self.canales_audio[nombre_nota].play()
        
        if nombre_nota in self.botones_teclas:
            btn = self.botones_teclas[nombre_nota]
            es_negra = "#" in nombre_nota
            
            if es_negra:
                btn.setStyleSheet("background-color: #718093; color: white; border: 3px solid white; border-radius: 15px; font-size: 11px; font-weight: bold;")
                QTimer.singleShot(120, lambda: btn.setStyleSheet("background-color: #2F3640; color: white; border: 3px solid white; border-radius: 15px; font-size: 11px; font-weight: bold;"))
            else:
                color_original = next(nota["color"] for nota in self.notas_config if nota["nombre"] == nombre_nota)
                btn.setStyleSheet(f"background-color: #FFFFFF; color: {color_original}; border-radius: 20px; font-size: 16px; font-weight: bold;")
                QTimer.singleShot(120, lambda: btn.setStyleSheet(f"background-color: {color_original}; color: white; border-radius: 20px; font-size: 16px; font-weight: bold;"))

    def keyPressEvent(self, event):
        key = event.text()
        mapeo_teclado = {
            "1": "DO\n(1)", "2": "RE\n(2)", "3": "MI\n(3)", "4": "FA\n(4)", 
            "5": "SOL\n(5)", "6": "LA\n(6)", "7": "SI\n(7)", "8": "DO+\n(8)"
        }
        if key in mapeo_teclado:
            self.tocar_nota(mapeo_teclado[key])
        else:
            super().keyPressEvent(event)

# --- COMPONENTE INTERNO: SOUNDBOARD DE ANIMALES ---
class GranjaSonidos(QWidget):
    def __init__(self, callback_volver):
        super().__init__()
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(30, 30, 30, 30)
        
        btn_volver = QPushButton("⬅ Volver al Menú")
        btn_volver.setFixedSize(180, 50)
        btn_volver.setStyleSheet("background-color: #607D8B; color: white; font-size: 16px; font-weight: bold; border-radius: 15px;")
        btn_volver.clicked.connect(callback_volver)
        layout_principal.addWidget(btn_volver, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.label_estado = QLabel("🐾 ¡La Granja de Sonidos! 🐾\n(Presiona para escuchar a tus amigos)")
        self.label_estado.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        self.label_estado.setStyleSheet("color: #2C3E50; margin-bottom: 25px; background: transparent;")
        self.label_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_principal.addWidget(self.label_estado)
        
        grilla_animales = QGridLayout()
        grilla_animales.setSpacing(15)
        layout_principal.addLayout(grilla_animales)
        
        self.animales_config = [
            {"emoji": "🐱", "nombre": "Gatito", "archivo": "gato.mp3", "color": "#FFB7B2"},
            {"emoji": "🐶", "nombre": "Perrito", "archivo": "perro.mp3", "color": "#FFDAC1"},
            {"emoji": "🐸", "nombre": "Ranita", "archivo": "rana.mp3", "color": "#E2F0CB"},
            {"emoji": "🐥", "nombre": "Pollito", "archivo": "pollito.mp3", "color": "#FFF5BA"},
            {"emoji": "🦁", "nombre": "León", "archivo": "leon.mp3", "color": "#B5EAEA"},
            {"emoji": "🐮", "nombre": "Vaca", "archivo": "vaca.mp3", "color": "#C7CEEA"}
        ]
        
        ruta_base = os.path.dirname(os.path.abspath(__file__))
        self.ruta_sonidos = os.path.join(ruta_base, "Musica_KuKuDesktop")
        self.reproductores = {}
        self.salidas_audio = {}
        self.botones_animales = {}
        
        row, col = 0, 0
        for animal in self.animales_config:
            nombre_completo = f"{animal['emoji']}\n{animal['nombre']}"
            btn = QPushButton(nombre_completo)
            btn.setFixedSize(180, 180)
            btn.setFont(QFont("Arial", 20, QFont.Weight.Bold))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {animal['color']}; color: #2C3E50;
                    border: 4px solid white; border-radius: 25px;
                }}
            """)
            
            reproductor_mp3 = QMediaPlayer()
            salida_mp3 = QAudioOutput()
            reproductor_mp3.setAudioOutput(salida_mp3)
            salida_mp3.setVolume(0.8)
            
            ruta_completa = os.path.join(self.ruta_sonidos, animal["archivo"])
            if os.path.exists(ruta_completa):
                reproductor_mp3.setSource(QUrl.fromLocalFile(ruta_completa))
                
            self.reproductores[animal["nombre"]] = reproductor_mp3
            self.salidas_audio[animal["nombre"]] = salida_mp3
            self.botones_animales[animal["nombre"]] = btn
            
            btn.clicked.connect(lambda checked, a=animal: self.reproducir_sonido(a))
            grilla_animales.addWidget(btn, row, col, alignment=Qt.AlignmentFlag.AlignCenter)
            
            col += 1
            if col > 2:
                col = 0
                row += 1
                
        layout_principal.addStretch()
        self.setLayout(layout_principal)
        
    def reproducir_sonido(self, animal):
        nombre = animal["nombre"]
        if nombre in self.reproductores:
            self.reproductores[nombre].stop()
            self.reproductores[nombre].play()
        
        btn = self.botones_animales[nombre]
        # Corrección: Se fijó el font-size para evitar saltos bruscos en el texto
        btn.setStyleSheet(f"background-color: #FFFFFF; color: #2C3E50; border: 4px solid {animal['color']}; border-radius: 25px; font-size: 20px; font-weight: bold;")
        QTimer.singleShot(150, lambda: btn.setStyleSheet(f"background-color: {animal['color']}; color: #2C3E50; border: 4px solid white; border-radius: 25px; font-size: 20px; font-weight: bold;"))

# --- COMPONENTE INTERNO: JUEGO DE TRIVIA ---
class JuegoTrivia(QWidget):
    def __init__(self, callback_volver):
        super().__init__()
        self.callback_volver = callback_volver
        self.puntos = 0
        self.pregunta_actual = 0
        
        self.preguntas = [
            {"pregunta": "🐜 ¿Cómo se comunican las hormigas principalmente?", "opciones": ["Oliendo rastros químicos (feromonas)", "Cantando en voz alta", "Haciendo señas con los pies"], "correcta": 0},
            {"pregunta": "💻 En programación, ¿cuál es el animal que representa a Python?", "opciones": ["Un osito panda", "Una serpiente", "Un delfín saltarín"], "correcta": 1},
            {"pregunta": "🌍 ¿Cuál es el océano más grande de todo el planeta Tierra?", "opciones": ["Océano Atlántico", "Océano Índico", "Océano Pacífico"], "correcta": 2},
            {"pregunta": "🐸 ¿Por qué las ranas hacen sus ruidos tan particulares?", "opciones": ["Para hablar con los humanos", "Para llamar a sus amigos y cantar", "Porque les duele la pancita"], "correcta": 1},
            {"pregunta": "🚀 ¿Qué es lo que hace que brille una estrella en el espacio?", "opciones": ["Tiene un foco gigante adentro", "Es una enorme bola de gas quemándose", "Refleja la luz de un espejo"], "correcta": 1},
            {"pregunta": "❓ ¿Cuál es el animal más rápido del mundo?", "opciones": ["León", "Guepardo", "Antílope"], "correcta": 1},
            {"pregunta": "🎨 Si mezclas pintura de color Azul 🟦 y Amarillo 🟨, ¿qué color se forma?", "opciones": ["Morado 🟪", "Naranja 🟧", "Verde 🟩"], "correcta": 2},
            {"pregunta": "🦖 ¿Qué significa la palabra 'Dinosaurio'?", "opciones": ["Lagarto terrible", "Monstruo gigante", "Cazador veloz"], "correcta": 0},
            {"pregunta": "🍯 ¿Qué pequeños y trabajadores insectos fabrican la deliciosa miel?", "opciones": ["Las mariposas", "Las avispas", "Las abejas"], "correcta": 2},
            {"pregunta": "🌙 ¿Cuánto tiempo tarda la Tierra en darle una vuelta completa al Sol?", "opciones": ["Un mes entero", "Un año completo (365 días)", "Un día solito"], "correcta": 1},
            {"pregunta": "🐢 ¿Cuál es la característica más famosa de las tortugas?", "opciones": ["Su velocidad supersónica", "Su caparazón duro y protector", "Sus alas para volar"], "correcta": 1},
            {"pregunta": "¿Qué animal pasa por una transformación llamada metamorfosis?", "opciones": ["La mariposa", "El elefante", "El pingüino"], "correcta": 0},
            {"pregunta": "¿Qué fenómeno natural aparece después de la lluvia y tiene muchos colores?", "opciones": ["Un arcoíris", "Un tornado", "Un eclipse"], "correcta": 0}
        ]
        
        random.shuffle(self.preguntas)
        self.init_ui()
        
    def init_ui(self):
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(40, 30, 40, 30)
        
        fila_superior = QHBoxLayout()
        btn_volver = QPushButton("⬅ Volver al Menú")
        btn_volver.setFixedSize(180, 50)
        btn_volver.setStyleSheet("background-color: #607D8B; color: white; font-size: 16px; font-weight: bold; border-radius: 15px;")
        btn_volver.clicked.connect(self.reiniciar_y_volver)
        fila_superior.addWidget(btn_volver)
        fila_superior.addStretch()
        
        self.label_puntos = QLabel("⭐ Puntos: 0")
        self.label_puntos.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.label_puntos.setStyleSheet("color: #2C3E50; background: transparent;")
        fila_superior.addWidget(self.label_puntos)
        layout_principal.addLayout(fila_superior)
        
        self.label_pregunta = QLabel("")
        self.label_pregunta.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        self.label_pregunta.setStyleSheet("color: #2C3E50; margin-top: 30px; margin-bottom: 20px; background: transparent;")
        self.label_pregunta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_pregunta.setWordWrap(True)
        layout_principal.addWidget(self.label_pregunta)
        
        self.layout_opciones = QVBoxLayout()
        self.layout_opciones.setSpacing(15)
        self.botones_opciones = []
        
        for i in range(3):
            btn = QPushButton("")
            btn.setFixedHeight(70)
            btn.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            btn.clicked.connect(lambda checked, idx=i: self.verificar_respuesta(idx))
            self.layout_opciones.addWidget(btn)
            self.botones_opciones.append(btn)
            
        layout_principal.addLayout(self.layout_opciones)
        layout_principal.addStretch()
        
        self.setLayout(layout_principal)
        self.cargar_pregunta()
        
    def cargar_pregunta(self):
        for btn in self.botones_opciones:
            btn.setEnabled(True)
            btn.setVisible(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF; color: #2C3E50;
                    border: 3px solid #B0BEC5; border-radius: 20px; padding-left: 20px;
                }
                QPushButton:hover { background-color: #F5F7F8; }
            """)
            
        if self.pregunta_actual < len(self.preguntas):
            datos = self.preguntas[self.pregunta_actual]
            self.label_pregunta.setText(datos["pregunta"])
            for i, opcion in enumerate(datos["opciones"]):
                self.botones_opciones[i].setText(opcion)
        else:
            self.label_pregunta.setText(f"🎉 ¡Felicidades! Completaste la trivia.\nTu puntuación final es de {self.puntos} puntos.")
            for btn in self.botones_opciones:
                btn.setVisible(False)
                
    def verificar_respuesta(self, indice_seleccionado):
        for btn in self.botones_opciones:
            btn.setEnabled(False)
            
        datos = self.preguntas[self.pregunta_actual]
        indice_correcto = datos["correcta"]
        
        if indice_seleccionado == indice_correcto:
            self.botones_opciones[indice_seleccionado].setStyleSheet("background-color: #2ECC71; color: white; border-radius: 20px; border: none; font-size: 16px; font-weight: bold;")
            self.puntos += 10
            self.label_puntos.setText(f"⭐ Puntos: {self.puntos}")
        else:
            self.botones_opciones[indice_seleccionado].setStyleSheet("background-color: #E74C3C; color: white; border-radius: 20px; border: none; font-size: 16px; font-weight: bold;")
            self.botones_opciones[indice_correcto].setStyleSheet("background-color: #2ECC71; color: white; border-radius: 20px; border: none; font-size: 16px; font-weight: bold;")
            
        self.pregunta_actual += 1
        QTimer.singleShot(2000, self.cargar_pregunta)
        
    def reiniciar_y_volver(self):
        self.puntos = 0
        self.pregunta_actual = 0
        self.label_puntos.setText("⭐ Puntos: 0")
        random.shuffle(self.preguntas)
        self.cargar_pregunta()
        self.callback_volver()


# --- VENTANA PRINCIPAL DE KUKUDESKTOP ---
class KukuDesktop(QWidget):
    def __init__(self):
        super().__init__()

        self.ruta_pin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "control_parental.txt")
        self.asegurar_pin_existing()

        self.temas = {
            "Claro ⛅": {
                "ventana": "background-color: #E3F2FD;", 
                "texto": "color: #2C3E50;",
                "barra_superior": "background-color: #0072de; color: white; border-bottom-left-radius: 20px; border-bottom-right-radius: 20px;"
            },
            "Espacial 🌙": {
                "ventana": "background-color: #1A1A2E;", 
                "texto": "color: #E0E0E0;",
                "barra_superior": "background-color: #0F0F1A; color: #00FFF0; border-bottom-left-radius: 20px; border-bottom-right-radius: 20px;"
            },
            "Rosa 🩷": {
                "ventana": "background-color: #FCE4EC;", 
                "texto": "color: #4A148C;",
                "barra_superior": "background-color: #EC407A; color: white; border-bottom-left-radius: 20px; border-bottom-right-radius: 20px;"
            }
        }

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.showFullScreen() 
        self.setStyleSheet("background-color: #E3F2FD;") 
        
        self.layout_base = QVBoxLayout()
        self.layout_base.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout_base)

        self.bloquear_teclado()

        self.reproductor = QMediaPlayer()
        self.salida_audio = QAudioOutput()
        self.reproductor.setAudioOutput(self.salida_audio)
        self.salida_audio.setVolume(0.7)

        self.barra_superior = QFrame()
        self.barra_superior.setFixedHeight(60)
        
        barra_layout = QHBoxLayout()
        self.logo = QLabel(" 🐾 KuKuDesktop")
        self.logo.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        barra_layout.addWidget(self.logo)
        barra_layout.addStretch()

        self.selector_temas = QComboBox()
        self.selector_temas.addItems(list(self.temas.keys()))
        self.selector_temas.setFixedSize(170, 35)
        self.selector_temas.setStyleSheet("""
            QComboBox {
                background-color: white; color: #333333;
                border-radius: 10px; padding-left: 10px;
                font-weight: bold; font-size: 13px; border: none;
            }
        """)
        self.selector_temas.currentTextChanged.connect(self.cambiar_tema)
        barra_layout.addWidget(self.selector_temas)

        btn_config = QPushButton("⚙️")
        btn_config.setFont(QFont("Arial", 16))
        btn_config.setFixedSize(40, 40)
        btn_config.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2); 
                border-radius: 10px; color: white; border: none; margin-left: 10px;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.4); }
        """)
        btn_config.clicked.connect(self.abrir_configuracion)
        barra_layout.addWidget(btn_config)
        
        btn_cerrar = QPushButton("✖")
        btn_cerrar.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        btn_cerrar.setFixedSize(40, 40)
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C; color: white; border-radius: 10px; border: none; margin-left: 10px;
            }
            QPushButton:hover { background-color: #C0392B; }
        """)
        btn_cerrar.clicked.connect(self.intentar_cerrar)
        barra_layout.addWidget(btn_cerrar)

        self.barra_superior.setLayout(barra_layout)
        self.layout_base.addWidget(self.barra_superior)

        self.paginas = QStackedWidget()
        self.layout_base.addWidget(self.paginas)
        
        # --- DICCIONARIO DE CUENTOS (BIBLIOTECA EXPANDIDA) ---
        self.biblioteca_cuentos = {
            "El sol y el viento": "El sol y el viento discutían sobre quién era más fuerte. Vieron a un viajero con una capa y apostaron a que el que lograra quitarle la capa sería el más poderoso. El viento sopló con fuerza, pero el viajero se aferró a su capa. \n\nLuego, el sol brilló cálidamente, haciendo que el viajero se quitara la capa para refrescarse. Así, el sol demostró que la amabilidad es más fuerte que la fuerza.",
            "El patito curioso": "Había una vez un patito que siempre se preguntaba qué había más allá del lago donde vivía. Un día, decidió aventurarse y descubrió un bosque mágico lleno de animales amistosos, flores brillantes y un arcoíris que lo llevó a un mundo de fantasía. \n\nEl patito aprendió que la curiosidad puede llevarnos a lugares maravillosos y hacer nuevos amigos.",
            "Los pollitos": "Había una vez unos pequeños pollitos que vivían en un gallinero. Un día, uno de ellos decidió aventurarse y descubrió un mundo lleno de oportunidades. \n\nAprendió que la valentía y la amistad son las mejores herramientas para enfrentar los desafíos.",
            "La hormiga ingeniera": "Había una vez una pequeña hormiga llamada Mini que no solo quería cargar hojitas, ¡sino que le encantaba resolver problemas! Un día, un enorme charco de agua bloqueó el camino hacia el hormiguero. Las demás hormigas estaban preocupadas porque no sabían cómo cruzar.\n\nMini miró a su alrededor de forma lógica, tomó unas cuantas ramitas caídas y diseñó un puente firme y seguro. Gracias a sus cálculos y a su gran ingenio, todo el hormiguero pudo regresar a casa a salvo y celebrar una gran fiesta.",
            "El oso que quería aprender": "Barny era un oso grande y peludo con un gran sueño: quería tocar el piano y cantar hermosas melodías en el bosque. Al principio, sus enormes garras tocaban muchas teclas al mismo tiempo y los sonidos salían un poco graciosos.\n\nPero Barny no se rindió. Practicó un poquito cada tarde, moviendo sus dedos con suavidad sobre el teclado. Muy pronto, aprendió a tocar una dulce melodía de cuna que hacía que los pajaritos y las ardillas se reunieran felices a escucharlo bajo las estrellas.",
            "El misterio espacial": "El tierno perrito astronauta Koko viajaba en su pequeña nave espacial cuando vio algo parpadear a lo lejos. ¡Una estrella brillante cambiaba de colores! Pasaba de un azul mágico a un rosa pastel en un segundo.\n\nKoko se acercó con cuidado y descubrió que era un pequeño planeta de juguete que reaccionaba a las risas de los niños. Desde entonces, cada vez que un niño sonríe en la Tierra, el planeta espacial brilla con sus colores favoritos para iluminar el cielo nocturno.",
            "El gato Pixel": "Pixel era un gatito blanco y negro muy travieso que vivía dentro de una computadora. A diferencia de otros gatos que cazaban ratones de verdad, a Pixel le encantaba perseguir el cursor del mouse por la pantalla.\n\nUn día, descubrió que si saltaba muy fuerte sobre los iconos, estos cambiaban de color. Jugando y explorando, descubrió un botón secreto que llenaba todo el escritorio de estrellas brillantes. Desde entonces, cada tarde ayuda a los niños a encontrar los juegos más divertidos del sistema.",
            "La melodía del río": "En un valle muy verde, un pequeño río corría cantando entre las piedras. El río quería tocar una canción de piano para sus amigos los animales, pero el agua se movía tan rápido que las notas se mezclaban y sonaban un poco alborotadas.\n\nUna tortuga vieja y sabia le sugirió ir más despacio. El río escuchó el consejo, disminuyó su velocidad y comenzó a golpear las rocas de forma suave y pausada. El bosque entero se llenó de una dulce melodía que ayudó a todos los animalitos a conciliar el sueño bajo la luz de la luna."
        }  
        
        ruta_base = os.path.dirname(os.path.abspath(__file__))
        ruta_folder_musica = os.path.join(ruta_base, "Musica_KuKuDesktop")

        self.biblioteca_musica = {
            "¡A Jugar!": os.path.join(ruta_folder_musica, "¡A_Jugar_Sin_Fin_.mp3"),
            "Divertida": os.path.join(ruta_folder_musica, "Cancion_Divertida.mp3"),
            "Instrumental": os.path.join(ruta_folder_musica, "the_mountain_kid.mp3"),
            "Relajante": os.path.join(ruta_folder_musica, "Melodia_linda.mp3"),
            "Animales": os.path.join(ruta_folder_musica, "musica_animales.mp3"),
            "Infantil": os.path.join(ruta_folder_musica, "infantil.mp3")
        }

        # Inicialización de vistas fijas
        self.crear_pantalla_principal()
        self.crear_pantalla_juego_memoria()
        self.crear_pantalla_cuentos()
        self.crear_pantalla_lector_cuento()
        self.crear_pantalla_musica()
        self.crear_pantalla_calculadora()
        self.crear_pantalla_tres_en_raya()
        self.crear_pantalla_piano()
        self.crear_pantalla_granja()
        self.crear_pantalla_trivia()

        self.paginas.setCurrentIndex(0)
        self.cambiar_tema("Claro ⛅")

    def cambiar_tema(self, nombre_tema):
        if nombre_tema in self.temas:
            style_dict = self.temas[nombre_tema]
            self.setStyleSheet(style_dict["ventana"])
            self.barra_superior.setStyleSheet(style_dict["barra_superior"])
            if hasattr(self, 'label_titulo_menu'):
                self.label_titulo_menu.setStyleSheet(style_dict["texto"] + " font-size: 28px; font-weight: bold;")

    def asegurar_pin_existing(self):
        if not os.path.exists(self.ruta_pin):
            try:
                with open(self.ruta_pin, "w", encoding="utf-8") as f:
                    f.write("1234")
            except Exception as e:
                print(f"Error PIN: {e}")

    def bloquear_teclado(self):
        try:
            keyboard.block_key('win')
            keyboard.add_hotkey('alt+tab', lambda: None, suppress=True)
            keyboard.add_hotkey('alt+f4', lambda: None, suppress=True)
        except Exception as e:
            print(f"🔒 Teclado sin modo Administrador: {e}")

    def crear_pantalla_principal(self):
        self.pantalla_inicio = QWidget()
        grilla = QGridLayout()
        self.pantalla_inicio.setLayout(grilla)
        
        apps = [
            ("🎮 Memory", "#FF5E00", "PANTALLA_MEMORY"),
            ("❌ Tres en Raya", "#006E58", "PANTALLA_TRES_EN_RAYA"), 
            ("🎹 Piano", "#FF0000", "PANTALLA_PIANO"), 
            ("🐾 Granja", "#1CFF7B", "PANTALLA_GRANJA"),
            ("🎨 Dibujo", "#BC84EE", "mspaint"), 
            ("📚 Cuentos", "#FFD700", "PANTALLA_CUENTOS"), 
            ("🎵 Música", "#FF69B4", "PANTALLA_MUSICA"),
            ("🧮 Calculadora", "#00BFFF", "PANTALLA_CALCULADORA"),
            ("❓ Trivia", "#FFB774", "PANTALLA_TRIVIA")
        ]

        row, col = 0, 0
        for nombre, color, accion in apps:
            btn = QPushButton(nombre)
            btn.setFixedSize(200, 200)
            btn.setStyleSheet(f"background-color: {color}; color: white; font-size: 22px; font-weight: bold; border-radius: 30px; border: 5px solid white;")
            
            if accion == "PANTALLA_MEMORY":
                btn.clicked.connect(self.ir_a_juego_memoria)
            elif accion == "PANTALLA_TRES_EN_RAYA":
                btn.clicked.connect(self.ir_a_tres_en_raya)
            elif accion == "PANTALLA_PIANO":
                btn.clicked.connect(self.ir_a_piano)
            elif accion == "PANTALLA_CUENTOS":
                btn.clicked.connect(self.ir_a_cuentos)
            elif accion == "PANTALLA_MUSICA":
                btn.clicked.connect(self.ir_a_musica)
            elif accion == "PANTALLA_CALCULADORA":
                btn.clicked.connect(self.ir_a_calculadora)
            elif accion == "PANTALLA_GRANJA":
                btn.clicked.connect(self.ir_a_granja)
            elif accion == "PANTALLA_TRIVIA":
                btn.clicked.connect(self.ir_a_trivia)
            elif accion:
                btn.clicked.connect(lambda checked, a=accion: self.abrir_programa_externo(a))
                
            grilla.addWidget(btn, row, col, alignment=Qt.AlignmentFlag.AlignCenter)
            col += 1
            if col > 2:
                col = 0
                row += 1

        self.paginas.addWidget(self.pantalla_inicio)

    def crear_pantalla_juego_memoria(self):
        self.juego_memoria = MemoriaGame(callback_volver=self.ir_a_inicio)
        self.paginas.addWidget(self.juego_memoria)

    def crear_pantalla_tres_en_raya(self):
        self.juego_tres_en_raya = TresEnRayaGame(callback_volver=self.ir_a_inicio)
        self.paginas.addWidget(self.juego_tres_en_raya)

    def crear_pantalla_piano(self):
        self.piano_musical = PianoMusical(callback_volver=self.ir_a_inicio)
        self.paginas.addWidget(self.piano_musical)

    def crear_pantalla_cuentos(self):
        self.pantalla_cuentos = QWidget()
        layout = QVBoxLayout()
        
        btn_volver = QPushButton("⬅ Volver al Menú")
        btn_volver.setFixedSize(180, 50)
        btn_volver.setStyleSheet("background-color: #607D8B; color: white; font-size: 16px; font-weight: bold; border-radius: 15px;")
        btn_volver.clicked.connect(self.ir_a_inicio)
        layout.addWidget(btn_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        txt_titulo = QLabel("📖 Elige un cuento para leer:")
        txt_titulo.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        txt_titulo.setStyleSheet("color: #2C3E50; margin-top: 10px; margin-bottom: 25px;")
        txt_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(txt_titulo)

        grilla_cuentos = QGridLayout()
        layout.addLayout(grilla_cuentos)
        
        row, col = 0, 0
        for titulo in self.biblioteca_cuentos.keys():
            btn_cuento = QPushButton(titulo)
            btn_cuento.setFixedSize(300, 100)
            btn_cuento.setStyleSheet("background-color: #FFD700; color: #2C3E50; font-size: 18px; font-weight: bold; border-radius: 20px; border: 4px solid white;")
            btn_cuento.clicked.connect(lambda checked, t=titulo: self.mostrar_cuento(t))
            grilla_cuentos.addWidget(btn_cuento, row, col, alignment=Qt.AlignmentFlag.AlignCenter)
            col += 1
            if col > 1: 
                col = 0
                row += 1
                
        layout.addStretch()
        self.pantalla_cuentos.setLayout(layout)
        self.paginas.addWidget(self.pantalla_cuentos)

    def crear_pantalla_lector_cuento(self):
        self.pantalla_lector = QWidget()
        layout = QVBoxLayout()
        
        btn_volver = QPushButton("⬅ Volver a Cuentos")
        btn_volver.setFixedSize(180, 50)
        btn_volver.setStyleSheet("background-color: #607D8B; color: white; font-size: 16px; font-weight: bold; border-radius: 15px;")
        btn_volver.clicked.connect(self.ir_a_cuentos)
        layout.addWidget(btn_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        self.label_titulo_cuento = QLabel("")
        self.label_titulo_cuento.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.label_titulo_cuento.setStyleSheet("color: #0072de; margin-bottom: 15px;")
        self.label_titulo_cuento.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_titulo_cuento)

        self.caja_texto_cuento = QTextBrowser()
        self.caja_texto_cuento.setFont(QFont("Arial", 20))
        self.caja_texto_cuento.setStyleSheet("QTextBrowser { background-color: white; color: #2C3E50; border-radius: 25px; padding: 35px; border: 4px solid #E0E0E0; }")
        layout.addWidget(self.caja_texto_cuento)
        
        self.pantalla_lector.setLayout(layout)
        self.paginas.addWidget(self.pantalla_lector)

    def crear_pantalla_musica(self):
        self.pantalla_musica = QWidget()
        layout = QVBoxLayout()
        
        btn_volver = QPushButton("⬅ Volver al Menú")
        btn_volver.setFixedSize(180, 50)
        btn_volver.setStyleSheet("background-color: #607D8B; color: white; font-size: 16px; font-weight: bold; border-radius: 15px;")
        btn_volver.clicked.connect(self.ir_a_inicio)
        layout.addWidget(btn_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        self.txt_estado_musica = QLabel("🎵 Elige una canción para reproducir:")
        self.txt_estado_musica.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.txt_estado_musica.setStyleSheet("color: #2C3E50; margin-top: 10px; margin-bottom: 20px;")
        self.txt_estado_musica.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.txt_estado_musica)

        layout_controles = QHBoxLayout()
        
        self.btn_pausa = QPushButton("⏸ Pausar")
        self.btn_pausa.setFixedSize(150, 50)
        self.btn_pausa.setStyleSheet("background-color: #E91E63; color: white; font-size: 16px; font-weight: bold; border-radius: 12px;")
        self.btn_pausa.clicked.connect(self.alternar_pausa)
        
        self.btn_stop = QPushButton("⏹ Detener")
        self.btn_stop.setFixedSize(150, 50)
        self.btn_stop.setStyleSheet("background-color: #9C27B0; color: white; font-size: 16px; font-weight: bold; border-radius: 12px;")
        self.btn_stop.clicked.connect(self.detener_musica)
        
        layout_controles.addWidget(self.btn_pausa)
        layout_controles.addWidget(self.btn_stop)
        layout_controles.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(layout_controles)

        grilla_musica = QGridLayout()
        layout.addLayout(grilla_musica)
        
        row, col = 0, 0
        for nombre_cancion, ruta_archivo in self.biblioteca_musica.items():
            btn_cancion = QPushButton(f"🎶\n{nombre_cancion}")
            btn_cancion.setFixedSize(280, 110)
            btn_cancion.setStyleSheet("QPushButton { background-color: #FF69B4; color: white; font-size: 16px; font-weight: bold; border-radius: 20px; border: 4px solid white; } QPushButton:hover { background-color: #FF1493; }")
            btn_cancion.clicked.connect(lambda checked, r=ruta_archivo, n=nombre_cancion: self.reproducir_cancion(r, n))
            
            grilla_musica.addWidget(btn_cancion, row, col, alignment=Qt.AlignmentFlag.AlignCenter)
            col += 1
            if col > 1: 
                col = 0
                row += 1

        layout.addStretch()
        self.pantalla_musica.setLayout(layout)
        self.paginas.addWidget(self.pantalla_musica)

    def crear_pantalla_calculadora(self):
        self.pantalla_calc = QWidget()
        layout = QVBoxLayout()
        
        btn_volver = QPushButton("⬅ Volver al Menú")
        btn_volver.setFixedSize(180, 50)
        btn_volver.setStyleSheet("background-color: #607D8B; color: white; font-size: 16px; font-weight: bold; border-radius: 15px;")
        btn_volver.clicked.connect(self.ir_a_inicio)
        layout.addWidget(btn_volver, alignment=Qt.AlignmentFlag.AlignLeft)

        self.pantalla_digital = QLabel("0")
        self.pantalla_digital.setFixedHeight(80)
        self.pantalla_digital.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        self.pantalla_digital.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.pantalla_digital.setStyleSheet("QLabel { background-color: #2C3E50; color: #00FF66; padding-right: 20px; border-radius: 15px; border: 4px solid #1A252F; }")
        layout.addWidget(self.pantalla_digital)

        grilla_botones = QGridLayout()
        layout.addLayout(grilla_botones)

        botones = {
            '7': (0, 0), '8': (0, 1), '9': (0, 2), '÷': (0, 3),
            '4': (1, 0), '5': (1, 1), '6': (1, 2), '×': (1, 3),
            '1': (2, 0), '2': (2, 1), '3': (2, 2), '−': (2, 3),
            'C': (3, 0), '0': (3, 1), '=': (3, 2), '+': (3, 3)
        }

        for texto, pos in botones.items():
            btn = QPushButton(texto)
            btn.setFixedSize(100, 100)
            
            if texto == 'C':
                color_bg = "#F44336"
            elif texto == '=':
                color_bg = "#4CAF50"
            elif texto in ['+', '−', '×', '÷']:
                color_bg = "#FF9800"
            else:
                color_bg = "#FFFFFF"
                
            color_texto = "#2C3E50" if color_bg == "#FFFFFF" else "#FFFFFF"
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_bg}; color: {color_texto};
                    font-size: 26px; font-weight: bold;
                    border-radius: 20px; border: 2px solid #BDC3C7;
                }}
                QPushButton:pressed {{ background-color: #BDC3C7; }}
            """)
            
            btn.clicked.connect(lambda checked, t=texto: self.presionar_boton_calc(t))
            grilla_botones.addWidget(btn, pos[0], pos[1], alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()
        self.pantalla_calc.setLayout(layout)
        self.paginas.addWidget(self.pantalla_calc)

    def crear_pantalla_granja(self):
        self.granja_sonidos = GranjaSonidos(callback_volver=self.ir_a_inicio)
        self.paginas.addWidget(self.granja_sonidos)

    def crear_pantalla_trivia(self):
        self.juego_trivia = JuegoTrivia(callback_volver=self.ir_a_inicio)
        self.paginas.addWidget(self.juego_trivia)

    def reproducir_cancion(self, ruta, nombre):
        if os.path.exists(ruta):
            self.reproductor.setSource(QUrl.fromLocalFile(ruta))
            self.reproductor.play()
            self.txt_estado_musica.setText(f"🔊 Sonando: {nombre}")
            self.txt_estado_musica.setStyleSheet("color: #E91E63; margin-top: 10px; margin-bottom: 20px;")
            self.btn_pausa.setText("⏸ Pausar")
        else:
            self.txt_estado_musica.setText(f"❌ Archivo no encontrado")
            self.txt_estado_musica.setStyleSheet("color: #D32F2F; margin-top: 10px; margin-bottom: 20px;")

    def alternar_pausa(self):
        if self.reproductor.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.reproductor.pause()
            self.btn_pausa.setText("▶ Reanudar")
        elif self.reproductor.playbackState() == QMediaPlayer.PlaybackState.PausedState:
            self.reproductor.play()
            self.btn_pausa.setText("⏸ Pausar")

    def detener_musica(self):
        self.reproductor.stop()
        self.txt_estado_musica.setText("🎵 Elige una canción para reproducir:")
        self.txt_estado_musica.setStyleSheet("color: #2C3E50; margin-top: 10px; margin-bottom: 20px;")
        self.btn_pausa.setText("⏸ Pausar")

    def presionar_boton_calc(self, caracter):
        actual = self.pantalla_digital.text()
        
        if caracter == 'C':
            self.pantalla_digital.setText("0")
            return
            
        if caracter == '=':
            # Validación simple para que no evalúe operadores vacíos al final
            if actual[-1] in ['+', '−', '×', '÷'] or actual == "Error":
                self.pantalla_digital.setText("Error")
                return
            try:
                expr = actual.replace('×', '*').replace('÷', '/').replace('−', '-')
                resultado = str(eval(expr))
                self.pantalla_digital.setText(resultado)
            except:
                self.pantalla_digital.setText("Error")
            return

        if actual == "0" or actual == "Error":
            if caracter in ['+', '−', '×', '÷']:
                self.pantalla_digital.setText("0" + caracter)
            else:
                self.pantalla_digital.setText(caracter)
        else:
            self.pantalla_digital.setText(actual + caracter)

    def abrir_programa_externo(self, ruta):
        try:
            subprocess.Popen(ruta)
        except Exception as e:
            print(f"No se pudo abrir el ejecutable: {e}")

    def mostrar_cuento(self, titulo):
        texto = self.biblioteca_cuentos.get(titulo, "Ups, no encontré ese cuento.")
        self.label_titulo_cuento.setText(titulo)
        self.caja_texto_cuento.setText(texto)
        self.paginas.setCurrentWidget(self.pantalla_lector)

    def ir_a_inicio(self): 
        self.paginas.setCurrentWidget(self.pantalla_inicio)
    def ir_a_juego_memoria(self): 
        self.juego_memoria.iniciar_juego()
        self.paginas.setCurrentWidget(self.juego_memoria)
    def ir_a_cuentos(self): 
        self.paginas.setCurrentWidget(self.pantalla_cuentos)
    def ir_a_musica(self): 
        self.paginas.setCurrentWidget(self.pantalla_musica)
    def ir_a_calculadora(self): 
        self.paginas.setCurrentWidget(self.pantalla_calc)
    def ir_a_tres_en_raya(self):
        self.juego_tres_en_raya.iniciar_juego()
        self.paginas.setCurrentWidget(self.juego_tres_en_raya)
    def ir_a_piano(self):
        self.paginas.setCurrentWidget(self.piano_musical)
        self.piano_musical.setFocus()
    def ir_a_granja(self):
        self.paginas.setCurrentWidget(self.granja_sonidos)
    def ir_a_trivia(self):
        self.juego_trivia.reiniciar_y_volver() 
        self.paginas.setCurrentWidget(self.juego_trivia) 

    def abrir_configuracion(self):
        dialogo = PanelConfiguracion(ruta_pin=self.ruta_pin, parent=self)
        dialogo.setModal(True)
        dialogo.exec()

    def intentar_cerrar(self):
        self.close()

    def closeEvent(self, event: QCloseEvent):
        dialogo = DialogoSalir(ruta_pin=self.ruta_pin, parent=self)
        dialogo.setModal(True)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KukuDesktop()
    window.show()
    sys.exit(app.exec())