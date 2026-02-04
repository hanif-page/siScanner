import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QComboBox, QLabel)
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from app.database import SiScannerDatabase

class SiScannerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("siScanner | Industrial Desktop Terminal")
        self.resize(1100, 800)
        
        # Initialize Database
        self.db = SiScannerDatabase()
        
        # Setup UI
        self.init_ui()
        self.load_sessions()

    def init_ui(self):
        # Main Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # --- Sidebar (Controls) ---
        sidebar = QVBoxLayout()
        sidebar.setContentsMargins(10, 10, 10, 10)
        
        self.label = QLabel("siScanner")
        self.label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333333;")
        sidebar.addWidget(self.label)

        sidebar.addWidget(QLabel("Select Scan Session:"))
        self.session_box = QComboBox()
        sidebar.addWidget(self.session_box)

        self.btn_load = QPushButton("Render Spatial Map")
        self.btn_load.setMinimumHeight(40)
        self.btn_load.setStyleSheet("background-color: #1f2937; color: white; font-weight: bold;")
        self.btn_load.clicked.connect(self.plot_data)
        sidebar.addWidget(self.btn_load)

        sidebar.addStretch() # Push items to the top
        
        # Metrics Display
        self.metrics_label = QLabel("Status: Standby")
        sidebar.addWidget(self.metrics_label)
        
        layout.addLayout(sidebar, 1) # Sidebar takes 25% width

        # --- Main View (The Radar) ---
        self.plot_widget = pg.PlotWidget()
        
        # 1. Background: Light Gray/White
        self.plot_widget.setBackground('#f3f4f6') # A clean, professional light gray
        self.plot_widget.setAspectLocked(True)
        
        # 2. Circular Grid Lines (Radar Rings)
        from PyQt6.QtWidgets import QGraphicsEllipseItem
        from PyQt6.QtGui import QPen, QColor

        # Darker gray for the grid lines to ensure visibility on light background
        grid_pen = QPen(QColor('#d1d5db'), 1, Qt.PenStyle.DashLine) 

        for r in range(500, 3001, 500):
            circle = QGraphicsEllipseItem(-r, -r, r*2, r*2)
            circle.setPen(grid_pen)
            self.plot_widget.addItem(circle)

        # 3. Distance Labels
        for r in range(500, 3001, 1000):
            text = pg.TextItem(text=f"{r}mm", color='#374151', anchor=(0, 1))
            text.setPos(0, r)
            self.plot_widget.addItem(text)

        # 4. The Scatter Item (Data Points)
        # We add a thin border (pen) to the dots so they don't blend into the light background
        self.scatter = pg.ScatterPlotItem(
            size=12, 
            pen=pg.mkPen('white', width=0.5), # High-contrast outline
            hoverable=True
        )
        self.plot_widget.addItem(self.scatter)
        
        # Center marker (Scanner position)
        self.plot_widget.addItem(pg.ScatterPlotItem(pos=[[0,0]], size=15, brush=pg.mkBrush('#ef4444')))

        layout.addWidget(self.plot_widget, 4) # Radar takes 75% width

    def load_sessions(self):
        """Pulls session list from MongoDB into the dropdown."""
        sessions = self.db.get_all_sessions()
        self.session_data = {str(s['timestamp']): s['_id'] for s in sessions}
        self.session_box.addItems(list(self.session_data.keys()))

    def plot_data(self):
        """Renders points with a Red-to-Blue distance gradient."""
        selected_time = self.session_box.currentText()
        if not selected_time: return
        
        session_id = self.session_data.get(selected_time)
        scan = self.db.get_session_by_id(session_id)
        
        if scan and 'data' in scan:
            points = scan['data']
            spots = []

            # Define our range for the gradient (adjust based on your room size)
            NEAR_LIMIT = 500   # mm
            FAR_LIMIT = 2500   # mm

            for p in points:
                try:
                    x, y = float(p.get('x', 0)), float(p.get('y', 0))
                    d = float(p.get('dist', 0))
                    if x == 0 and y == 0: continue

                    # --- COLOR INTERPOLATION LOGIC ---
                    # Clamp distance to our limits
                    d_clamped = max(NEAR_LIMIT, min(d, FAR_LIMIT))
                    
                    # Calculate ratio (0.0 = Near, 1.0 = Far)
                    ratio = (d_clamped - NEAR_LIMIT) / (FAR_LIMIT - NEAR_LIMIT)
                    
                    # Interpolate: Red decreases as Blue increases
                    r = int(255 * (1 - ratio))
                    b = int(255 * ratio)
                    g = 0 # Keep it clean on the Red-Blue spectrum

                    spots.append({
                        'pos': (x, y),
                        'size': 10,
                        'brush': pg.mkBrush(r, g, b, 200), # 200 is alpha/transparency
                        'pen': pg.mkPen(None)
                    })
                except Exception as e:
                    print(f"Error processing point: {e}")

            if spots:
                self.scatter.setData(spots)
                # Keep view focused on the 180° front-arc
                self.plot_widget.setRange(xRange=[-3000, 3000], yRange=[0, 3000])
                self.metrics_label.setText(f"Status: {len(spots)} points (R: Near -> B: Far)")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SiScannerApp()
    window.show()
    sys.exit(app.exec())