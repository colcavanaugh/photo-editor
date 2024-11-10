# Photo Editor

A desktop application for image editing and processing built with Python and PySide6.

## Photo Editor Application Architecture
```mermaid
graph TD
    A[run.py] -->|imports & runs| B[main.py]
    B -->|creates| C[PhotoEditorWindow]
    C -->|contains| D[FileNavigator]
    C -->|contains| E[ImageViewer]
    C -->|contains| F[ToolPanel]
    E -->|uses| G[ImageProcessor]
    G -->|performs| H[Image Operations]
    
    subgraph "Core Components"
        C
        D -->|emits signals| E
        E -->|displays| I[ImageViewerContainer]
        I -->|contains| J[Original Image]
        I -->|contains| K[Edited Image]
        F -->|triggers| E
    end
    
    subgraph "Image Processing"
        H -->|operations| L[Grayscale]
        H -->|operations| M[K-means Clustering]
        H -->|operations| N[Smart Segmentation]
    end

    style A fill:#f9f,stroke:#333
    style B fill:#f9f,stroke:#333
    style C fill:#bbf,stroke:#333
    style G fill:#bfb,stroke:#333
```

## Main Components
- `FileNavigator`: Browse and select image files
- `ImageViewer`: Display and compare original/edited images
- `ToolPanel`: Access editing operations
- `ImageProcessor`: Handle image processing operations

## Features
- File navigation and management
- Basic image processing operations (grayscale, k-means clustering)
- Advanced segmentation with customizable parameters
- Drag-and-drop interface for image comparison
- Support for multiple image formats

## Requirements
- Python 3.x
- PySide6
- OpenCV (cv2)
- scikit-learn
- scikit-image
- scipy
- numpy

## Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python run.py`

## Development Roadmap

1. **Phase 1: Core Foundation**
   - Basic window setup
   - Simple image loading and display
   - One basic image operation (e.g., grayscale)
   - Unit tests for core functionality

2. **Phase 2: Image Processing**
   - Implement processing operations one by one
   - Add parameter controls
   - Test each operation thoroughly

3. **Phase 3: UI Enhancement**
   - Add file navigation
   - Implement comparison view
   - Add drag-and-drop functionality
   - Test UI interactions
