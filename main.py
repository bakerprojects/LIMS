import csv
import zmq


def login():
    # User login, prompts for username and password
    username = input("Please enter your username: ")
    password = input("Please enter your password: ")
    # username and password storage
    return username == "admin" and password == "password"


def searchMicroservice(work_order_id):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    # Send request to the microservice
    request_message = {"work_order_id": work_order_id}
    socket.send_json(request_message)

    # Receive response from the microservice
    response = socket.recv_json()
    return response


def inProgressMicroservice(status):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5556")

    # Send request message to microservice
    request_message = {"status": status}
    socket.send_json(request_message)

    # Receive response message from microservice
    response = socket.recv_json()
    return response


def completionMicroservice(status):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5559")

    # Send request message to microservice
    request_message = {"status": status}
    socket.send_json(request_message)

    # Receive response message from microservice
    response = socket.recv_json()
    return response


def exportMicroservice(ids):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5562")

    # Send request message to microservice
    request = {"ids": [ids]}
    socket.send_json(request)

    # Receive response message from microservice
    response = socket.recv_json()
    return response


class WorkOrder:
    def __init__(self, sample_id, collection_datetime, due_date, analyses, status="In Progress", work_order_id=0):
        # Work order class that initializes the components of a work order
        self.sample_id = sample_id
        self.collection_datetime = collection_datetime
        self.due_date = due_date
        self.analyses = analyses
        self.status = status
        self.work_order_id = work_order_id


