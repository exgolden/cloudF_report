"""
V2 functions neccesary to run the graph creation
"""

__version__ = "2.0.0"
# TODO Normalize graph sizes

from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from geopandas import gpd
from matplotlib.table import Table
from matplotlib.transforms import Bbox
from path import Path


def graph_line(data: dict, output_path: str, data_type: str = "numeric") -> None:
    """
    Generates a minimalistic line graph from a directory of dates and int values:
    Args:
         data (dict): A dictionary where keyas are dates and values are numeric.
         output_path (str): Path where the graph image is saved.
         data_type (str): The type of data ("numeric" or "bytes"). Defaults to "numeric".
    """
    # TODO Add logging and improve errors
    fig_horizontal_size = 7
    fig_vertical_size = 1.5
    fig_top_space = 0.85
    fig_title_horizontal = 0.01
    fig_title_vertical = 1.2
    fig_title_fontsize = 10
    fig_facecolor = "white"
    graph_line_color = "#4693ff"
    graph_area_alpha = 0.2
    try:
        sort_d = sorted(data.items(), key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"))
        x_values = mdates.date2num(
            [datetime.strptime(date, "%Y-%m-%d") for date, _ in sort_d]
        )
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
            figsize=(fig_horizontal_size, fig_vertical_size), facecolor=fig_facecolor
        )
        plt.plot(x_values, y_values, linestyle="-", color=graph_line_color)
        plt.fill_between(
            x_values, y_values, color=graph_line_color, alpha=graph_area_alpha
        )
        graph_title = Path(output_path).stem
        ax = plt.gca()
        plt.text(
            fig_title_horizontal,
            fig_title_vertical,
            f"{graph_title}: {total_display}",
            transform=ax.transAxes,
            fontsize=fig_title_fontsize,
            ha="left",
            va="top",
            weight="bold",
        )
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
        plt.subplots_adjust(top=fig_top_space)
        save_path = Path(output_path).with_suffix(".png")
        plt.savefig(save_path, dpi=100, bbox_inches="tight")
        plt.close()
        print("graph generated")
    except Exception as e:
        print(f"Error generating graph: {e}")
        raise


def graph_bar(data: dict, output_path: str) -> None:
    """
    Generates a minimalistic bar graph from a directory of str and int values:
    Args:
        data (dict): A dictionary where keyas are dates and values are numeric.
        output_path (str): Path where the graph image is saved.
    """
    # TODO Add logging and improve errors
    fig_horizontal_size = 2.5
    fig_vertical_size = 2
    fig_top_space = 0.85
    fig_title_horizontal = -0.46
    fig_title_vertical = 1.2
    fig_title_fontsize = 10
    fig_fontsize = 8
    fig_facecolor = "white"
    graph_y_padding = 65
    graph_number_padding = 0.01
    graph_bar_height = 0.5
    graph_fill_color = "#0051c3"
    graph_box_color = "#dadad9"
    try:
        sort_d = sorted(data.items(), key=lambda x: x[1])
        x_values = [key for key, _ in sort_d]
        y_values = [value for _, value in sort_d]
        max_value = max(y_values)
        plt.figure(
            figsize=(fig_horizontal_size, fig_vertical_size), facecolor=fig_facecolor
        )
        ax = plt.gca()
        graph_title = Path(output_path).stem
        plt.text(
            fig_title_horizontal,
            fig_title_vertical,
            graph_title,
            transform=ax.transAxes,
            fontsize=fig_title_fontsize,
            ha="left",
            va="top",
            weight="bold",
        )
        ax.barh(
            x_values,
            [max_value] * len(y_values),
            color=graph_box_color,
            height=graph_bar_height,
        )
        ax.barh(
            x_values,
            y_values,
            color=graph_fill_color,
            height=graph_bar_height,
        )
        for i, (_, v) in enumerate(sort_d):
            ax.text(
                max_value + graph_number_padding * max_value,
                i,
                f"{v:,}",
                va="center",
                ha="left",
                fontsize=fig_fontsize,
            )
        ax.set_yticks(range(len(x_values)))
        ax.set_yticklabels(x_values, ha="left")
        ax.tick_params(axis="y", pad=graph_y_padding)
        ax.tick_params(axis="y", length=0)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.set_xticks([])
        plt.subplots_adjust(top=fig_top_space)
        save_path = Path(output_path).with_suffix(".png")
        plt.savefig(save_path, dpi=100, bbox_inches="tight")
        plt.close()
        print("graph generated")
    except Exception as e:
        print(f"Error generating graph: {e}")
        raise e


