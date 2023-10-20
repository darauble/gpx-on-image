#!/usr/bin/env python3
import os
import math
import gpxpy
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    earth_radius = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Calculate the distance in kilometers
    distance = earth_radius * c

    return distance

def calculate_bearing_radians(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Calculate the difference in longitudes
    dlon = lon2 - lon1

    # Calculate the bearing using the spherical trigonometry formula
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = math.atan2(y, x)

    return bearing

def calculate_bearing(lat1, lon1, lat2, lon2):
    # Convert the bearing from radians to degrees
    bearing = math.degrees(calculate_bearing_radians(lat1, lon1, lat2, lon2))

    # Normalize the bearing to the range [0, 360]
    bearing = (bearing + 360) % 360

    return bearing

def calculate_true_angle(angle):
    if angle >= 0 and angle <= 90:
        return angle
    elif angle > 90 and angle <= 180:
        return angle - 90
    elif angle > 180 and angle <= 270:
        return angle - 180
    elif angle > 270 and angle <= 360:
        return angle - 270

def calculate_rectangle(hypotenuse, angle):
    theta_radians = math.radians(angle)

    a = hypotenuse * math.cos(theta_radians)
    b = hypotenuse * math.sin(theta_radians)

    return (b, a)

def draw_gpx_on_image(image_path, gpx_path, output_path, margin_percent):
    # Open the image
    img = Image.open(image_path)
    img_width, img_height = img.size
    
    #margin_percent = 0.65
    
    # Leave some margins between the track and the image
    limit_width = math.floor(img_width * margin_percent)
    limit_height = math.floor(img_height * margin_percent)
    
    if limit_width > limit_height:
        limit_width = limit_height
    else:
        limit_height = limit_width
    
    # Center the track in the image
    width_center = (img_width / 2)
    height_center = (img_height / 2)

    # Create a new image with a white background
    result_img = Image.new("RGB", (img_width, img_height), "white")

    # Paste the original image onto the result image
    result_img.paste(img, (0, 0))

    # Calculate the line width, 1% of longest image side
    line_width = max(img_width, img_height) // 100

    half_pi = math.pi / 2

    # Load and parse the GPX file
    gpx_file = open(gpx_path, "r")
    gpx = gpxpy.parse(gpx_file)
    gpx_file.close()

    # Create a drawing object to draw on the result image
    draw = ImageDraw.Draw(result_img)

    for track in gpx.tracks:
        for segment in track.segments:
            max_lat = -500
            min_lat = 500
            max_lon = -500
            min_lon = 500

            for point in segment.points:
                if point.latitude > max_lat:
                    max_lat = point.latitude
                elif point.latitude < min_lat:
                    min_lat = point.latitude
                
                if point.longitude > max_lon:
                    max_lon = point.longitude
                elif point.longitude < min_lon:
                    min_lon = point.longitude
            
            hypotenuse = haversine(max_lat, max_lon, min_lat, min_lon)
            # print("Track segment max and min coordinates:", max_lat, max_lon, min_lat, min_lon)
            # print("Distance between points, km: ", hypotenuse)
            
            bearing = calculate_bearing(max_lat, max_lon, min_lat, min_lon)
            angle = calculate_true_angle(bearing)
            
            # print("Bearing from max to min: ", bearing)
            # print("True angle: ", angle)
            
            hor_len, ver_len = calculate_rectangle(hypotenuse, angle)
            # print("Horizontal length, vertical length:", hor_len, ver_len)

            max_track_len = hor_len

            if hor_len < ver_len:
                max_track_len = ver_len

            mid_lat = (max_lat + min_lat) / 2
            mid_lon = (max_lon + min_lon) / 2

            km_pixels_coeff = limit_width / max_track_len

            points = []

            for point in segment.points:
                center_distance = haversine(mid_lat, mid_lon, point.latitude, point.longitude) * km_pixels_coeff
                center_bearing = calculate_bearing_radians(mid_lat, mid_lon, point.latitude, point.longitude) - half_pi

                x = center_distance * math.cos(center_bearing) + width_center
                y = center_distance * math.sin(center_bearing) + height_center

                points.append((x, y))
            
            # Draw the track line
            draw.line(points, fill="white", width=line_width)

    # Save the result image
    result_img.save(output_path)

def browse_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg")])
    image_entry.delete(0, tk.END)
    image_entry.insert(0, file_path)
    
    input_image = image_entry.get()
    input_img = Image.open(input_image)
    input_img.thumbnail((400, 400))
    input_photo = ImageTk.PhotoImage(input_img)
    input_label.config(image=input_photo)
    input_label.image = input_photo

    output_entry.insert(0, add_suffix_to_filename(image_entry.get(), "gpx"))

def browse_gpx():
    file_path = filedialog.askopenfilename(filetypes=[("GPX files", "*.gpx")])
    gpx_entry.delete(0, tk.END)
    gpx_entry.insert(0, file_path)

def draw_button_clicked():
    input_image = image_entry.get()
    input_gpx = gpx_entry.get()
    output_image = output_entry.get()

    draw_gpx_on_image(input_image, input_gpx, output_image, float(margin_entry.get()) / 100)

    output_img = Image.open(output_image)
    output_img.thumbnail((400, 400))
    output_photo = ImageTk.PhotoImage(output_img)
    output_label.config(image=output_photo)
    output_label.image = output_photo

def validate_margin_input(P):
    if P == "" or P.isdigit() and 1 <= int(P) <= 100:
        return True
    return False

def add_suffix_to_filename(filename, suffix):
    base_name, extension = os.path.splitext(filename)
    new_filename = f"{base_name}_{suffix}{extension}"
    return new_filename

root = tk.Tk()
root.title("GPX Track on Image Drawer")

image_label = tk.Label(root, text="Image File:")
image_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)

image_entry = tk.Entry(root, width=100)
image_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=5)

image_browse_button = tk.Button(root, text="Browse", command=browse_image)
image_browse_button.grid(row=0, column=3, padx=5, pady=5)

gpx_label = tk.Label(root, text="GPX File:")
gpx_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)

gpx_entry = tk.Entry(root, width=100)
gpx_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=5)

gpx_browse_button = tk.Button(root, text="Browse", command=browse_gpx)
gpx_browse_button.grid(row=1, column=3, padx=5, pady=5)

output_label = tk.Label(root, text="Output File:")
output_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)

output_entry = tk.Entry(root, width=100)
output_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=5)

draw_button = tk.Button(root, text="Draw GPX", command=draw_button_clicked)
draw_button.grid(row=2, column=3, padx=5, pady=5)

# Create a validation command for the entry field
margin_validate = root.register(validate_margin_input)

# Adding the new entry field
margin_label = tk.Label(root, text="Track margin in % (1 to 100):")
margin_label.grid(row=3, column=0, padx=10, pady=5, sticky=tk.E)

margin_default = tk.StringVar(value="75")  # Set the default value
margin_entry = tk.Entry(root, validate="key", validatecommand=(margin_validate, "%P"), textvariable=margin_default)
margin_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=5, sticky=tk.W)

input_label = tk.Label(root, text="Input Image")
input_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

output_label = tk.Label(root, text="Output Image")
output_label.grid(row=4, column=2, columnspan=2, padx=10, pady=5)

root.mainloop()

