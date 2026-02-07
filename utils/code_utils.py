"""
Code Processing Module for GyanGuru
Handles code analysis, dependency detection, and file management
"""

import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Set


class CodeProcessor:
    """Handles code processing, dependency detection, and file management"""
    
    # Common ML/Data Science packages
    KNOWN_PACKAGES = {
        'numpy': 'numpy',
        'np': 'numpy',
        'pandas': 'pandas',
        'pd': 'pandas',
        'matplotlib': 'matplotlib',
        'plt': 'matplotlib',
        'seaborn': 'seaborn',
        'sns': 'seaborn',
        'sklearn': 'scikit-learn',
        'tensorflow': 'tensorflow',
        'tf': 'tensorflow',
        'keras': 'keras',
        'torch': 'torch',
        'cv2': 'opencv-python',
        'PIL': 'Pillow',
        'scipy': 'scipy',
        'xgboost': 'xgboost',
        'lightgbm': 'lightgbm',
        'nltk': 'nltk',
        'spacy': 'spacy',
        'transformers': 'transformers',
        'datasets': 'datasets',
        'tqdm': 'tqdm',
        'requests': 'requests',
        'bs4': 'beautifulsoup4',
        'networkx': 'networkx',
    }
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize code processor
        
        Args:
            output_dir: Directory to save code files
        """
        self.output_dir = output_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'static', 'generated', 'code'
        )
        os.makedirs(self.output_dir, exist_ok=True)
    
    def detect_dependencies(self, code: str) -> Dict[str, Any]:
        """
        Parse Python code to detect required dependencies
        
        Args:
            code: Python source code
        
        Returns:
            Dictionary with imports and pip packages
        """
        imports: Set[str] = set()
        pip_packages: Set[str] = set()
        
        # Pattern for import statements
        import_patterns = [
            r'^import\s+(\w+)',  # import module
            r'^from\s+(\w+)',    # from module import ...
        ]
        
        for line in code.split('\n'):
            line = line.strip()
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    module = match.group(1)
                    imports.add(module)
                    
                    # Map to pip package name
                    if module in self.KNOWN_PACKAGES:
                        pip_packages.add(self.KNOWN_PACKAGES[module])
                    elif not self._is_stdlib(module):
                        pip_packages.add(module)
        
        return {
            "imports": sorted(list(imports)),
            "pip_packages": sorted(list(pip_packages)),
            "install_command": f"pip install {' '.join(sorted(pip_packages))}" if pip_packages else None
        }
    
    def _is_stdlib(self, module: str) -> bool:
        """Check if module is part of Python standard library"""
        stdlib_modules = {
            'os', 'sys', 'math', 'random', 'time', 'datetime', 'json',
            'collections', 'itertools', 'functools', 'typing', 're',
            'copy', 'pickle', 'csv', 'io', 'string', 'textwrap',
            'struct', 'codecs', 'unicodedata', 'warnings', 'logging',
            'abc', 'contextlib', 'pathlib', 'tempfile', 'shutil',
            'argparse', 'configparser', 'hashlib', 'secrets',
            'threading', 'multiprocessing', 'queue', 'asyncio',
            'unittest', 'doctest', 'pdb', 'timeit', 'statistics',
            'dataclasses', 'enum', 'numbers', 'decimal', 'fractions'
        }
        return module in stdlib_modules
    
    def format_code_response(
        self,
        code: str,
        topic: str,
        complexity: str
    ) -> Dict[str, Any]:
        """
        Format code with metadata and setup instructions
        
        Args:
            code: Generated Python code
            topic: The ML topic
            complexity: Code complexity level
        
        Returns:
            Formatted response with code and metadata
        """
        dependencies = self.detect_dependencies(code)
        
        # Generate Colab setup instructions
        colab_setup = self._generate_colab_setup(dependencies['pip_packages'])
        
        # Generate local setup instructions
        local_setup = self._generate_local_setup(dependencies['pip_packages'])
        
        return {
            "code": code,
            "topic": topic,
            "complexity": complexity,
            "dependencies": dependencies,
            "colab_setup": colab_setup,
            "local_setup": local_setup,
            "line_count": len(code.split('\n'))
        }
    
    def _generate_colab_setup(self, packages: List[str]) -> str:
        """Generate Google Colab setup instructions"""
        if not packages:
            return "# No additional packages required - ready to run!"
        
        # Filter out packages that are pre-installed in Colab
        colab_preinstalled = {'numpy', 'pandas', 'matplotlib', 'seaborn', 
                              'scikit-learn', 'tensorflow', 'keras'}
        
        packages_to_install = [p for p in packages if p not in colab_preinstalled]
        
        if not packages_to_install:
            return "# All required packages are pre-installed in Google Colab!"
        
        return f"""# Run this cell first to install required packages
!pip install {' '.join(packages_to_install)}

# Then run the main code below"""
    
    def _generate_local_setup(self, packages: List[str]) -> str:
        """Generate local environment setup instructions"""
        if not packages:
            return "No additional packages required."
        
        return f"""## Local Setup Instructions

1. Create a virtual environment (recommended):
   ```bash
   python -m venv ml_env
   source ml_env/bin/activate  # On Windows: ml_env\\Scripts\\activate
   ```

2. Install required packages:
   ```bash
   pip install {' '.join(packages)}
   ```

3. Run the code:
   ```bash
   python your_script.py
   ```"""
    
    def save_code_file(
        self,
        code: str,
        topic: str,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Save generated code to a file
        
        Args:
            code: Python code to save
            topic: The ML topic (used for filename)
            filename: Optional custom filename
        
        Returns:
            Dictionary with file path info
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_topic = "".join(c if c.isalnum() else "_" for c in topic[:30])
                filename = f"{safe_topic}_{timestamp}.py"
            
            if not filename.endswith('.py'):
                filename = f"{filename}.py"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # Add header comment to code
            header = f'''"""
Generated by GyanGuru - AI ML Learning Assistant
Topic: {topic}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

'''
            
            with open(filepath, 'w') as f:
                f.write(header + code)
            
            return {
                "success": True,
                "filepath": filepath,
                "filename": filename,
                "relative_path": f"/static/generated/code/{filename}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "filepath": None
            }
    
    def get_available_code_files(self) -> list:
        """Get list of available code files"""
        files = []
        if os.path.exists(self.output_dir):
            for f in os.listdir(self.output_dir):
                if f.endswith('.py'):
                    filepath = os.path.join(self.output_dir, f)
                    files.append({
                        "filename": f,
                        "path": filepath,
                        "relative_path": f"/static/generated/code/{f}",
                        "size": os.path.getsize(filepath)
                    })
        return files
