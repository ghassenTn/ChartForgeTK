import tkinter as tk
from tkinter import ttk
import time
import math

class SmoothBarChart(tk.Canvas):
    def __init__(self, parent, width=800, height=600):
        super().__init__(parent, width=width, height=height, bg="white")
        self.data = []
        self.bars = []
        self.animation_duration = 500  # Animation time in milliseconds
        self.start_time = None
        self.target_data = []
        self.padding = 50  # Space for axes
    
    def ease_out_quad(self, t):
        """Easing function for smooth animation"""
        return 1 - (1 - t) ** 2

    def plot(self, data):
        """Smoothly transition to new bar values"""
        if not data:
            raise ValueError("Data cannot be empty")
        
        self.target_data = data
        self.start_time = time.time()
        self.data = [0] * len(data)  # Start bars from 0
        self.bars = []  # Store bar references
        
        self.animate_bars()  # Start animation

    def animate_bars(self):
        """Animates bars smoothly"""
        elapsed = (time.time() - self.start_time) * 1000  # Convert to ms
        progress = min(elapsed / self.animation_duration, 1)  # Normalize (0 to 1)
        eased_progress = self.ease_out_quad(progress)  # Apply easing
        
        self.delete("all")  # Clear previous frame
        
        bar_width = (self.winfo_width() - 2 * self.padding) / max(len(self.target_data), 1)
        
        for i, target_height in enumerate(self.target_data):
            current_height = self.data[i] + (target_height - self.data[i]) * eased_progress
            self.data[i] = current_height  # Update animated value
            
            x0 = self.padding + i * bar_width
            x1 = x0 + bar_width * 0.8
            y0 = self.winfo_height() - self.padding
            y1 = y0 - (current_height / max(self.target_data) * (self.winfo_height() - 2 * self.padding))
            
            # Draw bars with smooth gradient
            self.create_rectangle(x0, y1, x1, y0, fill="blue", outline="black")
            self.create_text((x0 + x1) / 2, y1 - 10, text=f"{int(current_height)}", fill="black")
        
        if progress < 1:
            self.after(16, self.animate_bars)  # Run next frame (60 FPS)
        else:
            self.data = self.target_data[:]  # Finalize animation

# Test Application
root = tk.Tk()
root.title("Smooth Bar Chart")

chart = SmoothBarChart(root, width=600, height=400)
chart.pack()

def update_chart():
    import random
    new_data = [random.randint(10, 100) for _ in range(5)]
    chart.plot(new_data)

btn = ttk.Button(root, text="Update Data", command=update_chart)
btn.pack()

update_chart()  # Initial plot
root.mainloop()
