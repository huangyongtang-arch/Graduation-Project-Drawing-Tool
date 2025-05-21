import re
import xml.etree.ElementTree as ET
import sys
import argparse # Added for CLI argument parsing

def parse_mermaid_flowchart(mermaid_code: str) -> tuple[list[dict], list[dict]]:
    """
    Parses basic Mermaid flowchart syntax to extract nodes and edges.

    Args:
        mermaid_code: A string containing the Mermaid flowchart definition.

    Returns:
        A tuple containing two lists:
        - The first list contains dictionaries for nodes (id, label, shape).
        - The second list contains dictionaries for edges (source, target, label).
    """
    # Initialize lists for nodes and edges
    nodes = []
    edges = []
    
    # Regular expression pattern for matching nodes
    node_pattern = re.compile(r"^\s*([\w]+)(?:\[(.*?)\]|\{(.*?)\}|\((.*?)\))?\s*(?:;)?\s*$")
    
    # Regular expression patterns for matching different types of edges
    edge_pattern = re.compile(r"^\s*([\w]+)\s*---+--\s*([\w]+)\s*$") 
    edge_with_arrow_pattern = re.compile(r"^\s*([\w]+)\s*--+>\s*([\w]+)\s*$")
    edge_with_label_pattern = re.compile(r"^\s*([\w]+)\s*--\s*(.*?)\s*--\s*([\w]+)\s*$")
    edge_with_label_and_arrow_pattern = re.compile(r"^\s*([\w]+)\s*--\s*(.*?)\s*--+>\s*([\w]+)\s*$")

    # Sets for storing node IDs and processed node definitions to avoid duplicates
    node_ids = set()
    processed_node_definitions = set()

    # Split the input Mermaid code into lines
    lines = mermaid_code.strip().split('\n')

    # Process each line to extract nodes and edges
    for line in lines:
        line = line.strip()

        # Skip lines that define the graph or flowchart orientation
        if line.lower().startswith("graph") or line.lower().startswith("flowchart"):
            continue

        # Check and process edges with labels and/or arrows
        matched_edge = False
        match = edge_with_label_and_arrow_pattern.match(line)
        if match:
            source, label, target = match.groups()
            edges.append({'source': source, 'target': target, 'label': label.strip()})
            node_ids.add(source)
            node_ids.add(target)
            matched_edge = True
        else:
            match = edge_with_label_pattern.match(line)
            if match:
                source, label, target = match.groups()
                edges.append({'source': source, 'target': target, 'label': label.strip()})
                node_ids.add(source)
                node_ids.add(target)
                matched_edge = True
            else:
                match = edge_with_arrow_pattern.match(line)
                if match:
                    source, target = match.groups()
                    edges.append({'source': source, 'target': target, 'label': ''})
                    node_ids.add(source)
                    node_ids.add(target)
                    matched_edge = True
                else:
                    match = edge_pattern.match(line)
                    if match:
                        source, target = match.groups()
                        edges.append({'source': source, 'target': target, 'label': ''})
                        node_ids.add(source)
                        node_ids.add(target)
                        matched_edge = True

        # Continue to the next line if an edge has been processed
        if matched_edge:
            continue

        # Process nodes with different shapes
        match = node_pattern.match(line)
        if match:
            node_id, rect_label, rhomb_label, stadium_label = match.groups()
            
            # Skip processing if the node has already been defined
            if node_id in processed_node_definitions:
                continue

            label = node_id 
            shape = 'default' 

            # Determine the shape of the node based on the label format
            if rect_label is not None:
                label = rect_label.strip()
                shape = 'rectangle'
            elif rhomb_label is not None:
                label = rhomb_label.strip()
                shape = 'rhombus'
            elif stadium_label is not None:
                label = stadium_label.strip()
                shape = 'stadium'
            
            # Update or add the node information
            existing_node = next((n for n in nodes if n['id'] == node_id), None)
            if existing_node:
                existing_node['label'] = label
                existing_node['shape'] = shape
            else:
                nodes.append({'id': node_id, 'label': label, 'shape': shape})
            
            processed_node_definitions.add(node_id)
            node_ids.add(node_id)

    # Add default nodes for any node IDs mentioned in edges but not defined as nodes
    for node_id_in_edge in node_ids:
        if not any(n['id'] == node_id_in_edge for n in nodes):
            nodes.append({'id': node_id_in_edge, 'label': node_id_in_edge, 'shape': 'default'})
            
    # Return the extracted nodes and edges
    return nodes, edges

