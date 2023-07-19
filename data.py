import csv
import cv2
import os
from datetime import datetime


def add_student():
    with open("student_data.csv", mode="w", newline=""):
        pass
    with open("student_data.csv", mode="a", newline="") as file:
        writer = csv.writer(file)

        image_folder = "Images"
        image_files = sorted(
            os.listdir(image_folder), key=lambda x: int(os.path.splitext(x)[0])
        )

        for i, image_file in enumerate(image_files, start=1):
            image_path = os.path.join(image_folder, image_file)
            img = cv2.imread(image_path)

            # Resize image while preserving aspect ratio
            width = 300
            height = int(img.shape[0] * (width / img.shape[1]))
            img = cv2.resize(img, (width, height))

            # Create window and display image on top
            cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
            cv2.imshow("Image", img)
            cv2.setWindowProperty("Image", cv2.WND_PROP_TOPMOST, 1)
            cv2.resizeWindow("Image", width, height)

            # Wait for key press
            cv2.waitKey(0)

            name = input("Enter student name: ")
            major = input("Enter student major: ")
            starting_year = int(input("Enter student starting year: "))
            cv2.destroyAllWindows()
            writer.writerow([name, major, starting_year, image_path, datetime.now()])
            print(f"Data added for Image {i} successfully!")
            cv2.destroyAllWindows()
    print("All student data added successfully!")


if __name__ == "__main__":
    add_student()
