import arcade
import arcade.gui
import random
from datetime import datetime, timedelta

# Hardcoded Blue Line stations with approx lat/long
blue_line_stations = [
    {"name": "Wimco Nagar Depot", "lat": 13.236, "lon": 80.305},
    {"name": "Wimco Nagar", "lat": 13.211, "lon": 80.306},
    {"name": "Tiruvottriyur", "lat": 13.159, "lon": 80.303},
    {"name": "Tiruvottriyur Theradi", "lat": 13.147, "lon": 80.302},
    {"name": "Kaladipet", "lat": 13.137, "lon": 80.298},
    {"name": "Tollgate", "lat": 13.125, "lon": 80.294},
    {"name": "New Washermanpet", "lat": 13.115, "lon": 80.289},
    {"name": "Tondiarpet", "lat": 13.126, "lon": 80.290},
    {"name": "Sir Theagaraya College", "lat": 13.113, "lon": 80.283},
    {"name": "Washermanpet", "lat": 13.115, "lon": 80.289},
    {"name": "Mannadi", "lat": 13.097, "lon": 80.282},
    {"name": "High Court", "lat": 13.086, "lon": 80.285},
    {"name": "Puratchi Thalaivar Dr. M.G. Ramachandran Central", "lat": 13.083, "lon": 80.275},
    {"name": "Government Estate", "lat": 13.070, "lon": 80.274},
    {"name": "LIC", "lat": 13.065, "lon": 80.274},
    {"name": "Thousand Lights", "lat": 13.061, "lon": 80.257},
    {"name": "AG-DMS", "lat": 13.046, "lon": 80.245},
    {"name": "Teynampet", "lat": 13.038, "lon": 80.248},
    {"name": "Nandanam", "lat": 13.031, "lon": 80.239},
    {"name": "Saidapet", "lat": 13.023, "lon": 80.226},
    {"name": "Little Mount", "lat": 13.010, "lon": 80.223},
    {"name": "Guindy", "lat": 13.008, "lon": 80.208},
    {"name": "Arignar Anna Alandur", "lat": 13.000, "lon": 80.207},
    {"name": "Nanganallur Road", "lat": 12.988, "lon": 80.193},
    {"name": "Meenambakkam", "lat": 12.984, "lon": 80.176},
    {"name": "Chennai International Airport", "lat": 12.994, "lon": 80.171},
]

def scale_coords(coords, width=700, height=500, margin=50):
    min_lat = min(s['lat'] for s in coords)
    max_lat = max(s['lat'] for s in coords)
    min_lon = min(s['lon'] for s in coords)
    max_lon = max(s['lon'] for s in coords)
    scaled = []
    for s in coords:
        x = margin + (s['lon'] - min_lon) / (max_lon - min_lon) * (width - 2*margin)
        y = margin + (height - 2*margin) - ((s['lat'] - min_lat) / (max_lat - min_lat) * (height - 2*margin))
        scaled.append((x, y))
    return scaled

blue_line_path = scale_coords(blue_line_stations)

monthly_ridership = {
    "Apr-2023": 4377813,
    "May-2023": 4500000,
}

def generate_trains(day_type="weekday", start_time=datetime(2026, 2, 2, 5, 0), end_time=datetime(2026, 2, 2, 23, 0)):
    trains = []
    current_time = start_time
    while current_time < end_time:
        hour = current_time.hour
        if day_type == "weekday":
            if 8 <= hour < 11 or 17 <= hour < 20:
                interval = 6
            elif 22 <= hour < 23:
                interval = 15
            else:
                interval = 7
        elif day_type == "saturday":
            interval = 10 if 12 <= hour < 20 else 14
        else:  # sunday
            interval = 10 if 12 <= hour < 20 else 15
        trains.append({"start_time": current_time, "position": 0, "speed": 1.5})
        current_time += timedelta(minutes=interval)
    return trains

