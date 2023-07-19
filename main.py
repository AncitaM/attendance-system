import os
import numpy as np
import cv2
import face_recognition
import cvzone
import csv
from datetime import datetime, timedelta

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread("Resources/background.png")
# Importing the mode images into a list
folderModePath = "Resources/Modes"
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# Store the face encodings
encodeListKnownWithIds = []
students = []
studentInfo = {}

# Load the encodings from CSV
with open("student_data.csv", "r") as file:
    lines = file.readlines()
    for line in lines:
        data = line.strip().split(",")
        studentId = ((data[3].split("\\"))[1].split("."))[0]
        studentInfo = {
            "name": data[0].strip(),
            "major": data[1].strip(),
            "starting_year": data[2].strip(),
            "year": datetime.now().year - int(data[2].strip()),
            "path": data[3],
            "time": data[4],
        }
        img = cv2.imread(data[3])
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodeFace = face_recognition.face_encodings(img)[0]
        encodeListKnownWithIds.append((encodeFace, studentId))
        students.append(studentInfo)

modeType = 0
counter = 0
id = -1
studentInfo = {}
while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162 : 162 + 480, 55 : 55 + 640] = img
    imgBackground[44 : 44 + 633, 808 : 808 + 414] = imgModeList[modeType]
    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(
                [x[0] for x in encodeListKnownWithIds], encodeFace
            )
            faceDis = face_recognition.face_distance(
                [x[0] for x in encodeListKnownWithIds], encodeFace
            )

            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = encodeListKnownWithIds[matchIndex][1]
                studentInfo = students[matchIndex]
                currentTime = datetime.now()
                notedTime = datetime.strptime(
                    studentInfo["time"], "%Y-%m-%d %H:%M:%S.%f"
                )
                elapsedTime = currentTime - notedTime
                if elapsedTime > timedelta(seconds=30):
                    timePassed = True
                else:
                    timePassed = False
        if counter == 0:
            cvzone.putTextRect(imgBackground, "Loading", (275, 400))
            cv2.imshow("Face Attendance", imgBackground)
            cv2.waitKey(1)
            counter = 1
            modeType = 1

        if counter != 0:
            if counter == 1:
                # Get the Data
                for encodeFace, studentId in encodeListKnownWithIds:
                    if studentId == id:
                        break

                # Perform your desired actions with studentInfo
                # For example, print the student's name and major
                print(data)
                print("Name:", studentInfo["name"])
                print("Major:", studentInfo["major"])
                imgStudent = cv2.imread(studentInfo["path"])  # ONE WITH THE ERROR
                imgStudent = cv2.resize(imgStudent, (414, 633))
                imgBackground[44 : 44 + 633, 808 : 808 + 414] = imgStudent

            if counter <= 10:
                cv2.putText(
                    imgBackground,
                    f"Name: " + str(studentInfo["name"]),
                    (808 + 50, 445),
                    cv2.FONT_HERSHEY_COMPLEX,
                    1,
                    (0, 0, 0),
                    2,
                )
                cv2.putText(
                    imgBackground,
                    f"Major: " + str(studentInfo["major"]),
                    (925, 550),
                    cv2.FONT_HERSHEY_COMPLEX,
                    0.5,
                    (0, 0, 0),
                    2,
                )
                cv2.putText(
                    imgBackground,
                    f"ID: " + str(id),
                    (925, 493),
                    cv2.FONT_HERSHEY_COMPLEX,
                    0.5,
                    (0, 0, 0),
                    2,
                )
                cv2.putText(
                    imgBackground,
                    f"Current Year: " + str(studentInfo["year"]),
                    (925, 625),
                    cv2.FONT_HERSHEY_COMPLEX,
                    0.6,
                    (0, 0, 0),
                    2,
                )
                cv2.putText(
                    imgBackground,
                    f"Starting Year: " + str(studentInfo["starting_year"]),
                    (925, 650),
                    cv2.FONT_HERSHEY_COMPLEX,
                    0.6,
                    (0, 0, 0),
                    2,
                )
                imgStudent = cv2.imread(studentInfo["path"])  # ONE WITH THE ERROR
                imgStudent = cv2.resize(imgStudent, (250, 250))
                imgBackground[160 : 160 + 250, 890 : 890 + 250] = imgStudent

            elif 10 < counter < 20:
                if timePassed:
                    modeType = 2
                    students[matchIndex]["time"] = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S.%f"
                    )
                    studentInfo = students[matchIndex]
                else:
                    modeType = 3
                imgBackground[44 : 44 + 633, 808 : 808 + 414] = imgModeList[modeType]

            elif counter >= 20:
                counter = 0
                modeType = 0
                studentInfo = {}
                imgBackground[44 : 44 + 633, 808 : 808 + 414] = imgModeList[modeType]
            counter += 1

    else:
        modeType = 0
        counter = 0
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
with open("student_data.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    for studentInfo in students:
        data[0], data[1], data[2], data[3], data[4] = (
            studentInfo["name"],
            studentInfo["major"],
            studentInfo["starting_year"],
            studentInfo["path"],
            studentInfo["time"],
        )
        writer.writerow([data[0], data[1], data[2], data[3], data[4]])

cap.release()
cv2.destroyAllWindows()
