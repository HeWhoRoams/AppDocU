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
from appdocu_preprocessor.converters.base_converter import BaseConverter, ConversionResult


class VisioToJsonConverter(BaseConverter):
    def __init__(self):
        super().__init__("visio_to_json", "visio")
    
    def convert(self, file_path: Path, output_dir: Path) -> Dict[str, Any]:
        """
        Convert Visio file to JSON and Mermaid format
        
        Args:
            file_path: Path to the input Visio file
            output_dir: Directory where output should be written
        
        Returns:
            Dictionary with conversion result
        """
        try:
            # Validate input file
            if not self.validate_input_file(file_path):
                return ConversionResult("visio_to_json").set_failed("Invalid input file").build()
            
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
                
                # Write JSON file using base converter functionality
                json_content = json.dumps(json_data, indent=2, ensure_ascii=False)
                json_output_file = self.write_output_file(output_dir, file_path, json_content, ".json")
                
                # Generate Mermaid flowchart
                mermaid_content = self.generate_mermaid_flowchart(all_shapes, all_connectors)
                
                # Write Mermaid file using base converter functionality
                mermaid_output_file = self.write_output_file(output_dir, file_path, mermaid_content, ".mmd")
            
            # Create result with metadata
            result = ConversionResult("visio_to_json")
            result.set_success(str(json_output_file.relative_to(output_dir.parent)))
            result.add_metadata('pages', len(pages_data))
            result.add_metadata('shapes', len(all_shapes))
            result.add_metadata('connectors', len(all_connectors))
            result.add_metadata('edges', len(all_connectors))
            result.add_metadata('file_info', self.get_file_info(file_path))
            
            conversion_result = result.build()
            self.log_conversion_result(file_path, conversion_result)
            return conversion_result
            
        except Exception as e:
            error_result = self.handle_conversion_error(file_path, e)
            return error_result
    
    def generate_mermaid_flowchart(self, shapes: List[Dict], connectors: List[Dict]) -> str:
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
            from_clean = self.clean_mermaid_label(from_name)
            to_clean = self.clean_mermaid_label(to_name)
            
            # Add edge with optional label
            if connector['text']:
                label = self.clean_mermaid_label(connector['text'])
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
            clean_name = self.clean_mermaid_label(shape['name'] or shape['text'] or f"Shape_{shape['id']}")
            mermaid_lines.append(f"  {clean_name}")
        
        return "\n".join(mermaid_lines)
    
    def clean_mermaid_label(self, label: str) -> str:
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


def convert(file_path: Path, output_dir: Path) -> Dict[str, Any]:
    """Wrapper function for backward compatibility"""
    converter = VisioToJsonConverter()
    return converter.convert(file_path, output_dir)
