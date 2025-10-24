"""
Visio to JSON + Mermaid Converter
Converts Visio diagrams to JSON data and Mermaid flowcharts
"""
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple
import json
from vsdx import VisioFile


def convert(file_path: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Convert Visio file to JSON and Mermaid format
    
    Args:
        file_path: Path to the input Visio file
        output_dir: Directory where output should be written
    
    Returns:
        Dictionary with conversion result
    """
    try:
        # Create visio output directory if it doesn't exist
        visio_dir = output_dir / "visio"
        visio_dir.mkdir(exist_ok=True)
        
        # Open the Visio file
        with VisioFile(str(file_path)) as vis:
            pages_data = []
            all_connectors = []
            all_shapes = []
            
            # Process each page
            for page in vis.pages:
                page_data = {
                    'name': page.name,
                    'shapes': [],
                    'connectors': []
                }
                
                shapes = []
                connectors = []
                
                # Get all shapes on the page
                for shape in page.shapes:
                    shape_data = {
                        'id': shape.ID,
                        'name': shape.name,
                        'text': shape.text if hasattr(shape, 'text') else '',
                        'type': shape.shape_name if hasattr(shape, 'shape_name') else 'unknown',
                        'properties': {}
                    }
                    
                    # Extract shape properties if available
                    if hasattr(shape, 'shape_properties'):
                        for prop in shape.shape_properties:
                            shape_data['properties'][prop.name] = prop.value
                    
                    # Extract coordinates if available
                    if hasattr(shape, 'x') and hasattr(shape, 'y'):
                        shape_data['coordinates'] = {
                            'x': float(shape.x) if shape.x else 0,
                            'y': float(shape.y) if shape.y else 0
                        }
                    
                    shapes.append(shape_data)
                    all_shapes.append(shape_data)
                
                # Get all connectors on the page
                for connector in page.connectors:
                    connector_data = {
                        'id': connector.ID,
                        'name': connector.name,
                        'from_shape': connector.from_id,
                        'to_shape': connector.to_id,
                        'text': connector.text if hasattr(connector, 'text') else '',
                        'properties': {}
                    }
                    
                    # Extract connector properties if available
                    if hasattr(connector, 'shape_properties'):
                        for prop in connector.shape_properties:
                            connector_data['properties'][prop.name] = prop.value
                    
                    connectors.append(connector_data)
                    all_connectors.append(connector_data)
                
                page_data['shapes'] = shapes
                page_data['connectors'] = connectors
                pages_data.append(page_data)
            
            # Create JSON output
            json_data = {
                'source_file': str(file_path.name),
                'converted_at': datetime.now(timezone.utc).isoformat(),
                'pages': pages_data,
                'all_shapes': all_shapes,
                'all_connectors': all_connectors,
                'total_shapes': len(all_shapes),
                'total_connectors': len(all_connectors)
            }
            
            # Write JSON file
            json_filename = file_path.stem + ".json"
            json_output_file = visio_dir / json_filename
            
            with open(json_output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            # Generate Mermaid flowchart
            mermaid_content = generate_mermaid_flowchart(all_shapes, all_connectors)
            
            # Write Mermaid file
            mermaid_filename = file_path.stem + ".mmd"
            mermaid_output_file = visio_dir / mermaid_filename
            
            with open(mermaid_output_file, 'w', encoding='utf-8') as f:
                f.write(mermaid_content)
        
        return {
            'status': 'success',
            'output': str(json_output_file.relative_to(output_dir.parent)),
            'converter': 'visio_to_json',
            'metadata': {
                'pages': len(pages_data),
                'shapes': len(all_shapes),
                'connectors': len(all_connectors),
                'edges': len(all_connectors)
            }
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e),
            'converter': 'visio_to_json'
        }


def generate_mermaid_flowchart(shapes: List[Dict], connectors: List[Dict]) -> str:
    """
    Generate Mermaid flowchart from shapes and connectors
    """
    # Create a mapping of shape ID to shape name for easier reference
    shape_map = {shape['id']: shape['name'] or shape['text'] or f"Shape_{shape['id']}" 
                 for shape in shapes}
    
    # Start building the Mermaid diagram
    mermaid_lines = ["graph LR"]
    
    # Add all connectors as edges
    for connector in connectors:
        from_id = connector['from_shape']
        to_id = connector['to_shape']
        from_name = shape_map.get(from_id, f"Shape_{from_id}")
        to_name = shape_map.get(to_id, f"Shape_{to_id}")
        
        # Clean up names for Mermaid (remove special characters, spaces, etc.)
        from_clean = clean_mermaid_label(from_name)
        to_clean = clean_mermaid_label(to_name)
        
        # Add edge with optional label
        if connector['text']:
            label = clean_mermaid_label(connector['text'])
            mermaid_lines.append(f"  {from_clean} -->|{label}| {to_clean}")
        else:
            mermaid_lines.append(f"  {from_clean} --> {to_clean}")
    
    # Add any shapes that aren't connected to anything
    connected_ids = set()
    for conn in connectors:
        connected_ids.add(conn['from_shape'])
        connected_ids.add(conn['to_shape'])
    
    unconnected_shapes = [shape for shape in shapes if shape['id'] not in connected_ids]
    for shape in unconnected_shapes:
        clean_name = clean_mermaid_label(shape['name'] or shape['text'] or f"Shape_{shape['id']}")
        mermaid_lines.append(f"  {clean_name}")
    
    return "\n".join(mermaid_lines)


def clean_mermaid_label(label: str) -> str:
    """
    Clean up a label for use in Mermaid diagrams
    """
    if not label:
        return "Empty"
    
    # Remove special characters and replace with underscores
    import re
    cleaned = re.sub(r'[^\w\s-]', '_', label)
    # Replace spaces with underscores
    cleaned = re.sub(r'\s+', '_', cleaned)
    # Remove multiple underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    # Remove leading/trailing underscores
    cleaned = cleaned.strip('_')
    
    # If the result is empty or just numbers, create a generic name
    if not cleaned or cleaned.isdigit():
        return f"Node_{hash(label) % 10000}"
    
    # Limit length to avoid Mermaid issues
    if len(cleaned) > 50:
        cleaned = cleaned[:50]
    
    return cleaned
