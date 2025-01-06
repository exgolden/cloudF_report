"""
Module to create the graphs for the report
"""

from datetime import datetime

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.table import Table
from path import Path

# Table
"""
Module to create the graphs for the report
"""

from datetime import datetime

import matplotlib.pyplot as plt
from path import Path


def get_timeserie(
    data: dict, output_file: str, graph_title: str, is_plain: bool, output_path: str
):
    """
    Generates a minimalistic line graph from a dictionary of dates and values.

    Args:
        data (dict): A dictionary where keys are dates (as strings in ISO format)
                     and values are numerical values.
        output_file (str): Name of the file to save the graph image.
        graph_title (str): Title for the graph.
        is_plain (bool): If True, treat values as plain numbers. If False, convert to MB.
        output_path (str): Path where the graph image should be saved.
    """
    try:
        # Sort data by date
        sorted_data = dict(
            sorted(data.items(), key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"))
        )

        # Convert keys (dates) and values to separate lists
        x_values = [datetime.strptime(date, "%Y-%m-%d") for date in sorted_data.keys()]
        y_values = list(sorted_data.values())

        # Calculate total
        if is_plain:
            total = sum(y_values)
            total_display = f"{total:,}"
        else:
            total_mb = sum(y_values) / (1024 * 1024)  # Convert bytes to MB
            total_display = f"{total_mb:,.2f} MB"

        # Create a plot
        plt.figure(
            figsize=(6.25, 1.11), facecolor="white"
        )  # 450x80 px with white background
        ax = plt.gca()
        ax.set_facecolor("white")  # Set axes background to white
        plt.plot(x_values, y_values, linestyle="-", color="blue", linewidth=2)

        # Add title with total and adjust position
        title = f"{graph_title}: {total_display}"
        plt.text(
            0.01,
            1.2,
            title,
            transform=ax.transAxes,
            fontsize=10,
            ha="left",
            va="top",
            weight="bold",
        )

        # Remove box, ticks, and labels
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
 xx      ax.set_xticks([])  # Remove x-axis ticks
        ax.set_yticks([])  # Remove y-axis ticks

        # Adjust layout to avoid collision
        plt.subplots_adjust(top=0.85)

        # Save the image
        save_path = Path(output_path) / output_file
        save_path.dirname().mkdir_p()  # Ensure the directory exists
        plt.tight_layout()
        plt.savefig(save_path, dpi=72, facecolor="white", bbox_inches="tight")
        plt.close()
        print(f"Graph saved at {save_path}")
    except ValueError as e:
        print(f"Error processing data: {e}")


# Create table
def create_table(
    requests_data: dict, bandwidth_data: dict, output_file: str, output_path: str
):
    """
    Creates a table with three columns: Country, Requests, and Bandwidth.

    Args:
        requests_data (dict): A dictionary where keys are countries and values are requests.
        bandwidth_data (dict): A dictionary where keys are countries and values are bandwidth in bytes.
        output_file (str): Name of the file to save the table image.
        output_path (str): Path where the table image should be saved.
    """
    try:
        # Merge the dictionaries and sort by requests in descending order
        combined_data = [
            (country, requests_data[country], bandwidth_data.get(country, 0))
            for country in requests_data
        ]
        combined_data.sort(key=lambda x: x[1], reverse=True)

        # Convert bandwidth to MB
        table_data = [
            (country, f"{requests:,}", f"{bandwidth / (1024 * 1024):,.2f} MB")
            for country, requests, bandwidth in combined_data
        ]

        # Create a figure
        fig, ax = plt.subplots(figsize=(6, len(table_data) * 0.5), dpi=100)
        ax.axis("off")  # Turn off the axes

        # Create a table
        table = Table(ax, bbox=[0, 0, 1, 1])

        # Add header
        headers = ["Country", "Requests", "Bandwidth"]
        for col_idx, header in enumerate(headers):
            table.add_cell(
                0,
                col_idx,
                width=0.33,
                height=0.2,
                text=header,
                loc="center",
                facecolor="lightgray",
            )

        # Add rows
        for row_idx, row in enumerate(table_data, start=1):
            for col_idx, cell in enumerate(row):
                table.add_cell(
                    row_idx, col_idx, width=0.33, height=0.2, text=cell, loc="center"
                )

        # Adjust table rows/columns
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.auto_set_column_width(col=list(range(len(headers))))

        # Add the table to the plot
        ax.add_table(table)

        # Save the image
        save_path = Path(output_path) / output_file
        save_path.dirname().mkdir_p()  # Ensure the directory exists
        plt.savefig(save_path, dpi=100, bbox_inches="tight")
        plt.close()
        print(f"Table saved at {save_path}")
    except Exception as e:
        print(f"Error creating table: {e}")


# Bar charts
def create_horizontal_bar_chart(data: dict, output_file: str, title: str):
    """
    Creates a horizontal bar chart from a dictionary.

    Args:
        data (dict): A dictionary where keys are labels (strings) and values are numerical values.
        output_file (str): Name of the file to save the chart image.
        title (str): Title for the chart.
    """
    try:
        # Ensure data is sorted in descending order by value
        sorted_data = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))

        # Labels and values
        labels = list(sorted_data.keys())
        values = list(sorted_data.values())

        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, len(labels) * 0.5), dpi=100)
        ax.barh(labels, values, color="skyblue")
        ax.invert_yaxis()  # Invert y-axis for better appearance
        ax.set_title(title, fontsize=14, weight="bold", loc="left")

        # Remove spines and ticks for a clean look
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.xaxis.set_ticks([])  # Remove x-axis values
        ax.yaxis.set_ticks_position("none")
        # Add values to the bars
        for i, v in enumerate(values):
            ax.text(v, i, f"{v:,}", va="center", ha="left", fontsize=10)

        # Save chart
        output_path = Path("./assets/network/")
        output_path.mkdir_p()  # Ensure the directory exists
        save_path = output_path / output_file
        plt.tight_layout()
        plt.savefig(save_path, bbox_inches="tight", facecolor="white")
        plt.close()
        print(f"Horizontal bar chart saved at {save_path}")
    except Exception as e:
        print(f"Error creating horizontal bar chart: {e}")


