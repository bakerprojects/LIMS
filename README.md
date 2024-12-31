Laboratory Information System (LIMS)

Overview

The Laboratory Information System (LIMS) is a command-line-based application designed to streamline laboratory workflows. It allows users to securely log in and manage work orders with full CRUD (Create, Read, Update, Delete) functionality. The system is built with modularity and scalability in mind, incorporating four distinct microservices that communicate using ZeroMQ.

Features

Secure Login: Protect user access with authentication.

Work Order Management: Create, view, update, and delete work orders.

Microservices Architecture: Four specialized microservices for:

Exporting work orders.

Searching for completed work orders.

Searching for in progress work orders.

Searching by work order ID.

ZeroMQ Communication.

System Requirements

Python 3

ZeroMQ library


Usage

Launch the main application and 4 microservices

Log in with your credentials.

Use the provided menu options to manage work orders:

Create new work orders.

View, update, or delete existing work orders.

Interact with microservices:

Export work orders.

Search for completed or in progress work orders.

Look up work orders by their unique ID