class MetroSimulation(arcade.Window):
    def __init__(self):
        super().__init__(1100, 600, "Chennai Metro Replay")
        arcade.set_background_color(arcade.color.BLACK)
        
        self.trains = generate_trains()
        self.sim_time = datetime(2026, 2, 2, 5, 0)
        self.passengers = 0
        self.time_speed = 60
        self.paused = False
        self.day_type = "weekday"
        self.month = "Apr-2023"
        self.end_time = datetime(2026, 2, 2, 23, 0)
        
        # UI Manager
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()
        
        # Create UI panel
        self.setup_ui()

    def setup_ui(self):
        # Create a vertical box for controls
        v_box = arcade.gui.UIBoxLayout(space_between=10)
        
        # Title
        title = arcade.gui.UILabel(text="Controls", font_size=16, bold=True)
        v_box.add(title)
        
        # Play/Pause button
        self.play_button = arcade.gui.UIFlatButton(text="Pause", width=200)
        self.play_button.on_click = self.toggle_pause
        v_box.add(self.play_button)
        
        # Speed label
        speed_label = arcade.gui.UILabel(text=f"Speed: {self.time_speed}x", font_size=12)
        v_box.add(speed_label)
        self.speed_label = speed_label
        
        # Speed buttons
        speed_up = arcade.gui.UIFlatButton(text="Speed Up (+)", width=200)
        speed_up.on_click = self.speed_up
        v_box.add(speed_up)
        
        speed_down = arcade.gui.UIFlatButton(text="Speed Down (-)", width=200)
        speed_down.on_click = self.speed_down
        v_box.add(speed_down)
        
        # Day type buttons
        weekday_btn = arcade.gui.UIFlatButton(text="Weekday", width=200)
        weekday_btn.on_click = lambda e: self.set_day_type("weekday")
        v_box.add(weekday_btn)
        
        saturday_btn = arcade.gui.UIFlatButton(text="Saturday", width=200)
        saturday_btn.on_click = lambda e: self.set_day_type("saturday")
        v_box.add(saturday_btn)
        
        sunday_btn = arcade.gui.UIFlatButton(text="Sunday", width=200)
        sunday_btn.on_click = lambda e: self.set_day_type("sunday")
        v_box.add(sunday_btn)
        
        # Create anchor and add v_box
        anchor = self.ui_manager.add(
            arcade.gui.UIAnchorLayout()
        )
        anchor.add(
            child=v_box,
            anchor_x="right",
            anchor_y="top",
            align_x=-20,
            align_y=-20
        )

    def toggle_pause(self, event):
        self.paused = not self.paused
        self.play_button.text = "Play" if self.paused else "Pause"

    def speed_up(self, event):
        self.time_speed = min(240, self.time_speed + 10)
        self.speed_label.text = f"Speed: {self.time_speed}x"

    def speed_down(self, event):
        self.time_speed = max(10, self.time_speed - 10)
        self.speed_label.text = f"Speed: {self.time_speed}x"

    def set_day_type(self, day_type):
        self.day_type = day_type
        self.trains = generate_trains(self.day_type)
        self.sim_time = datetime(2026, 2, 2, 5, 0)
        self.passengers = 0

    def on_draw(self):
        self.clear()
        
        # Draw metro line
        arcade.draw_line_strip(blue_line_path, arcade.color.BLUE, 5)
        
        # Draw stations
        for i, (x, y) in enumerate(blue_line_path):
            arcade.draw_circle_filled(x, y, 5, arcade.color.WHITE)
            station_name = blue_line_stations[i]["name"][:15]
            arcade.draw_text(station_name, x + 10, y, arcade.color.WHITE, 8)
        
        # Draw trains
        for train in self.trains:
            if self.sim_time >= train["start_time"]:
                pos = train["position"] % len(blue_line_path)
                if pos < len(blue_line_path) - 1:
                    idx = int(pos)
                    fraction = pos - idx
                    x1, y1 = blue_line_path[idx]
                    x2, y2 = blue_line_path[min(idx + 1, len(blue_line_path) - 1)]
                    x = x1 + (x2 - x1) * fraction
                    y = y1 + (y2 - y1) * fraction
                    arcade.draw_circle_filled(x, y, 10, arcade.color.RED)
        
        # Draw info panel
        panel_x = 850
        arcade.draw_text(f"Sim Time: {self.sim_time.strftime('%H:%M')}", 
                        panel_x, 550, arcade.color.WHITE, 14, bold=True)
        arcade.draw_text(f"Passengers: {int(self.passengers):,}", 
                        panel_x, 520, arcade.color.WHITE, 12)
        arcade.draw_text(f"Day Type: {self.day_type.capitalize()}", 
                        panel_x, 490, arcade.color.WHITE, 12)
        arcade.draw_text(f"Active Trains: {sum(1 for t in self.trains if self.sim_time >= t['start_time'])}", 
                        panel_x, 460, arcade.color.WHITE, 12)
        
        # Busiest stations
        arcade.draw_text("Busiest Stations:", panel_x, 420, arcade.color.WHITE, 12, bold=True)
        arcade.draw_text("1. Central: ~20k", panel_x, 390, arcade.color.LIGHT_GRAY, 10)
        arcade.draw_text("2. Airport: ~15k", panel_x, 370, arcade.color.LIGHT_GRAY, 10)
        arcade.draw_text("3. Guindy: ~10k", panel_x, 350, arcade.color.LIGHT_GRAY, 10)
        
        # Draw UI
        self.ui_manager.draw()

    def on_update(self, delta_time):
        if not self.paused and self.sim_time < self.end_time:
            self.sim_time += timedelta(seconds=delta_time * self.time_speed)
            for train in self.trains:
                if self.sim_time >= train["start_time"]:
                    train["position"] += train["speed"] * delta_time
            
            # Accumulate passengers
            monthly_scale = monthly_ridership.get(self.month, sum(monthly_ridership.values()) / len(monthly_ridership))
            self.passengers += (monthly_scale / 30 / 86400) * delta_time * random.uniform(0.8, 1.2)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.toggle_pause(None)
        elif key == arcade.key.UP:
            self.speed_up(None)
        elif key == arcade.key.DOWN:
            self.speed_down(None)

if __name__ == "__main__":
    window = MetroSimulation()
    arcade.run()
