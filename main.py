import tkinter as tk
from tkinter import filedialog
from PIL import Image
import subprocess, shutil, face_recognition, os, customtkinter



#Sets up main window
home_screen=customtkinter.CTk()
home_screen.geometry("1200x600")
home_screen.title("TheftGuard")
customtkinter.set_appearance_mode("light")
home_screen.resizable(width=True, height=True)



#Creating the testing and known images directory
testing_dir = os.getcwd() + "/Testing_Images"
if not (os.path.exists(testing_dir)):
    os.makedirs(testing_dir)
else:
    # If the testing directory exists, clear it
    shutil.rmtree(testing_dir)
    os.makedirs(testing_dir)
known_dir = os.getcwd() + "/Known_People"
if not (os.path.exists(known_dir)):
    os.makedirs(known_dir)



def upload():
    #Updates Verify Button incase of previous attempts to verify without images selected
    verifyButton.configure(text="Verify")
    #Asks user to select files, then for each file they select create a label widget with that image to display it
    filepath = list(filedialog.askopenfilenames(title="Select the file", filetypes=((".jpg","*.jpg"), ("All Files", "*.*"))))
    for i in filepath:
        #Saves the file to the testing directory
        shutil.copy(i, testing_dir)
        #Displays the image on the users window
        my_image=customtkinter.CTkImage(light_image=Image.open(i), dark_image=Image.open(i), size=(288, 180))
        image_Label=customtkinter.CTkLabel(master=selectedImages, text=os.path.basename(i), image=my_image, fg_color="white")
        image_Label.pack(pady=10)
    
def verify():
    #Checking for no images selected error
    Known_People_Length = os.listdir(known_dir) 
    if len(Known_People_Length) == 0: 
        #Changes Verify Button to tell user to select images to begin
        verifyButton.configure(text="No Images Selected Yet")
    else: 
        output = subprocess.check_output(['face_recognition', known_dir, testing_dir])
        #Converts the byte output into a string output
        output_str = output.decode('utf-8')
        #Splits the text by each image test, then separates the name from the image test
        lines = output_str.strip().split('\r\n')
        
        # Compile and organize the matches
        matches = []
        for line in lines:
            parts = line.split(',')
            # Make sure there's at least 2 parts after splitting
            if len(parts) > 1:
                test_image_path = parts[0]
                name = parts[1].strip()
                known_image_path = None
                if name != "unknown_person":
                    # Find the matched image in "Known_People" directory
                    for file in os.listdir(known_dir):
                        # Extract the file name without the .jpg
                        file_name = os.path.splitext(file)[0]
                        if file_name == name:
                            #if match is found calculate the file path and break
                            known_image_path = os.path.join(known_dir, file)
                            break
                
                matches.append((test_image_path, name, known_image_path))
            else:
                print(f"Warning: Line format unexpected: '{line}'")
        
        # Create the assailant selection window
        assailant_selection_window = customtkinter.CTkToplevel(home_screen)
        assailant_selection_window.title("Face Verification Results")
        assailant_selection_window.geometry("800x600")
        
        # Create a frame for the matches
        matches_frame = customtkinter.CTkScrollableFrame(
            master=assailant_selection_window, 
            label_text="Matched Faces", 
            label_font=("Arial", 20)
        )
        matches_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Display each matched image
        if matches:
            for test_image_path, name, known_image_path in matches:
                # Create a frame for each match
                match_frame = customtkinter.CTkFrame(master=matches_frame)
                match_frame.pack(pady=10, padx=10, fill="x")
                try:
                    # Display matched image if found, else display test image
                    display_path = known_image_path if known_image_path and name != "unknown_person" else test_image_path
                    img = Image.open(display_path)
                    img_display = customtkinter.CTkImage(
                        light_image=img, 
                        dark_image=img,
                        size=(200, 150)
                    )
                    img_label = customtkinter.CTkLabel(
                        master=match_frame, 
                        text="", 
                        image=img_display,
                        fg_color="white"
                    )
                    img_label.pack(side="left", padx=10, pady=10)
                    
                    if name == "unknown_person":
                        name_text = "Unknown Person"
                    else:
                        name_text = f"Matched: {name}"
                    name_label = customtkinter.CTkLabel(
                        master=match_frame,
                        text=name_text,
                        font=("Arial", 16)
                    )
                    name_label.pack(side="left", padx=20)
                    
                    source_text = "(Test Image)" if name == "unknown_person" else "(Reference Image)"
                    source_label = customtkinter.CTkLabel(
                        master=match_frame,
                        text=source_text,
                        font=("Arial", 12)
                    )
                    source_label.pack(side="left", padx=5)
                    
                except Exception as e:
                    print(f"Error loading image {display_path}: {e}")
                    error_label = customtkinter.CTkLabel(
                        master=match_frame,
                        text=f"Error loading image for: {name}",
                        font=("Arial", 16)
                    )
                    error_label.pack(padx=10, pady=10)
        else:
            # No matches were found
            no_match_label = customtkinter.CTkLabel(
                master=matches_frame,
                text="No face matches were found in the uploaded images.",
                font=("Arial", 16)
            )
            no_match_label.pack(padx=20, pady=20)
        
        # Add close button
        close_button = customtkinter.CTkButton(
            master=assailant_selection_window,
            text="Close",
            fg_color="green",
            font=("Arial", 20),
            command=assailant_selection_window.destroy
        )
        close_button.pack(pady=20)



#Creates all the widgets used in main window
selectedImages = customtkinter.CTkScrollableFrame(master=home_screen, label_text="Selected Images", label_font=("Arial", 20))
selectedImages.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

uploadButton = customtkinter.CTkButton(master=home_screen, text="Upload", fg_color="green", font=("Arial", 30), command=upload)
uploadButton.grid(row=1, column=0, padx=100, pady=20, sticky="nsew")

textFrame = customtkinter.CTkFrame(master=home_screen)
textFrame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
titleLabel = customtkinter.CTkLabel(master=textFrame, text="TheftGuard", font=("Arial", 40))
titleLabel.pack(pady=5, padx=20, fill="both", expand=True)
textbox = customtkinter.CTkTextbox(master=textFrame, font=("Arial", 20))
textbox.pack(pady=(0,20), padx=20, fill="both", expand=True)
textbox.insert("0.0", "To start screenshot a picture of the assailant where their face is most visible and upload it to the block to the left, then press the Verify button below. To increase accuracy, upload multiple pictures. Make sure the only face visible in the image you upload is the assailant's face, cropping the imagine if necessary.")

verifyButton = customtkinter.CTkButton(master=home_screen, text="Verify", fg_color="green", font=("Arial", 30), command=verify)
verifyButton.grid(row=1, column=1, padx=100, pady=20, sticky="nsew")

home_screen.grid_columnconfigure((0, 1), weight=1)
home_screen.grid_rowconfigure((0, 1), weight=1)



#Starts the program by running the main window
home_screen.mainloop()