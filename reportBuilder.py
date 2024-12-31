import subprocess
import sys
from pathlib import Path
import zmq
import os

dbFilePath = "./lims_data.csv"
exportsFolderPath = "./exports"
newlineChar = "\n"
passedIDStrings = sys.argv[1:]  # list of IDs to export
missingIDs = []
exportedIDs = []


# compiles data and prints it to a text file
def compileFile(headerList, dataList):
    index = 0
    fileContent = []
    if len(headerList) != len(dataList):
        print("Error: Mismatched Columns")
        print(dataList)
        print(f"{len(headerList)} columns in the Header, {len(dataList)} columns in this row")
        sys.exit(-2)
    Path("exports").mkdir(exist_ok=True)  #check if exportsFolderPath exists, if not create it
    with open(f"{exportsFolderPath}/Order{dataList[0]}", "w") as exportFile:
        while index < len(headerList):
            headerList[index] = headerList[index].replace("_", " ").title()
            fileContent.append(f"{headerList[index]}: {dataList[index]}{newlineChar}{newlineChar}")
            index += 1
        fileContent[-1] = fileContent[-1][:-1]
        exportFile.writelines(fileContent)
        exportedIDs.append(int(dataList[0]))


# Prints all IDs not found in the database
def endProgram(exitCode):
    if len(exportedIDs) > 0:
        exportedMesg = "File IDs "
        for id in exportedIDs:
            exportedMesg += f"{id}, "
        exportedMesg = exportedMesg[:-2] + " exported."
        print(exportedMesg)
    if len(missingIDs) > 0:
        notFoundMesg = "File IDs "
        for id in missingIDs:
            notFoundMesg += f"{id}, "
        notFoundMesg = notFoundMesg[:-2] + " not found."
        print(notFoundMesg)
    sys.exit(exitCode)


passedIDs = sorted(list(map(int, passedIDStrings)))  # turn all passedIDs into ints
# open file
with open(dbFilePath, 'r') as dbFile:
    index = 0
    headers = dbFile.readline().strip().split(",")
    for line in dbFile:  # read data from file row by row
        row = line.strip().split("\"")  # split on "\""
        if isinstance(row, list):
            i = 0
            tempRow = []
            while i < len(row):
                if i % 2 == 0:
                    if row[i][-1] == ",":
                        row[i] = row[i][:-1]
                    elif row[i][0] == "," and i != 0:
                        row[i] = row[i][1:]
                    tempRow.append(row[i].split(","))
                else:
                    tempRow.append([row[i]])
                i += 1
            row = sum(tempRow, [])  # flatten sub-lists
        else:
            row = row.split(",")
        rowID = int(row[0])  # turn row[0] to int
        if rowID in passedIDs:
            compileFile(headers, row)
            passedIDs.remove(rowID)
            if len(passedIDs) == 0:
                endProgram(0)
        elif passedIDs and rowID > passedIDs[0]:
            missingIDs.append(passedIDs[0])
            passedIDs.remove(passedIDs[0])
            if len(passedIDs) == 0:
                endProgram(0)


def exportMicroservice():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5562")
    print("Service running on port 5562.")

    while True:
        message = socket.recv_json()
        print(f"Received request: {message}")

        ids = message.get("ids")
        if ids:
            try:
                id_args = [str(id) for id in ids]
                python_location = os.path.join(os.path.dirname(__file__), "venv", "Scripts", "python.exe")
                subprocess.run([python_location, "reportBuilder.py", *id_args])
                response = {"status": "success", "message": f"Processed IDs: {ids}"}
            except Exception as e:
                response = {"status": "error", "message": str(e)}
        else:
            response = {"status": "error", "message": "Invalid request: Work Order ID is required."}

        socket.send_json(response)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        passedIDStrings = sys.argv[1:]
        process_ids(passedIDStrings)
    else:
        exportMicroservice()