def generate_drawio_xml(nodes: list[dict], edges: list[dict]) -> str:
    """
    Generates Draw.io XML from parsed nodes and edges.

    Args:
        nodes: A list of node dictionaries ({'id', 'label', 'shape'}).
        edges: A list of edge dictionaries ({'source', 'target', 'label'}).

    Returns:
        A string containing the Draw.io XML.
    """
    # Create the root element of the Draw.io XML
    mxfile = ET.Element("mxfile", compressed="false", host="app.diagrams.net")
    
    # Create the diagram element
    diagram = ET.SubElement(mxfile, "diagram", id="Diagram1", name="Page-1")
    
    # Create the mxGraphModel element with default settings
    mx_graph_model = ET.SubElement(diagram, "mxGraphModel", dx="1000", dy="800", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="850", pageHeight="1100", math="0", shadow="0")
    
    # Create the root element for cells (nodes and edges)
    root = ET.SubElement(mx_graph_model, "root")
    
    # Create the first two default mxCell elements
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    # Dictionary to store the mapping of node IDs to XML IDs
    xml_node_ids = {} 
    # Counter for generating unique cell IDs
    cell_id_counter = 2 

    # Initial position and spacing for nodes
    node_x_position = 50
    node_y_position = 50 
    node_spacing_x = 150 
    node_width = 120
    node_height = 60

    # Iterate through nodes to create node elements
    for i, node in enumerate(nodes):
        xml_id = str(cell_id_counter)
        xml_node_ids[node['id']] = xml_id
        cell_id_counter += 1

        style = ""
        # Determine the style based on the node shape
        if node['shape'] == 'rectangle':
            style = "rounded=0;whiteSpace=wrap;html=1;"
        elif node['shape'] == 'rhombus':
            style = "shape=rhombus;whiteSpace=wrap;html=1;"
        elif node['shape'] == 'stadium': 
            style = "shape=ellipse;perimeter=ellipsePerimeter;whiteSpace=wrap;html=1;"
        elif node['shape'] == 'default': 
            style = "rounded=0;whiteSpace=wrap;html=1;"
        else: 
            style = "rounded=0;whiteSpace=wrap;html=1;"

        # Create the node cell element
        node_cell = ET.SubElement(root, "mxCell", 
                                  id=xml_id, 
                                  value=node['label'], 
                                  style=style, 
                                  parent="1", 
                                  vertex="1")
        
        # Calculate the position of the node
        current_x = str(node_x_position + (i * node_spacing_x))
        current_y = str(node_y_position)

        # Create the mxGeometry element for the node
        ET.SubElement(node_cell, "mxGeometry", attrib={ # 将属性明确放入 attrib 字典
            "x": current_x,
            "y": current_y,
            "width": str(node_width),
            "height": str(node_height),
            "as": "geometry"
        })

    # Iterate through edges to create edge elements
    for edge in edges:
        edge_xml_id = str(cell_id_counter)
        cell_id_counter += 1

        source_xml_id = xml_node_ids.get(edge['source'])
        target_xml_id = xml_node_ids.get(edge['target'])

        # Check if the source and target XML IDs exist
        if source_xml_id is None or target_xml_id is None:
            print(f"Warning: Could not find XML ID for source/target of edge: {edge}", file=sys.stderr)
            continue 

        edge_style = "endArrow=classic;html=1;rounded=0;"
        
        # Create the edge cell element
        edge_cell = ET.SubElement(root, "mxCell",
                                  id=edge_xml_id,
                                  value=edge['label'], 
                                  style=edge_style,
                                  parent="1",
                                  edge="1",
                                  source=source_xml_id,
                                  target=target_xml_id)
        
        # Create the mxGeometry element for the edge
        ET.SubElement(edge_cell, "mxGeometry", attrib={"relative": "1", "as": "geometry"}) # 将属性明确放入 attrib 字典

    # Convert the ElementTree to an XML string
    xml_string = ET.tostring(mxfile, encoding="unicode")
    
    # Return the generated XML string
    return xml_string

