# photo_editor/processing/image_operations.py
import cv2
import numpy as np
from sklearn.cluster import KMeans
from skimage.segmentation import slic
from skimage.color import label2rgb
from scipy import ndimage
from dataclasses import dataclass
from PySide6.QtGui import QImage

@dataclass
class SegmentationParams:
    """Parameters for controlling the segmentation process"""
    n_segments: int = 100          # Number of initial superpixels
    n_colors: int = 8             # Number of colors in final output
    compactness: float = 10.0     # Balance between color and spatial proximity
    sigma: float = 3.0            # Width of gaussian smoothing kernel
    edge_weight: float = 1.0      # Weight of edge preservation (0-1)
    color_space: str = 'lab'      # Color space to use ('lab', 'rgb', 'hsv')
    smoothing_factor: float = 0.5  # Amount of final smoothing to apply (0-1)
    edge_enhancement: float = 0.5  # Strength of edge enhancement (0-1)

class ImageProcessor:
    def __init__(self):
        self.current_image = None
        self.edited_image = None
        
    def load_image(self, file_path):
        self.current_image = cv2.imread(file_path)
        if self.current_image is not None:
            self.edited_image = self.current_image.copy()
            
    def has_image(self):
        return self.current_image is not None
        
    def get_qt_image(self, cv_img):
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        return QImage(rgb_img.data, w, h, ch * w, QImage.Format.Format_RGB888)
        
    def apply_grayscale(self):
        if self.edited_image is not None:
            self.edited_image = cv2.cvtColor(
                self.edited_image, cv2.COLOR_BGR2GRAY)
            self.edited_image = cv2.cvtColor(
                self.edited_image, cv2.COLOR_GRAY2BGR)
            
    def kmeans_clustering(self, image, n_clusters):
        """Apply K-means clustering to the image."""
        # Reshape the image to 2D array of pixels
        height, width, channels = image.shape
        pixels = image.reshape(-1, channels)
        pixels = np.float32(pixels)
        
        # Apply k-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(pixels)
        
        # Get the quantized colors
        centers = kmeans.cluster_centers_
        
        # Map each pixel to its closest center
        quantized = centers[labels]
        
        # Normalize to 0-255 range
        quantized = ((quantized - quantized.min()) / 
                    (quantized.max() - quantized.min()) * 255).astype(np.uint8)
        
        # Reshape back to original image dimensions
        return quantized.reshape(height, width, channels)
            
    def apply_kmeans(self, k):
        """Apply k-means clustering to the image with progress updates."""
        if self.edited_image is not None:
            # Apply kmeans clustering
            self.edited_image = self.kmeans_clustering(self.edited_image, k)
            
# photo_editor/processing/image_operations.py
def smooth_segmentation(self, image, params: SegmentationParams):
    """
    Enhanced segmentation with controllable parameters.
    """
    # Convert to specified color space
    if params.color_space == 'lab':
        working_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    elif params.color_space == 'hsv':
        working_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    else:
        working_image = image.copy()

    # Apply initial Gaussian smoothing
    if params.sigma > 0:
        working_image = cv2.GaussianBlur(
            working_image, 
            (0, 0), 
            params.sigma
        )

    # Generate superpixels
    segments = slic(
        working_image,
        n_segments=params.n_segments,
        compactness=params.compactness,
        sigma=params.sigma,
        start_label=0
    )

    # Calculate mean color for each superpixel
    result = np.zeros_like(image)
    for segment_id in range(segments.max() + 1):
        mask = segments == segment_id
        mean_color = image[mask].mean(axis=0)
        result[mask] = mean_color

    # Convert pixels to a list of tuples for k-means
    pixels = result.reshape(-1, 3)
    
    # Apply K-means to the unique colors
    kmeans = KMeans(
        n_clusters=params.n_colors,
        random_state=42,
        n_init=10
    )
    kmeans.fit(pixels)
    
    # Create the quantized image directly
    quantized = kmeans.cluster_centers_[kmeans.labels_]
    final_result = quantized.reshape(image.shape)

    # Edge preservation and enhancement
    if params.edge_weight > 0:
        edges = cv2.Canny(
            cv2.cvtColor(image, cv2.COLOR_BGR2GRAY),
            100,
            200
        )
        edges = cv2.dilate(edges, None)
        edge_mask = edges > 0
        
        # Preserve original edges
        final_result[edge_mask] = image[edge_mask] * params.edge_weight + \
                                final_result[edge_mask] * (1 - params.edge_weight)

    # Final smoothing with edge preservation
    if params.smoothing_factor > 0:
        final_result = cv2.edgePreservingFilter(
            final_result.astype(np.uint8),
            flags=cv2.RECURS_FILTER,
            sigma_s=int(60 * params.smoothing_factor),
            sigma_r=0.4
        )

    # Edge enhancement
    if params.edge_enhancement > 0:
        sharpened = cv2.addWeighted(
            final_result, 1 + params.edge_enhancement,
            cv2.GaussianBlur(final_result, (0, 0), 3),
            -params.edge_enhancement, 0
        )
        final_result = np.clip(sharpened, 0, 255).astype(np.uint8)

    return final_result

def apply_smooth_segmentation(self, params: SegmentationParams = None):
    """Apply smooth segmentation with given parameters."""
    if params is None:
        params = SegmentationParams()
        
    if self.edited_image is not None:
        self.edited_image = self.smooth_segmentation(
            self.edited_image, 
            params
        )

def save_image(self, file_path):
    if self.edited_image is not None:
        cv2.imwrite(file_path, self.edited_image)