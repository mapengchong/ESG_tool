# ESG_tool

CODE WILL BE AVAIABALE soon on Github...

This repository contains a Python script for performing gene data analysis and similarity comparison using the `pandas`, `rapidfuzz`, and `neo4j` libraries. The script processes gene data stored in CSV files, populates a Neo4j graph database with the data, and calculates similarity scores between genes based on their characteristics.

## Prerequisites

Before running the script, make sure you have the following dependencies installed:

- Python 3.x
- pandas
- rapidfuzz
- neo4j

You can install the required packages using `pip` or `conda`.

## Getting Started

Follow these steps to run the gene data analysis pipeline:

1. Clone this repository to your local machine or download the script file.

2. Ensure that the necessary gene data CSV files (`gene_data_locus.csv` and `gene_data_GO.csv`) are present in the same directory as the script.

3. Open the script file in a text editor or IDE of your choice.

4. Customize the script according to your needs by uncommenting the desired function calls in the `main()` function.

5. Update the connection details in the `Neo4j_Connection` instantiation to match your Neo4j database configuration.

6. Save the changes to the script file.

7. Open a terminal or command prompt and navigate to the directory where the script is located.

8. Run the script by executing the command: `python script_name.py` or `python3 script_name.py`.

9. Observe the output in the terminal or check your Neo4j graph database to see the populated gene data and similarity scores.

## Script Overview

The Python script consists of the following components:

- Data preprocessing functions: These functions process the gene data CSV files, standardize gene names, and combine relevant columns.

- `Neo4j_Connection` class: This class represents a connection to a Neo4j graph database. It provides methods for initializing similarity scores between genes and retrieving the most similar genes based on a given threshold.

- `main()` function: This function serves as the entry point of the script. It creates an instance of the `Neo4j_Connection` class and calls its methods to populate the database and perform similarity scoring.


## Acknowledgments

- The `rapidfuzz` library: [https://github.com/maxbachmann/rapidfuzz](https://github.com/maxbachmann/rapidfuzz)
- The `neo4j` library: [https://neo4j.com/developer/python/](https://neo4j.com/developer/python/)

## Contributing

Contributions to this project are welcome. If you encounter any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request.


## Contact

For any inquiries or questions, please contact [pma5@unl.edu]