def convert_mermaid_to_drawio_xml(mermaid_code: str) -> str:
    """
    Orchestrates the conversion of Mermaid flowchart code to Draw.io XML.

    Args:
        mermaid_code: A string containing the Mermaid flowchart definition.

    Returns:
        A string containing the Draw.io XML.
    """
    nodes, edges = parse_mermaid_flowchart(mermaid_code)
    xml_output = generate_drawio_xml(nodes, edges)
    return xml_output

def save_drawio_xml_to_file(xml_content: str, output_filepath: str) -> None:
    """
    Saves the Draw.io XML content to a specified file.

    Args:
        xml_content: The Draw.io XML string.
        output_filepath: The path to the file where the XML should be saved.
    """
    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)
    except IOError as e:
        print(f"Error saving file to {output_filepath}: {e}", file=sys.stderr)
        # Optionally, re-raise the exception or exit if this is critical
        # sys.exit(1) 

def main():
    """
    Main function to handle CLI arguments and orchestrate the conversion process.
    """
    parser = argparse.ArgumentParser(description="Convert Mermaid flowchart code to Draw.io XML.")
    
    # Mutually exclusive group for input
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("-if", "--input_file", 
                             help="Path to an input file containing Mermaid code.")
    input_group.add_argument("-is", "--input_string", 
                             help="Mermaid code directly as a string.")
    
    # Required output file argument
    parser.add_argument("-o", "--output_file", 
                        required=True, 
                        help="Path for the output .drawio file.")
    
    args = parser.parse_args()
    
    mermaid_content = ""
    
    # Determine Mermaid Input
    if args.input_file:
        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                mermaid_content = f.read()
        except FileNotFoundError:
            print(f"Error: Input file not found at {args.input_file}", file=sys.stderr)
            sys.exit(1)
        except IOError as e:
            print(f"Error reading input file {args.input_file}: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.input_string:
        mermaid_content = args.input_string
    # No need for an else here because the input_group is required, 
    # argparse will handle if neither is provided.

    if not mermaid_content.strip():
        print("Error: Mermaid input is empty.", file=sys.stderr)
        sys.exit(1)

    # Call convert_mermaid_to_drawio_xml()
    drawio_xml = convert_mermaid_to_drawio_xml(mermaid_content)
    
    # Call save_drawio_xml_to_file()
    save_drawio_xml_to_file(drawio_xml, args.output_file)
    
    print(f"Successfully converted Mermaid input to Draw.io XML and saved to {args.output_file}")

if __name__ == '__main__':
    main()
    # Previous test code (commented out or removed):
    # sample_mermaid_code = """
    # graph TD
    #     A[Client] --> B{Load Balancer};
    #     B --> C[Server 1];
    #     B --> D[Server 2];
    #     C --> E((Database));
    #     D --> E;
    #     F[Monitoring] --> C;
    #     F --> D;
    # """
    # print("--- Converting Mermaid to Draw.io XML ---")
    # drawio_output_xml = convert_mermaid_to_drawio_xml(sample_mermaid_code)
    # output_filename = "output.drawio"
    # save_drawio_xml_to_file(drawio_output_xml, output_filename)
    # print(f"\nDraw.io XML saved to {output_filename}")
