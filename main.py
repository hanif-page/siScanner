import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QComboBox, QLabel, 
                             QGraphicsEllipseItem, QSplitter, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPen, QColor
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from app.database import SiScannerDatabase

class SiScannerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("siScanner | Volumetric 3D Terminal")
        self.resize(1500, 900)
        self.db = SiScannerDatabase()
        self.init_ui()
        self.load_sessions()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Sidebar ---
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(320)
        sidebar = QVBoxLayout(sidebar_container := sidebar_widget) # Using walrus for clarity
        
        self.label = QLabel("📡 siScanner 3D")
        self.label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e3a8a; margin-bottom: 5px;")
        sidebar.addWidget(self.label)

        # --- NEW: WARNING BANNER ---
        self.warning_note = QLabel("⚠️ SYSTEM NOTE: Color-depth calculation is currently disabled. Rendering in flat-blue mode.")
        self.warning_note.setWordWrap(True)
        self.warning_note.setStyleSheet("""
            background-color: #fee2e2; 
            color: #991b1b; 
            padding: 10px; 
            border-radius: 6px; 
            border: 1px solid #fecaca;
            font-size: 11px;
            font-weight: 500;
            margin-bottom: 10px;
        """)
        sidebar.addWidget(self.warning_note)
        
        sidebar.addWidget(QLabel("📂 Scan History:"))
        self.session_box = QComboBox()
        self.session_box.setStyleSheet("padding: 5px; border: 1px solid #d1d5db; border-radius: 4px;")
        sidebar.addWidget(self.session_box)

        self.btn_load = QPushButton("🚀 GENERATE PROJECTION")
        self.btn_load.setMinimumHeight(55)
        self.btn_load.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; border-radius: 8px;")
        self.btn_load.clicked.connect(self.plot_data)
        sidebar.addWidget(self.btn_load)

        # --- Telemetry Dashboard ---
        sidebar.addSpacing(20)
        self.telemetry_panel = QFrame()
        self.telemetry_panel.setStyleSheet("background-color: #f3f4f6; border-radius: 10px; border: 1px solid #e5e7eb;")
        tel_layout = QVBoxLayout(self.telemetry_panel)
        
        self.radius_label = QLabel("Max Radius: --- mm")
        self.height_label = QLabel("Avg Height: --- mm")
        self.point_label = QLabel("Data Nodes: ---")
        
        for lbl in [self.radius_label, self.height_label, self.point_label]:
            lbl.setStyleSheet("font-size: 15px; color: #111827; font-family: 'Courier New'; padding: 2px;")
            tel_layout.addWidget(lbl)
        sidebar.addWidget(self.telemetry_panel)
        sidebar.addStretch()
        
        layout.addWidget(sidebar_widget, 1)

        # --- Viewports ---
        self.radar_widget = pg.PlotWidget()
        self.radar_widget.setBackground('#f9fafb')
        self.radar_widget.setAspectLocked(True)
        self.init_radar_grid()
        self.scatter_2d = pg.ScatterPlotItem(size=6, pen=None)
        self.radar_widget.addItem(self.scatter_2d)

        self.view_3d = gl.GLViewWidget()
        self.view_3d.setBackgroundColor('#05070a')
        self.view_3d.setCameraPosition(distance=4000, elevation=30, azimuth=45)
        grid = gl.GLGridItem()
        grid.setSize(8000, 8000, 1)
        grid.setSpacing(500, 500, 1)
        self.view_3d.addItem(grid)

        self.splitter.addWidget(self.radar_widget)
        self.splitter.addWidget(self.view_3d)
        layout.addWidget(self.splitter, 5)

    def init_radar_grid(self):
        grid_pen = QPen(QColor('#d1d5db'), 1, Qt.PenStyle.DashLine)
        for r in range(500, 4001, 500):
            circle = QGraphicsEllipseItem(-r, -r, r*2, r*2)
            circle.setPen(grid_pen)
            self.radar_widget.addItem(circle)

    def load_sessions(self):
        sessions = self.db.get_all_sessions()
        self.session_data = {f"{s['timestamp'].strftime('%H:%M:%S')} | {s.get('scan_mode', 'N/A')}": s['_id'] for s in sessions}
        self.session_box.addItems(self.session_data.keys())

    def plot_data(self):
        selected = self.session_box.currentText()
        if not selected: return
        scan = self.db.get_session_by_id(self.session_data[selected])
        if not (scan and 'data' in scan): return

        for item in self.view_3d.items[:]:
            if isinstance(item, (gl.GLMeshItem, gl.GLScatterPlotItem)):
                self.view_3d.removeItem(item)

        points = scan['data']
        dists = np.array([p['dist'] for p in points])
        
        self.radius_label.setText(f"Max Radius: {int(np.max(dists))} mm")
        self.height_label.setText(f"Avg Height: {int(2 * np.mean(dists) * np.tan(np.radians(13.5)))} mm")
        self.point_label.setText(f"Data Nodes: {len(points)}")

        # --- FLAT BLUE RENDER ---
        spots_2d = [{'pos': (p['x'], p['y']), 'brush': pg.mkBrush(30, 144, 255, 200)} for p in points]
        self.scatter_2d.setData(spots_2d)

        angle_list = sorted(list(set(p['angle'] for p in points)))
        num_v, num_h = 13, len(angle_list)
        grid = np.zeros((num_h, num_v, 3))
        for p in points:
            try:
                grid[angle_list.index(p['angle'])][p['roi_index']] = [p['x'], p['y'], p['z']]
            except: continue

        verts = grid.reshape(-1, 3)
        faces, face_colors = [], []
        for i in range(num_h - 1):
            for j in range(num_v - 1):
                p1, p2, p3, p4 = i*num_v+j, (i+1)*num_v+j, (i+1)*num_v+(j+1), i*num_v+(j+1)
                faces.extend([[p1, p2, p3], [p1, p3, p4]])
                face_colors.extend([[0.1, 0.5, 0.9, 0.6]] * 2) # Solid semi-transparent blue

        mesh_data = gl.MeshData(vertexes=verts, faces=np.array(faces), faceColors=np.array(face_colors))
        mesh_item = gl.GLMeshItem(meshdata=mesh_data, smooth=True, drawEdges=True, edgeColor=(1,1,1,0.2))
        self.view_3d.addItem(mesh_item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SiScannerApp()
    window.show()
    sys.exit(app.exec())