# Map
def create_request_map(data: dict, output_file: str, title: str):
    """
    Creates a map visualization of requests by country using ISO codes.

    Args:
        data (dict): A dictionary where keys are ISO country codes and values are numerical requests.
        output_file (str): Name of the file to save the map image.
        title (str): Title of the map.
    """
    try:
        shapefile_path = "./assets/countries/ne_110m_admin_0_countries.shp"
        world = gpd.read_file(shapefile_path)

        # Ensure the ISO codes match between the data and the shapefile
        if "ISO_A2" not in world.columns:
            raise KeyError("Shapefile must contain an ISO_A2 column for country codes.")

        # Add request data to the world GeoDataFrame
        world["requests"] = world["ISO_A2"].map(data).fillna(0)

        # Plot the map
        fig, ax = plt.subplots(1, 1, figsize=(8, 4))  # Smaller figure size
        world.boundary.plot(
            ax=ax, linewidth=0.5, color="black"
        )  # Add country boundaries
        map_plot = world.plot(
            column="requests",
            cmap="Blues",
            legend=True,
            ax=ax,
            legend_kwds={
                "orientation": "horizontal",  # Move color bar under the graph
                "shrink": 0.7,  # Shrink the color bar
                "pad": 0.05,  # Add padding between the plot and color bar
            },
        )

        # Remove ticks and labels
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xticklabels([])
        ax.set_yticklabels([])

        # Add title
        plt.title(title, fontsize=12, fontweight="bold", loc="left", pad=20)

        # Save the map
        plt.savefig(output_file, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Map saved as {output_file}")
    except Exception as e:
        print(f"Error creating map visualization: {e}")


# General stats
create_request_map(
    TEST_REQ_COUNT, "assets/general_stats/requests_map.png", "Requests por pais"
)
create_table(TEST_REQ_COUNT, TEST_BAND_COUNT, "table.png", "./assets/general_stats/")
get_timeserie(
    TEST_BYTES, "bandwidth.png", "Bandwidth", False, "./assets/general_stats/"
)
get_timeserie(TEST_REQ, "requests.png", "Requests", True, "./assets/general_stats/")
get_timeserie(TEST_VIEWS, "views.png", "Views", True, "./assets/general_stats/")
get_timeserie(TEST_VISITS, "visitas.png", "Visitas", True, "./assets/general_stats/")
# Security
get_timeserie(
    TEST_ENCRYPTED_REQ,
    "encrypted_requests.png",
    "Requests encriptados",
    True,
    "./assets/security/",
)
get_timeserie(
    TEST_ENCRYPTED_BAND,
    "encrypted_bandwidth.png",
    "Bandwidth encriptado",
    False,
    "./assets/security/",
)
# Cache
get_timeserie(
    TEST_CACHED_REQ,
    "cached_requests.png",
    "Requests cacheados",
    True,
    "./assets/cache/",
)
get_timeserie(
    TEST_CACHED_BAND,
    "cached_bandwidth.png",
    "Bandwidth cacheado",
    False,
    "./assets/cache/",
)
# Errors
get_timeserie(
    TEST_FOUR_ERRORS,
    "four_errors.png",
    "Errores 4xx",
    True,
    "./assets/errors/",
)
get_timeserie(
    TEST_FIVE_ERRORS,
    "five_errors.png",
    "Errores 4xx",
    True,
    "./assets/errors/",
)
# Network
create_horizontal_bar_chart(HTML_VERSIONS, "html_versions.png", "HTML versions")
create_horizontal_bar_chart(CONTENT_TYPES, "content_type", "Content by type")
create_horizontal_bar_chart(SSL_TRAFFIC, "ssl_content", "SSL Content")
