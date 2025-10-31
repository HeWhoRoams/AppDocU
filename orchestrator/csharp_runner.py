"""C# subprocess management and artifact collection."""

import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any
from orchestrator.logger import setup_logger

logger = setup_logger(__name__)


class CSharpExecutionError(Exception):
    """C# worker execution failed."""
    
    def __init__(self, message: str, exit_code: int = None, 
                 stdout: str = None, stderr: str = None):
        super().__init__(message)
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr


class CSharpRunner:
    """Manages execution of C# DocTool worker."""
    
    def __init__(self, config):
        self.config = config
        self._verify_tool_exists()
    
    def _verify_tool_exists(self):
        """Verify C# tool is built and available."""
        if not self.config.csharp_tool_path.exists():
            raise FileNotFoundError(
                f"C# tool not found at: {self.config.csharp_tool_path}\n"
                f"Please build the tool first: dotnet build DocTool/DocTool.csproj -c Release"
            )
    
    def analyze_files(self, files: List[Path]) -> List[Dict[str, Any]]:
        """
        Analyze multiple C# files.
        
        Args:
            files: List of C# file paths
            
        Returns:
            List of artifact dictionaries
        """
        artifacts = []
        
        for i, file_path in enumerate(files, 1):
            logger.info(f"Analyzing file {i}/{len(files)}: {file_path.name}")
            
            try:
                artifact = self._analyze_single_file(file_path)
                artifacts.append(artifact)
            except CSharpExecutionError as e:
                logger.error(f"Failed to analyze {file_path}: {e}")
                # Continue with other files
        
        return artifacts
    
    def _analyze_single_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a single C# file.
        
        Args:
            file_path: Path to C# file
            
        Returns:
            Artifact dictionary
            
        Raises:
            CSharpExecutionError: If analysis fails
        """
        output_path = self.config.artifacts_dir / f"{file_path.stem}.json"
        
        cmd = [
            str(self.config.csharp_tool_path),
            "analyze-file",
            "--file", str(file_path),
            "--output", str(output_path)
        ]
        
        logger.debug(f"Executing: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.csharp_timeout,
                check=False
            )
            
            # Log stderr (contains structured logs)
            if result.stderr:
                self._parse_and_log_stderr(result.stderr)
            
            # Check exit code
            if result.returncode != 0:
                raise CSharpExecutionError(
                    f"C# tool exited with code {result.returncode}",
                    exit_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr
                )
            
            # Parse artifact
            if output_path.exists():
                with open(output_path, 'r') as f:
                    return json.load(f)
            else:
                raise CSharpExecutionError("No artifact generated")
        
        except subprocess.TimeoutExpired:
            raise CSharpExecutionError(f"C# tool timed out after {self.config.csharp_timeout}s")
        except json.JSONDecodeError as e:
            raise CSharpExecutionError(f"Failed to parse artifact JSON: {e}")
    
    def _parse_and_log_stderr(self, stderr: str):
        """Parse structured JSON logs from stderr."""
        for line in stderr.splitlines():
            if not line.strip():
                continue
            
            try:
                log_entry = json.loads(line)
                level = log_entry.get("level", "INFO")
                message = log_entry.get("message", line)
                
                if level == "ERROR":
                    logger.error(f"[C# Worker] {message}")
                elif level == "WARN":
                    logger.warning(f"[C# Worker] {message}")
                else:
                    logger.debug(f"[C# Worker] {message}")
            except json.JSONDecodeError:
                # Not JSON, log as-is
                logger.debug(f"[C# Worker] {line}")
