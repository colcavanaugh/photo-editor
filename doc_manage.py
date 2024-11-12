import os
import textwrap
from pathlib import Path
import json
from datetime import datetime

class DocsManager:
    def __init__(self, root_dir='.'):
        self.root_dir = Path(root_dir)
        self.docs_dir = self.root_dir / 'docs'
        self.learning_dir = self.docs_dir / 'learning'
        self.metadata_file = self.docs_dir / 'metadata.json'
        self.metadata = self.load_metadata()

    def load_metadata(self):
        """Load or create documentation metadata"""
        if self.metadata_file.exists():
            return json.loads(self.metadata_file.read_text())
        return {
            'last_updated': str(datetime.now()),
            'glossary_terms': {},
            'learning_paths': {},
            'components': {},
            'patterns': {}
        }

    def save_metadata(self):
        """Save documentation metadata"""
        self.metadata['last_updated'] = str(datetime.now())
        self.metadata_file.write_text(json.dumps(self.metadata, indent=2))

    def create_structure(self):
        """Create optimized documentation structure"""
        # Create directory structure
        dirs = [
            self.learning_dir / 'components',
            self.learning_dir / 'patterns',
            self.learning_dir / 'guides',
            self.docs_dir / 'api',
            self.docs_dir / 'architecture'
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {dir_path}")

        # Create optimized templates
        self.create_templates()
        
        # Create main README
        self.create_main_readme()
        
        # Create learning paths
        self.create_learning_paths()

        self.save_metadata()

    def create_templates(self):
        """Create optimized documentation templates"""
        templates = {
            'component': '''
            # [Component Name]

            ## Quick Start
            ```mermaid
            graph TD
                A[Purpose] --> B[Usage]
                B --> C[Integration]
            ```

            ## Core Concepts
            ### Key Terms
            - **Term**: Definition

            ### Essential Patterns
            - Pattern 1: Usage
            - Pattern 2: Usage

            ## Implementation
            ### Basic Usage
            ```python
            # Example code
            ```

            ### Integration Points
            - How to integrate
            - Common patterns
            - Best practices

            ### Advanced Usage
            - Performance considerations
            - Edge cases
            - Advanced patterns

            ## Learning Resources
            - Links to guides
            - Related patterns
            - External resources
            ''',

            'pattern': '''
            # [Pattern Name]

            ## Overview
            ```mermaid
            classDiagram
                class Pattern {
                    +purpose
                    +usage
                }
                class Implementation {
                    +examples
                    +considerations
                }
                Pattern --> Implementation
            ```

            ## Core Concepts
            - Main idea
            - When to use
            - Benefits/tradeoffs

            ## Implementation
            ### Basic Example
            ```python
            # Example code
            ```

            ### Considerations
            - Important points
            - Common pitfalls
            - Best practices

            ## Related Patterns
            - Pattern 1: Relationship
            - Pattern 2: Relationship
            '''
        }

        for name, content in templates.items():
            path = self.learning_dir / '_templates' / f'{name}_template.md'
            path.parent.mkdir(exist_ok=True)
            path.write_text(textwrap.dedent(content).strip())
            print(f"Created template: {path}")

    def create_main_readme(self):
        """Create main documentation README"""
        content = '''
        # Project Documentation

        ## Learning Resources
        ```mermaid
        mindmap
            root((Documentation))
                Components
                    Core Features
                    Integrations
                Patterns
                    Design Patterns
                    Usage Patterns
                Guides
                    Getting Started
                    Advanced Topics
        ```

        ## Quick Links
        - [Getting Started](learning/guides/getting_started.md)
        - [Core Components](learning/components/README.md)
        - [Design Patterns](learning/patterns/README.md)

        ## Development Integration
        This documentation evolves with the codebase:
        1. New features include component documentation
        2. Implementation patterns are documented as discovered
        3. Learning resources grow with development
        '''
        
        readme_path = self.docs_dir / 'README.md'
        readme_path.write_text(textwrap.dedent(content).strip())
        print(f"Created main README: {readme_path}")

    def create_learning_paths(self):
        """Create learning path documentation"""
        content = '''
        # Learning Paths

        ## Path Overview
        ```mermaid
        graph LR
            A[Basics] --> B[Components]
            B --> C[Patterns]
            C --> D[Advanced]
        ```

        ## Getting Started
        1. Core Concepts
        2. Basic Components
        3. Simple Patterns

        ## Intermediate Development
        1. Component Integration
        2. Common Patterns
        3. Testing Practices

        ## Advanced Topics
        1. Performance Optimization
        2. Advanced Patterns
        3. Architecture Design
        '''
        
        path = self.learning_dir / 'LEARNING_PATHS.md'
        path.write_text(textwrap.dedent(content).strip())
        print(f"Created learning paths: {path}")

    def update_glossary(self, term, definition, category='general'):
        """Add or update glossary term"""
        self.metadata['glossary_terms'][term] = {
            'definition': definition,
            'category': category,
            'last_updated': str(datetime.now())
        }
        self.save_metadata()

    def record_component(self, name, details):
        """Record information about a component"""
        self.metadata['components'][name] = {
            'details': details,
            'last_updated': str(datetime.now())
        }
        self.save_metadata()

def main():
    manager = DocsManager()
    manager.create_structure()
    print("\nOptimized documentation structure created!")
    print("\nNext steps:")
    print("1. Review the created structure")
    print("2. Start documenting components")
    print("3. Build learning paths")

if __name__ == '__main__':
    main()