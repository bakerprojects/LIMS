import zmq
import csv
import json


class inProgressMicroservice:
    def __init__(self, csv_file="lims_data.csv"):
        self.work_orders = []
        self.load_from_csv(csv_file)

    def load_from_csv(self, csv_file):
        # load the csv database file
        with open(csv_file, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # organize and label the retrieved data
                work_order = {
                    "work_order_id": int(row["work_order_id"]),
                    "sample_id": row["sample_id"],
                    "collection_datetime": row["collection_datetime"],
                    "due_date": row["due_date"],
                    "analyses": row["analyses"],
                    "status": row["status"]
                }
                self.work_orders.append(work_order)

    def search_by_status(self, status):
        # Filter work orders by the status
        matching_work_orders = [wo for wo in self.work_orders if wo["status"].lower() == status.lower()]
        return matching_work_orders

    def start_service(self):
        # Connection to main program, ZeroMQ
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5559")

        print("Completion microservice is running on port 5559.")
        while True:
            message = socket.recv_json()
            print(f"Received request: {message}")

            status = message.get("status")
            if status:
                result = self.search_by_status(status)
                if result:
                    response = {"status": "found", "work_orders": result}
                else:
                    response = {"status": "not_found", "message": f"No work orders found with status '{status}'."}
            else:
                response = {"status": "error", "message": "Invalid request: 'status' field is required."}

            socket.send_json(response)


if __name__ == "__main__":
    service = inProgressMicroservice()
    service.start_service()
