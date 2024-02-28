import vgamepad as vg
import pyautogui
import threading
import time
import keyboard

# Configurable
monitor_width = 1920
# How far you need to travel for full steering
# if this value is 1.0 you need to travel to the border of the monitor for full steering
# if it is 0.5 you need to travel halfway to the border, etc
monitor_range = 1.0
polling_rate = 0.002 # in seconds
reset_button = 'delete'
accel_button = 'w'
brake_button = 'ctrl'

# Don't edit these
steering = 0.0
exit_flag = False

# Function to clamp the steering value within the range [-1.0, 1.0]
def clamp_steering(value):
    return max(-1.0, min(1.0, value))

# Function to reset the mouse position to the center of the monitor
def reset_mouse_position():
    pyautogui.moveTo(monitor_width / 2, pyautogui.position()[1])

# Function to determine mouse movement direction and update steering variable
def update_steering():
    global steering
    global exit_flag
    while not exit_flag:
        mouse_x = pyautogui.position()[0]
        relative_position = (mouse_x / monitor_width) - 0.5  # Calculate relative position [-0.5, 0.5]
        steering = relative_position * 2.0 / monitor_range  # Map relative position to steering [-1.0, 1.0]
        steering = clamp_steering(steering)
        print("Steering:", steering)  # Print the current steering value
        time.sleep(polling_rate)

# Start the mouse movement detection thread
mouse_thread = threading.Thread(target=update_steering)
mouse_thread.start()

# Create vgamepad object
gamepad = vg.VX360Gamepad()

try:
    while True:
        # Check for the Delete key press to reset mouse position
        if keyboard.is_pressed(reset_button):
            reset_mouse_position()

        # Update the gamepad state with the steering value
        gamepad.left_joystick_float(x_value_float=steering, y_value_float=128)

        # Update the gamepad state with the left trigger value
        if keyboard.is_pressed(brake_button):
            left_trigger = 1.0
        else:
            left_trigger = 0.0
        gamepad.left_trigger_float(value_float=left_trigger)

        # Update the gamepad state with the right trigger value
        if keyboard.is_pressed(accel_button):
            right_trigger = 1.0
        else:
            right_trigger = 0.0
        gamepad.right_trigger_float(value_float=right_trigger)

        gamepad.update()
        time.sleep(polling_rate)

except KeyboardInterrupt:
    print("\nExiting...")
    exit_flag = True
    mouse_thread.join()  # Wait for the mouse movement detection thread to exit
    gamepad.reset()
