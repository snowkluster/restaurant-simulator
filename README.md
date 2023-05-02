 
                                                                                         
░██████╗██╗███╗░░░███╗██╗░░░██╗██╗░░░░░░█████╗░████████╗░█████╗░██████╗░                  
██╔════╝██║████╗░████║██║░░░██║██║░░░░░██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗                     
╚█████╗░██║██╔████╔██║██║░░░██║██║░░░░░███████║░░░██║░░░██║░░██║██████╔╝                      
░╚═══██╗██║██║╚██╔╝██║██║░░░██║██║░░░░░██╔══██║░░░██║░░░██║░░██║██╔══██╗                     
██████╔╝██║██║░╚═╝░██║╚██████╔╝███████╗██║░░██║░░░██║░░░╚█████╔╝██║░░██║                     
╚═════╝░╚═╝╚═╝░░░░░╚═╝░╚═════╝░╚══════╝╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░╚═╝░░╚═╝                       
                                                                                                 
                                                                                                     
# Overview
- This application emulates the real-time processing of food orders received by a single kitchen. Each order may contain several items, and the kitchen has a fixed number of cooks, each capable of preparing one item at a time. If all cooks are occupied, the items are placed in a queue and processed in order as soon as a cook becomes available. The number of cooks and simulator speed can be adjusted according to requirements.

- All the data required for the simulation is stored in the `simulator/data` directory. However, the system is designed to operate as if orders are received in real-time. Therefore, no component of the system can access future orders from the `orders.json file`.

- While the simulator is running, it saves order information to a `local SQLite database`, which is shared with a Flask app running on a separate thread. The Flask app presents a data dashboard that provides real-time insights into operational and business metrics.


# Run the Simulation Locally
## Requirements
To ensure optimal performance, it is recommended that you install Docker and the docker-compose CLI on your machine. Additionally, increasing the Docker Desktop resources beyond their default levels can provide even better results.

*it is recommended to have at least 8GB of ram on your machine*

## How to Run
- From the root directory, run the following:
```bash
docker-compose up --build
```
- Open a web browser to by clicking the link that the dash app generates
- (Optional) Change the parameters in [parameters/simulation_parameters.py](./parameters/simulation_parameters.py) and re-run steps 1 and 2 to see how the simulation changes

# App Architecture
The application consists of two separate processes, namely the order simulator and an analytics dashboard web app. These two processes communicate with each other using a shared SQLite database where the order simulator writes to the database while the dashboard reads from it. This approach separates the concerns of each process and enables them to run independently with their own operating systems, file systems, and hardware resources. Therefore, one process can be scaled without affecting the other as long as they both communicate through the shared database. The processes are networked through a basic docker-compose file, which also mounts a parameters file to each process. This file makes it easy to define all system parameters in one location for convenience.

## Order Simulator
The [SimPy framework](https://simpy.readthedocs.io/en/latest/) is used in the order simulator to create a simulation of real-time order processing with a limited number of resources, such as cooks. The simulation is defined using generator functions that pass orders to a kitchen object, which has a predetermined number of resources. Orders are divided into individual items, and the generator functions keep track of the order's status until completion. Each item has a predetermined cook time, and items are queued in sequence if resources are unavailable.

The SQLite database is updated three times for each order: when the order is received, when the first item is cooked, and when the last item is cooked. This approach allows for real-time tracking of order statuses while also enabling historical analysis of completed orders since each timestamp is stored independently.

## Dashboard
The [Dash framework](https://plotly.com/dash/) is used to create an interactive dashboard within a Flask application. It is an open-source library that is built on top of React and D3, making it highly flexible and extensible. The dashboard can be easily customized by adding new visualizations, filters, and other features. The data for the dashboard is obtained by running a set of pre-defined analytical SQL queries, with each query corresponding to a specific chart on the dashboard. The query results are then loaded into a Pandas dataframe, which allows for further transformations and integration with the Dash API. The data is refreshed every 5 seconds by default.
