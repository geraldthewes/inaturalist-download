from PIL import Image
import os
import argparse

def perform_resize_and_save(file_path, new_width, new_height):
    """
    Resize an image and save it to a temporary file before replacing the original.
    
    Args:
        file_path (str): Path to the image file.
        new_width (int): New width of the resized image.
        new_height (int): New height of the resized image.
        
    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        temp_file=None
        with Image.open(file_path) as img:
            # Resize the image
            img = img.resize((new_width, new_height), Image.LANCZOS)

            # Save as a temporary file first
            temp_file = os.path.join(os.path.dirname(file_path), f".{os.path.basename(file_path)}_temp.jpg")
            img.save(temp_file, optimize=True, quality=95)
            
            # Replace the original file with the resized image
            os.replace(temp_file, file_path)
        return True
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        # Clean up temporary file if it exists
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
        return False

def resize_image(file_path, size):
    """
    Resize a single image maintaining aspect ratio.
    
    Args:
        file_path (str): Path to the image file.
        size (int): Target size for the smallest dimension.
        
    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            # Determine the smallest dimension
            if width < height:
                smallest_dimension = width
            else:
                smallest_dimension = height
            
            # If the smallest dimension is already smaller than or equal to size, do nothing
            if smallest_dimension <= size:
                print(f"Skipping {file_path}")
                return True
            
            # Calculate new dimensions            
            if width < height:
                new_width = size
                new_height = int((height * size) / width)
            else:
                new_height = size
                new_width = int((width * size) / height)
            
            # Perform the resize and save operation
            print(f"Resize {file_path}")
            return perform_resize_and_save(file_path, new_width, new_height)
    except Exception as e:
        print(f"Error opening image {file_path}: {str(e)}")
        return False



def resize_images_in_place(input_dir, size):
    """
    Recursively resizes images in place within the specified directory.
    The smallest dimension of each image will be resized to the given size,
    maintaining aspect ratio. Images are modified directly in their original
    locations.
    
    Args:
        input_dir (str): Path to the directory containing images.
        size (int): Target size for the smallest dimension.
    """
    # Walk through all directories and files in the input directory
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            # Check if the file is an image
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                file_path = os.path.join(root, file)
                resize_image(file_path, size)

def main():
    parser = argparse.ArgumentParser(description="Recursively resize images in place within the specified directory.")
    parser.add_argument("input_directory", type=str, help="Path to the directory containing images.")
    parser.add_argument("--size", type=int, default=518, help="Target size for the smallest dimension.")

    args = parser.parse_args()

    input_dir = args.input_directory
    size = args.size

    if not os.path.isdir(input_dir):
        print(f"Error: The specified input directory '{input_dir}' does not exist.")
        sys.exit(1)
    
    if size <= 0:
        print("Size must be a positive integer.")
        sys.exit(1)

    resize_images_in_place(input_dir, size)

if __name__ == "__main__":
    import sys
    main()
