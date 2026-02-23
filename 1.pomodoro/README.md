# 🍅 Pomodoro Timer Application

A fully functional Pomodoro Timer built with Python and Tkinter, featuring multiple themes, customizable work/break intervals, and sound notifications.

## Features

### ⏱️ Timer Functionality
- **Large Timer Display**: Shows countdown in MM:SS format with bold 60pt font
- **Automatic Mode Switching**: Automatically switches between work and break sessions
- **Pause/Resume**: Pause and resume your timer at any time
- **Session Counter**: Tracks completed work sessions

### 🎨 Themes
Choose from three beautiful themes:

1. **Light Theme**
   - Clean white background
   - Dark text for easy reading
   - Blue accent color

2. **Dark Theme** (Default)
   - Modern dark gray background
   - Light text to reduce eye strain
   - Orange accent for visual appeal

3. **Focus Theme**
   - Minimal black background
   - Shows only timer, status, and controls
   - Perfect for distraction-free work

### ⚙️ Customization Options

**Work Time Selection:**
- 15 minutes
- 25 minutes (Default - Classic Pomodoro)
- 35 minutes
- 45 minutes

**Break Time Selection:**
- 5 minutes (Default)
- 10 minutes
- 15 minutes

**Sound Settings:**
- 🔔 Start Sound: Plays when timer starts (ON by default)
- 🔔 End Sound: Plays when session ends with double beep (ON by default)
- 🔔 Tick Sound: Plays every second (OFF by default)

## Installation

No installation required! Just Python 3.x with built-in tkinter.

### Requirements
- Python 3.6 or higher
- tkinter (included with Python)

### Running the Application

```bash
python3 app.py
```

Or on Windows:
```bash
python app.py
```

## Usage Guide

### Starting a Pomodoro Session
1. Select your preferred work time (default: 25 minutes)
2. Select your preferred break time (default: 5 minutes)
3. Choose a theme (Light/Dark/Focus)
4. Configure sound settings if desired
5. Click **Start** to begin your work session

### During a Session
- The timer counts down in MM:SS format
- The status label shows your current state
- Click **Pause** to pause the timer
- Click **Resume** to continue
- Click **Reset** to restart with current settings

### How It Works
1. **Work Session**: Focus on your task for the selected duration
2. **Automatic Break**: When work ends, break timer starts automatically
3. **Session Complete**: After break, return to work automatically
4. **Counter Updates**: Session counter increments after each work period

## Keyboard-Free Operation

All functionality is accessible through mouse clicks - no keyboard required!

## Cross-Platform Sound

Sound notifications use the built-in system bell (`tkinter.bell()`), ensuring compatibility across:
- Windows
- macOS
- Linux

## Technical Details

### Architecture
```python
PomodoroApp (Main Class)
├── Theme Management
├── Timer Logic (1-second intervals)
├── Sound System
├── UI Components
└── State Management
```

### File Structure
```
1.pomodoro/
├── app.py                    # Main application
├── pomodoro.png              # Icon/image
├── README.md                 # This file
├── IMPLEMENTATION_SUMMARY.md # Technical details
└── TEST_REPORT.md           # Test results
```

## Code Quality

✅ Clean, Pythonic code  
✅ Comprehensive documentation  
✅ No external dependencies  
✅ Cross-platform compatible  
✅ 414 lines of well-structured code  

## Screenshots

### Light Theme
Wide, clean interface with work/break time selectors, theme options, sound settings, large timer display, session counter, and control buttons.

### Dark Theme (Default)
Same layout with dark gray background and orange accents for comfortable viewing.

### Focus Theme
Minimal interface showing only:
- Large white timer on black background
- Status label
- Start/Pause and Reset buttons

## Tips for Best Results

1. **Use the Classic 25/5**: Start with 25-minute work and 5-minute break
2. **Enable End Sound**: Get notified when it's time to switch
3. **Try Focus Mode**: Switch to Focus theme during work sessions
4. **Disable Tick Sound**: Keep it off to avoid distraction during focus time
5. **Track Progress**: Watch your session counter grow!

## The Pomodoro Technique

The Pomodoro Technique is a time management method developed by Francesco Cirillo:

1. Choose a task
2. Set timer for 25 minutes (one "Pomodoro")
3. Work on the task until timer rings
4. Take a short break (5 minutes)
5. Every 4 Pomodoros, take a longer break (15-30 minutes)

This app automates the timer management for you!

## Troubleshooting

**Timer doesn't start?**
- Click the Start button
- Ensure a work time is selected

**No sound?**
- Check sound toggles are enabled
- System sound must be on
- Some systems may have bell disabled

**Theme not changing?**
- Click the theme radio button again
- Theme changes are immediate

## License

This is a practice project for educational purposes.

## Author

Created as part of the 2026 GitHub Copilot Hands-On demonstration.

---

**Enjoy productive work sessions with the Pomodoro Timer! 🍅⏱️**
