import zmq
import csv
import json


class searchMicroservice:
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

    def search_work_order(self, work_order_id):
        # Search for the work order by ID
        for wo in self.work_orders:
            if wo["work_order_id"] == work_order_id:
                return wo
        return None

    def start_service(self):
        # Connection to main program, ZeroMQ
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5555")

        print("Search microservice is running on port 5555.")
        while True:
            message = socket.recv_json()
            print(f"Received request: {message}")

            work_order_id = message.get("work_order_id")
            result = self.search_work_order(work_order_id)

            if result:
                response = {"status": "found", "work_order": result}
            else:
                response = {"status": "not_found", "message": "No work order found."}

            socket.send_json(response)


if __name__ == "__main__":
    service = searchMicroservice()
    service.start_service()