class WorkOrderManager:
    # Work order manager class, for manipulating work orders
    def __init__(self, csv_file="lims_data.csv"):
        # Initialize work order manager, links csv file used as database
        self.lims_data = csv_file
        self.work_orders = []
        self.next_id = 1
        self.load_from_csv()

    def create_work_order(self, sample_id, collection_datetime, due_date, analyses):
        # Creates work order from specified user input, adds to csv database
        work_order = WorkOrder(sample_id, collection_datetime, due_date, analyses, status="In Progress",
                               work_order_id=self.next_id)
        self.work_orders.append(work_order)
        self.next_id += 1
        self.save_to_csv()
        return work_order

    def update_work_order(self):
        print("Welcome to the Update Work Orders Page."
              "\nPlease have your work order number ready."
              "\nHere you will be able to update work orders in the system.")
        update_id = int(input("Enter the Work Order ID to update: "))

        for work_order in self.work_orders:
            if work_order.work_order_id == update_id:
                # Confirmation screen for updating
                print("Are you sure you want to update this work order?")
                confirmation = int(input("Press 1 to confirm or 2 to exit: "))

                if confirmation == 1:
                    print(f"\nUpdating Work Order ID: {update_id}"
                          "\nPress enter to keep previous information.")
                    # Prompts the user for each input, reads previous information out to user
                    # User can press enter to keep current sample information.
                    work_order.sample_id = input(
                        f"Enter new Sample ID (current: {work_order.sample_id}): ") or work_order.sample_id
                    work_order.collection_datetime = input(
                        f"Enter new Collection Date and Time (YYYY-MM-DD HH:MM) (current: {work_order.collection_datetime}): ") or work_order.collection_datetime
                    work_order.due_date = input(
                        f"Enter new Due Date (YYYY-MM-DD) (current: {work_order.due_date}): ") or work_order.due_date
                    work_order.analyses = input(
                        f"Enter new Analyses (current: {work_order.analyses}): ") or work_order.analyses
                    work_order.status = input(f"Enter new Status (current: {work_order.status}): ") or work_order.status
                    self.save_to_csv()
                    print(f"Work Order ID {update_id} has been updated.")
                else:
                    # if user inputs anything other than 1
                    print("Update Cancelled.")
                    input("\nPlease press enter to return to the Option Menu.")
                break
        # Only triggers when deletion_id isn't found
        else:
            print(f"No work order found with ID: {update_id}.")

        input("\nPlease press enter to return to the Option Menu.")

    def view_work_orders(self):
        # Screen to view all work orders, prints out all work order information
        print("Welcome to the View Work Orders Page."
              "\nHere you will find a list of all the work orders in the system.")
        for wo in self.work_orders:
            print(
                f"Work Order ID: {wo.work_order_id}, Sample ID: {wo.sample_id}, Collected: {wo.collection_datetime}, Due Date: {wo.due_date}, Analyses: {wo.analyses}, Status: {wo.status}")

        input("\nPlease press enter to return to the Option Menu.")

    def delete_work_order(self):
        # Screen for deleting a work order
        print("Welcome to the Delete Work Orders Page."
              "\nHere you can enter a work order ID number to delete the work order.")
        # User prompt for ID to delete
        deletion_id = int(input("Enter the Work Order ID to delete: "))

        for work_order in self.work_orders:
            if work_order.work_order_id == deletion_id:
                # Confirmation screen for deletion
                print("Are you sure you want to delete this work order? This action cannot be undone.")
                confirmation = int(input("Press 1 to confirm deletion or 2 to exit: "))
                if confirmation == 1:
                    self.work_orders.remove(work_order)
                    self.save_to_csv()
                    print(f"Work Order ID {deletion_id} has been deleted.")
                else:
                    # if user inputs anything other than 1
                    print("Deletion Cancelled.")
                    input("\nPlease press enter to return to the Option Menu.")
                break

        # Only triggers when deletion_id isn't found
        else:
            print(f"No work order found with ID: {deletion_id}.")

        input("\nPlease press enter to return to the Option Menu.")

    def save_to_csv(self):
        with open(self.lims_data, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["work_order_id", "sample_id", "collection_datetime", "due_date", "analyses", "status"])
            for wo in self.work_orders:
                writer.writerow(
                    [wo.work_order_id, wo.sample_id, wo.collection_datetime, wo.due_date, wo.analyses, wo.status])

    def load_from_csv(self):
        # Load data from existing csv file
        with open(self.lims_data, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                work_order = WorkOrder(
                    work_order_id=int(row["work_order_id"]),
                    sample_id=row["sample_id"],
                    collection_datetime=row["collection_datetime"],
                    due_date=row["due_date"],
                    analyses=row["analyses"],
                    status=row["status"]
                )
                self.work_orders.append(work_order)
                self.next_id = max(self.next_id, work_order.work_order_id + 1)


def main():
    while not login():
        # For invalid login cases, prompts the user to try again
        print("Invalid username and/or password"
              "\nPlease try again.")

    work_order_manager = WorkOrderManager()

    while True:
        # When login is valid
        print("\nWelcome to the Laboratory Information System!",
              "\nBelow you will find options to view all work orders, create a new work order, and logout",
              "\nYou can find information about updates here"
              "\nPlease Select an Option Below:")
        print("1. View all work orders")
        print("2. Create new work order")
        print("3. Update a work order")
        print("4. Delete a work order")
        print("5. Search for a work order")
        print("6. View in progress work orders")
        print("7. View completed work orders")
        print("8. Export a work order")
        print("9. Logout")
        option = input("Select an Option: ")

        if option == "1":
            work_order_manager.view_work_orders()
        elif option == "2":
            print("Welcome to the Create Work Orders Page."
                  "\nHere you can create a new work order with a provided sample ID, collection date and time, "
                  "due date,"
                  "and list of analyses")
            sample_id = input("Enter Sample ID: ")
            collection_datetime = input("Enter Collection Date and Time (YYYY-MM-DD HH:MM): ")
            due_date = input("Enter Due Date (YYYY-MM-DD): ")
            analyses = input("Enter Analyses to be performed: ")
            new_work_order = work_order_manager.create_work_order(sample_id, collection_datetime, due_date, analyses)
            print(f"New Work Order Created: ID {new_work_order.work_order_id}")

            input("\nPlease press enter to return to the Option Menu.")

        elif option == "3":
            work_order_manager.update_work_order()

        elif option == "4":
            work_order_manager.delete_work_order()

        elif option == "5":
            print("Welcome to the Search Work Orders Page."
                  "\nHere you can search for a work order by its ID.")
            try:
                search_id = int(input("Enter the Work Order ID to search for: "))
                response = searchMicroservice(search_id)

                if response["status"] == "found":
                    wo = response["work_order"]
                    print(
                        f"Work Order ID: {wo['work_order_id']}, Sample ID: {wo['sample_id']}, "
                        f"Collected: {wo['collection_datetime']}, Due Date: {wo['due_date']}, "
                        f"Analyses: {wo['analyses']}, Status: {wo['status']}"
                    )
                else:
                    print(response["message"])

            except ValueError:
                print("Invalid input. Please enter a valid Work Order ID.")

            input("\nPlease press enter to return to the Option Menu.")

        elif option == "6":
            print("Displaying all work orders currently in progress.")
            response = inProgressMicroservice("In Progress")

            if response["status"] == "found":
                print("Work Orders with 'In Progress' status:")

                for wo in response["work_orders"]:
                    print(f"Work Order ID: {wo['work_order_id']}, Sample ID: {wo['sample_id']}, "
                          f"Collected: {wo['collection_datetime']}, Due Date: {wo['due_date']}, "
                          f"Analyses: {wo['analyses']}, Status: {wo['status']}")

            else:
                print(response["message"])

            input("\nPlease press enter to return to the Option Menu.")

        elif option == "7":
            print("Displaying all work orders that have been Completed.")
            response = completionMicroservice("Completed")

            if response["status"] == "found":
                print("Work Orders with 'Completed' status:")
                for wo in response["work_orders"]:
                    print(
                        f"Work Order ID: {wo['work_order_id']}, Sample ID: {wo['sample_id']}, "
                        f"Collected: {wo['collection_datetime']}, Due Date: {wo['due_date']}, "
                        f"Analyses: {wo['analyses']}, Status: {wo['status']}"
                    )
            else:
                print(response["message"])

            input("\nPlease press enter to return to the Option Menu.")

        elif option == "8":
            print("Welcome to the Export Work Orders Page."
                  "\nHere you can export all information associated with a work order ID.")
            try:
                export_id = int(input("Enter the Work Order ID to Export: "))
                response = exportMicroservice(export_id)

                if response["status"] == "success":
                    print(f"Processed IDs: {response['message']}")
                else:
                    print(response["message"])

            except ValueError:
                print("Invalid input. Please enter a valid Work Order ID.")

            input("\nPlease press enter to return to the Option Menu.")

        elif option == "9":
            print("Logging out.")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