def graph_map(data: dict, output_path: str) -> None:
    """
    Generates a minimalistic bar graph from a directory of str and int values:
    Args:
        data (dict): A dict where keys are ISO country codes and values are numeric.
        output_path (str): Path where the graph image is saved.
    """
    # TODO Change the path for the countries using os
    fig_definition = 150
    fig_horizontal_size = 6
    fig_vertical_size = 3
    fig_facecolor = "white"
    # fig_legend_shrink = 0.18
    # fig_legend_padding = 0
    fig_boundary_linewidth = 0.1
    fig_boundary_color = "black"
    # fig_colorbar_fontsize = 10
    try:
        shapefile_path = "./assets/countries/ne_110m_admin_0_countries.shp"
        world = gpd.read_file(shapefile_path)
        if "ISO_A2" not in world.columns:
            raise KeyError("Shapefile must contain an ISO_A2 column for ctry codes.")
        world["requests"] = world["ISO_A2"].map(data).fillna(0)
        plt.figure(
            figsize=(fig_horizontal_size, fig_vertical_size), facecolor=fig_facecolor
        )
        ax = plt.gca()
        ax.set_aspect("auto")
        world.plot(
            column="requests",
            cmap="Blues",
            # legend=True,
            ax=ax,
            # legend_kwds = {
            #     "orientation": "vertical",
            #     "shrink": fig_legend_shrink,
            #     "pad": fig_legend_padding,
            #     "fontsize": fig_colorbar_fontsize
            # }
        )
        world.boundary.plot(
            ax=ax, linewidth=fig_boundary_linewidth, color=fig_boundary_color
        )
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        save_path = Path(output_path).with_suffix(".png")
        plt.savefig(save_path, dpi=fig_definition, bbox_inches="tight")
        plt.close()
        print("graph generated")
    except Exception as e:
        print(f"Error generating graph: {e}")
        raise e


def create_table(requests_data: dict, bandwidth_data: dict, output_path: str) -> None:
    """
    Generates a table image showing Country, Requests, and Bandwidth.
    Args:
        requests_data (dict): Countries as keys and requests as values.
        bandwidth_data (dict): Countries as keys and bandwidth in bytes as values.
        output_path (str): Path (including filename) to save the table image.
    """
    fig_width, fig_dpi = 6, 100
    cell_width, cell_height = 0.33, 0.2
    header_color, font_size = "lightgray", 10
    try:
        combined_data = [
            (country, requests_data[country], bandwidth_data.get(country, 0))
            for country in requests_data
        ]
        combined_data.sort(key=lambda x: x[1], reverse=True)
        table_rows = [
            (country, f"{requests:,}", f"{bandwidth / (1024 * 1024):,.2f} MB")
            for country, requests, bandwidth in combined_data
        ]
        fig, ax = plt.subplots(figsize=(fig_width, len(table_rows) * 0.5), dpi=fig_dpi)
        ax.axis("off")
        table = Table(ax, bbox=Bbox.from_extents(0, 0, 1, 1))
        headers = ["Country", "Requests", "Bandwidth"]
        for col_idx, header in enumerate(headers):
            table.add_cell(
                0,
                col_idx,
                width=cell_width,
                height=cell_height,
                text=header,
                loc="center",
                facecolor=header_color,
            )
        for row_idx, row in enumerate(table_rows, start=1):
            for col_idx, cell in enumerate(row):
                table.add_cell(
                    row_idx,
                    col_idx,
                    width=cell_width,
                    height=cell_height,
                    text=cell,
                    loc="center",
                )
        table.auto_set_font_size(False)
        table.set_fontsize(font_size)
        table.auto_set_column_width(col=list(range(len(headers))))
        ax.add_table(table)
        save_path = Path(output_path).with_suffix(".png")
        plt.savefig(save_path, bbox_inches="tight")
        plt.close()
        print(f"Table saved at {save_path}")
    except Exception as e:
        print(f"Error creating table: {e}")
        raise e


# from test_data import *

# graph_map(
#         TEST_REQ_COUNT,
#         "assets/general_stats/requests_map"
#         )
# graph_line(
#         TEST_ENCRYPTED_BAND,
#         "./assets/security/encrypted_requests",
#         data_type="bytes"
#         )
# graph_line(
#         TEST_CACHED_REQ,
#         "assets/cache/cached_requests",
#         )
# graph_line(
#         TEST_REQ,
#         "assets/general_stats/requests",
#         )
# graph_line(
#         TEST_VIEWS,
#         "assets/general_stats/views",
#         )
# graph_line(
#         TEST_VISITS,
#         "assets/general_stats/visitas",
#         )
# graph_line(
#         TEST_CACHED_BAND,
#         "assets/cache/cached_bandwidth",
#         data_type="bytes"
#         )
# graph_line(
#         TEST_BYTES,
#         "assets/general_stats/bandwidth",
#         data_type="bytes"
#         )
# graph_line(
#         TEST_ENCRYPTED_BAND,
#         "assets/security/encrypted_bandwidth",
#         data_type="bytes"
#         )
# graph_line(
#         TEST_FOUR_ERRORS,
#         "assets/errors/four_errors"
#         )
# graph_line(
#         TEST_FIVE_ERRORS,
#         "assets/errors/five_errors"
#         )
# graph_bar(
#         HTML_VERSIONS,
#         "assets/network/html_versions"
#         )
# graph_bar(
#         CONTENT_TYPES,
#         "assets/network/content_type"
#         )
# graph_bar(
#         SSL_TRAFFIC,
#         "assets/network/ssl_content"
#         )
