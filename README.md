# Player Role Assignment Through Positional Tracking in the Bundesliga

This repository is a modified version of https://github.com/spoho-datascience/idsse-data which was used for the paper:
> Bassek, M., Rein, R., Weber, H., Memmert, D. (2025). An integrated dataset of
> spatiotemporal and event data in elite soccer. *Scientific Data, 12*(1),

195. https://doi.org/10.1038/s41597-025-04505-y

## Project Structure

Files created by our team:

- `group_formations.py`: Functions for grouping player positional data into the 4-2-3-1 and 3-3-2-2 formations.
- `role_extraction.ipynb`: TODO.
- `roles.py`: TODO.
- `plot_data_by_formation.ipynb`: Visualize the results using the ETH color palette.

Files from the original repository:

- `data_processing.py`: Functions for loading and processing metadata, event data, and position data.
- `visualization.py`: Functions for visualizing the processed data.
- `data_summary.ipynb`: Jupyter notebook to replicate the descriptive statistics and visualizations presented in the
  paper.

## Data Source and Characteristics

- Soccer matches from the [German Bundesliga](https://www.dfl.de/de/) (1st and 2nd divisions)
- Size: 7 full matches
    - Official metadata (match information)
    - Official event data.
    - Official position data captured by [TRACAB](https://tracab.com/products/tracab-technologies/)

## License

The data are provided with authorization of the [Deutsche Fussball Liga (DFL)](https://www.dfl.de/de/). The dataset
is licensed under [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/). You must therefore give appropriate credit
when using this dataset by

1) naming the *Deutsche Fußball Liga (DFL)*
2) citing this [publication](https://doi.org/10.1038/s41597-025-04505-y)

## Usage

1. Download the raw data [here](https://doi.org/10.6084/m9.figshare.28196177)
2. Open the `plot_data_by_formation.ipynb` notebook.
3. Run the cells to load, process, and visualize the data. Note: Running the first cells may take about 1 minute since
   it takes a bit longer to process the data.

---
