# Pomodoro Timer App
import tkinter as tk
from tkinter import ttk, font


class PomodoroApp:
    """A fully functional Pomodoro Timer with multiple themes and customization options."""
    
    # Theme configurations
    THEMES = {
        'Light': {
            'bg': '#ffffff',
            'fg': '#2b2b2b',
            'accent': '#007acc',
            'button_bg': '#e0e0e0',
            'button_fg': '#2b2b2b',
            'timer_fg': '#007acc'
        },
        'Dark': {
            'bg': '#2b2b2b',
            'fg': '#e0e0e0',
            'accent': '#ff6b35',
            'button_bg': '#3a3a3a',
            'button_fg': '#e0e0e0',
            'timer_fg': '#ff6b35'
        },
        'Focus': {
            'bg': '#000000',
            'fg': '#ffffff',
            'accent': '#ffffff',
            'button_bg': '#1a1a1a',
            'button_fg': '#ffffff',
            'timer_fg': '#ffffff'
        }
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("500x650")
        self.root.resizable(False, False)
        
        # Timer variables
        self.work_time = tk.IntVar(value=25)  # minutes
        self.break_time = tk.IntVar(value=5)  # minutes
        self.current_theme = tk.StringVar(value='Dark')
        
        # Sound settings
        self.start_sound = tk.BooleanVar(value=True)
        self.end_sound = tk.BooleanVar(value=True)
        self.tick_sound = tk.BooleanVar(value=False)
        
        # Timer state
        self.is_running = False
        self.is_work_mode = True
        self.remaining_seconds = 0
        self.session_count = 0
        self.timer_id = None
        
        # Create UI
        self.create_widgets()
        self.apply_theme()
        self.reset_timer()
        
    def create_widgets(self):
        """Create all UI widgets."""
        
        # Main container
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        self.title_label = tk.Label(
            self.main_frame,
            text="🍅 Pomodoro Timer",
            font=('Arial', 20, 'bold')
        )
        self.title_label.pack(pady=(0, 20))
        
        # Work time selection
        self.work_frame = tk.LabelFrame(
            self.main_frame,
            text="Work Time",
            font=('Arial', 11, 'bold'),
            padx=10,
            pady=10
        )
        self.work_frame.pack(fill=tk.X, pady=(0, 10))
        
        work_times = [15, 25, 35, 45]
        for time_val in work_times:
            rb = tk.Radiobutton(
                self.work_frame,
                text=f"{time_val} min",
                variable=self.work_time,
                value=time_val,
                font=('Arial', 10),
                command=self.reset_timer
            )
            rb.pack(side=tk.LEFT, padx=5)
        
        # Break time selection
        self.break_frame = tk.LabelFrame(
            self.main_frame,
            text="Break Time",
            font=('Arial', 11, 'bold'),
            padx=10,
            pady=10
        )
        self.break_frame.pack(fill=tk.X, pady=(0, 10))
        
        break_times = [5, 10, 15]
        for time_val in break_times:
            rb = tk.Radiobutton(
                self.break_frame,
                text=f"{time_val} min",
                variable=self.break_time,
                value=time_val,
                font=('Arial', 10),
                command=self.reset_timer
            )
            rb.pack(side=tk.LEFT, padx=5)
        
        # Theme selection
        self.theme_frame = tk.LabelFrame(
            self.main_frame,
            text="Theme",
            font=('Arial', 11, 'bold'),
            padx=10,
            pady=10
        )
        self.theme_frame.pack(fill=tk.X, pady=(0, 10))
        
        themes = ['Light', 'Dark', 'Focus']
        for theme in themes:
            rb = tk.Radiobutton(
                self.theme_frame,
                text=theme,
                variable=self.current_theme,
                value=theme,
                font=('Arial', 10),
                command=self.apply_theme
            )
            rb.pack(side=tk.LEFT, padx=5)
        
        # Sound settings
        self.sound_frame = tk.LabelFrame(
            self.main_frame,
            text="Sound Settings",
            font=('Arial', 11, 'bold'),
            padx=10,
            pady=10
        )
        self.sound_frame.pack(fill=tk.X, pady=(0, 20))
        
        cb1 = tk.Checkbutton(
            self.sound_frame,
            text="Start Sound",
            variable=self.start_sound,
            font=('Arial', 10)
        )
        cb1.pack(side=tk.LEFT, padx=5)
        
        cb2 = tk.Checkbutton(
            self.sound_frame,
            text="End Sound",
            variable=self.end_sound,
            font=('Arial', 10)
        )
        cb2.pack(side=tk.LEFT, padx=5)
        
        cb3 = tk.Checkbutton(
            self.sound_frame,
            text="Tick Sound",
            variable=self.tick_sound,
            font=('Arial', 10)
        )
        cb3.pack(side=tk.LEFT, padx=5)
        
        # Timer display
        self.timer_frame = tk.Frame(self.main_frame)
        self.timer_frame.pack(pady=20)
        
        self.timer_label = tk.Label(
            self.timer_frame,
            text="25:00",
            font=('Arial', 60, 'bold')
        )
        self.timer_label.pack()
        
        # Status label
        self.status_label = tk.Label(
            self.main_frame,
            text="Ready to Work",
            font=('Arial', 14)
        )
        self.status_label.pack(pady=(0, 10))
        
        # Session counter
        self.session_label = tk.Label(
            self.main_frame,
            text="Sessions Completed: 0",
            font=('Arial', 11)
        )
        self.session_label.pack(pady=(0, 20))
        
        # Control buttons
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(pady=(0, 10))
        
        self.start_button = tk.Button(
            self.button_frame,
            text="Start",
            font=('Arial', 12, 'bold'),
            width=10,
            command=self.start_pause
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = tk.Button(
            self.button_frame,
            text="Reset",
            font=('Arial', 12, 'bold'),
            width=10,
            command=self.reset_timer
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
    def apply_theme(self):
        """Apply the selected theme to all widgets."""
        theme_name = self.current_theme.get()
        theme = self.THEMES[theme_name]
        
        # Configure root window
        self.root.configure(bg=theme['bg'])
        
        # Configure main frame
        self.main_frame.configure(bg=theme['bg'])
        
        # Focus theme - hide settings panels
        if theme_name == 'Focus':
            self.title_label.pack_forget()
            self.work_frame.pack_forget()
            self.break_frame.pack_forget()
            self.theme_frame.pack_forget()
            self.sound_frame.pack_forget()
            self.session_label.pack_forget()
        else:
            # Show all widgets in normal themes
            self.title_label.pack(pady=(0, 20))
            self.title_label.configure(bg=theme['bg'], fg=theme['fg'])
            
            self.work_frame.pack(fill=tk.X, pady=(0, 10))
            self.work_frame.configure(bg=theme['bg'], fg=theme['fg'])
            
            self.break_frame.pack(fill=tk.X, pady=(0, 10))
            self.break_frame.configure(bg=theme['bg'], fg=theme['fg'])
            
            self.theme_frame.pack(fill=tk.X, pady=(0, 10))
            self.theme_frame.configure(bg=theme['bg'], fg=theme['fg'])
            
            self.sound_frame.pack(fill=tk.X, pady=(0, 20))
            self.sound_frame.configure(bg=theme['bg'], fg=theme['fg'])
            
            # Configure all radio buttons and checkbuttons
            for widget in (self.work_frame.winfo_children() + 
                          self.break_frame.winfo_children() + 
                          self.theme_frame.winfo_children() + 
                          self.sound_frame.winfo_children()):
                if isinstance(widget, (tk.Radiobutton, tk.Checkbutton)):
                    widget.configure(
                        bg=theme['bg'],
                        fg=theme['fg'],
                        activebackground=theme['bg'],
                        activeforeground=theme['accent'],
                        selectcolor=theme['bg']
                    )
            
            self.session_label.pack(pady=(0, 20))
            self.session_label.configure(bg=theme['bg'], fg=theme['fg'])
        
        # Timer display (always visible)
        self.timer_frame.configure(bg=theme['bg'])
        self.timer_label.configure(bg=theme['bg'], fg=theme['timer_fg'])
        
        # Status label (always visible)
        self.status_label.configure(bg=theme['bg'], fg=theme['accent'])
        
        # Buttons (always visible)
        self.button_frame.configure(bg=theme['bg'])
        self.start_button.configure(
            bg=theme['button_bg'],
            fg=theme['button_fg'],
            activebackground=theme['accent'],
            activeforeground=theme['bg']
        )
        self.reset_button.configure(
            bg=theme['button_bg'],
            fg=theme['button_fg'],
            activebackground=theme['accent'],
            activeforeground=theme['bg']
        )
        
    def start_pause(self):
        """Toggle between start and pause."""
        if not self.is_running:
            # Start timer
            self.is_running = True
            self.start_button.configure(text="Pause")
            
            if self.is_work_mode:
                self.status_label.configure(text="Working...")
            else:
                self.status_label.configure(text="Break Time!")
            
            # Play start sound
            if self.start_sound.get():
                self.play_sound()
            
            # Start ticking
            self.tick()
        else:
            # Pause timer
            self.is_running = False
            self.start_button.configure(text="Resume")
            self.status_label.configure(text="Paused")
            
            # Cancel scheduled tick
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None
    
    def reset_timer(self):
        """Reset the timer to initial state."""
        # Cancel any running timer
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        
        # Reset state
        self.is_running = False
        self.is_work_mode = True
        self.start_button.configure(text="Start")
        
        # Set initial time
        self.remaining_seconds = self.work_time.get() * 60
        
        # Update display
        self.update_timer_display()
        self.status_label.configure(text="Ready to Work")
    
    def tick(self):
        """Called every second to update the timer."""
        if not self.is_running:
            return
        
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.update_timer_display()
            
            # Play tick sound
            if self.tick_sound.get():
                self.play_sound()
            
            # Schedule next tick
            self.timer_id = self.root.after(1000, self.tick)
        else:
            # Timer finished
            self.timer_finished()
    
    def timer_finished(self):
        """Called when timer reaches zero."""
        # Play end sound
        if self.end_sound.get():
            self.play_sound()
            self.root.after(100, self.play_sound)  # Double beep
        
        if self.is_work_mode:
            # Work session finished, increment counter
            self.session_count += 1
            self.session_label.configure(text=f"Sessions Completed: {self.session_count}")
            
            # Switch to break mode
            self.is_work_mode = False
            self.remaining_seconds = self.break_time.get() * 60
            self.status_label.configure(text="Break Time!")
        else:
            # Break finished, switch to work mode
            self.is_work_mode = True
            self.remaining_seconds = self.work_time.get() * 60
            self.status_label.configure(text="Working...")
        
        # Update display and continue
        self.update_timer_display()
        
        # Continue timer automatically
        self.timer_id = self.root.after(1000, self.tick)
    
    def update_timer_display(self):
        """Update the timer label with current time."""
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        self.timer_label.configure(text=time_str)
    
    def play_sound(self):
        """Play a sound using the system bell."""
        self.root.bell()


if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()
