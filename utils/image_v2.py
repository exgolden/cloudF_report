"""
 V2 functions neccesary to run the image creation API
"""

from datetime import datetime
from path import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.table import table
from geopandas.array import transform

def line_graph(data: dict, output_path: str, data_type: str = "numeric") -> None:
    """
    Generates a minimalistic line graph from a directory of dates and values:
    Args:
         data (dict): A dictionary where keyas are dates and values are numeric.
         output_path (str): Path where the graph image is saved.
         data_type (str): The type of data ("numeric" or "bytes"). Defaults to "numeric".
    """
    #TODO Add logging and improve errors
    fig_horizontal_size = 7
    fig_vertical_size = 1.5
    fig_top_space = 0.85
    fig_title_horizontal = 0.01
    fig_title_vertical = 1.2
    fig_title_fontsize = 10
    graph_line_color = "#4693ff"
    graph_area_alpha = 0.2
    try:
        sort_d = sorted(data.items(), key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"))
        x_values = mdates.date2num([datetime.strptime(date, "%Y-%m-%d") for date, _ in sort_d])
        y_values = [value for _, value in sort_d]
        total_display = sum(y_values)
        if data_type == "bytes":
            total_display = f"{total_display / (1024 * 1024):,.2f} MB"
        else:
            if total_display >= 1_000_000:
                total_display = f"{total_display / 1_000_000:.2f}M"
            elif total_display >= 1_000:
                total_display = f"{total_display / 1_000:.2f}k"
            else:
                total_display = str(total_display)
        plt.figure(
            figsize=(fig_horizontal_size, fig_vertical_size),
        )
        ax = plt.gca()
        plt.plot(x_values, y_values, linestyle="-", color=graph_line_color)
        plt.fill_between(x_values, y_values, color=graph_line_color, alpha=graph_area_alpha)
        graph_title = Path(output_path).stem
        plt.text(
            fig_title_horizontal,
            fig_title_vertical,
            f"{graph_title}: {total_display}",
            transform=ax.transAxes,
            fontsize=fig_title_fontsize,
            ha="left",
            va="top",
            weight="bold"
        )
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
        plt.subplots_adjust(top=fig_top_space)
        save_path = Path(output_path).with_suffix(".png")
        plt.savefig(save_path, dpi=100, bbox_inches="tight", transparent=True)
        plt.close()
        print("graph generated")
    except Exception as e:
        print(f"Error generating graph: {e}")
        raise 











