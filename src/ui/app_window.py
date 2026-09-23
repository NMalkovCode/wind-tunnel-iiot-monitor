import customtkinter as ctk

SENSORS = ["Fan 1", "Fan 2", "Fan 3", "Fan 4", "Fan 5", "Extra 1", "Extra 2"]

class FanMonitorApp(ctk.CTk):
    def __init__(self, config):
        super().__init__()
        self.title("Wind Tunnel Pressure Monitor")
        self.geometry(f"{config['UI_SETTINGS']['APP_WIDTH']}x{config['UI_SETTINGS']['APP_HEIGHT']}")
        self.resizable(False, False)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.pressure_labels = {}
        self.temp_labels = {}
        self.setup_ui()

    def setup_ui(self):
        title = ctk.CTkLabel(self, text="IIoT Moving Ground Plane Monitor", font=("Arial", 24, "bold"), text_color="#0B4F6C")
        title.place(x=25, y=25)

        x_offset = 25
        for sensor_name in SENSORS:
            frame = ctk.CTkFrame(self, width=120, height=180, fg_color="white", border_width=2, border_color="#0B4F6C")
            frame.place(x=x_offset, y=100)
            
            ctk.CTkLabel(frame, text=sensor_name, font=("Arial", 16, "bold"), text_color="#0B4F6C").place(x=10, y=10)
            
            p_lbl = ctk.CTkLabel(frame, text="0 Pa", font=("Arial", 22, "bold"), text_color="#0B4F6C")
            p_lbl.place(x=10, y=50)
            self.pressure_labels[sensor_name] = p_lbl

            t_lbl = ctk.CTkLabel(frame, text="0 °C", font=("Arial", 16), text_color="gray")
            t_lbl.place(x=10, y=100)
            self.temp_labels[sensor_name] = t_lbl
            
            x_offset += 135

    def update_sensor_display(self, sensor_name, current_sma, temperature, is_anomaly):
        if sensor_name in self.pressure_labels:
            color = "red" if is_anomaly else "#0B4F6C"
            self.pressure_labels[sensor_name].configure(text=f"{current_sma:.1f} Pa", text_color=color)
            self.temp_labels[sensor_name].configure(text=f"{temperature:.1f} °C")