# Mermaid to Draw.io Converter

## Description
This Python script converts basic Mermaid flowchart syntax into a Draw.io (diagrams.net) XML file format. This allows you to quickly generate editable diagrams from simple text-based Mermaid definitions.

## Requirements & Installation
*   **Python:** This is a Python script. Python 3.x is recommended.
*   **Standard Libraries Only:** The script currently uses only standard Python libraries (`re`, `xml.etree.ElementTree`, `sys`, `argparse`). No external dependencies need to be installed via `pip` or `requirements.txt` at this time.

To use the script, simply download `mermaid_to_drawio.py` or clone this repository.

## Usage
The script is run from the command line and offers options for providing the Mermaid input and specifying the output file.

### Command-Line Arguments

*   **Input (choose one):**
    *   `-if FILE_PATH`, `--input_file FILE_PATH`:
        Path to an input file containing the Mermaid flowchart code.
    *   `-is STRING`, `--input_string STRING`:
        Mermaid flowchart code provided directly as a string.
    *   *Note: Either `--input_file` or `--input_string` must be provided.*

*   **Output (required):**
    *   `-o FILE_PATH`, `--output_file FILE_PATH`:
        Path to save the generated `.drawio` file.

### Examples

1.  **Using an input file:**
    ```bash
    python mermaid_to_drawio.py --input_file path/to/your/diagram.mermaid --output_file path/to/your/diagram.drawio
    ```
    (Replace `path/to/your/diagram.mermaid` with the actual path to your Mermaid file and `path/to/your/diagram.drawio` with your desired output path.)

2.  **Using a direct string input:**
    ```bash
    python mermaid_to_drawio.py --input_string "graph TD; A[Start] --> B{Decision}; B -- Yes --> C(Process);" --output_file my_flowchart.drawio
    ```

## Supported Mermaid Syntax
The converter currently supports a basic subset of Mermaid flowchart syntax:

*   **Diagram Type Declaration:**
    *   `graph TD`, `graph LR`, `flowchart TD`, etc. (Note: The directionality `TD`, `LR` is parsed but not yet fully implemented in the layout of the Draw.io XML, which defaults to a simple horizontal arrangement).
*   **Nodes:**
    *   Simple node: `nodeId` (label defaults to `nodeId`, shape is rectangle/default)
    *   Node with rectangular shape (default): `nodeId[Label text]`
    *   Node with stadium/roundrect shape: `nodeId(Label text)`
    *   Node with rhombus/diamond shape: `nodeId{Label text}`
*   **Edges:**
    *   Arrow link: `id1 --> id2`
    *   Line link: `id1 --- id2`
    *   Arrow link with text: `id1 -- Link Text --> id2`
    *   Line link with text: `id1 --- Link Text --- id2`

The parser is designed for basic flowcharts. More complex Mermaid features, subgraphs, or advanced styling may not be supported.

## Output
The script generates an XML file with a `.drawio` extension. This file can be opened and edited using Draw.io (app.diagrams.net) or any compatible editor. The generated diagram will contain the nodes and edges defined in your Mermaid input, with a simple automatic layout.

## License
This project is licensed under the **MIT License**. See the `LICENSE` file for more details.
