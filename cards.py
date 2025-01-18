from pdf2image import convert_from_path
import numpy as np
import cv2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import sys
import os

# Group horizontal and vertical lines
def group_lines(lines):
    horizontal_lines = []
    vertical_lines = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(y1 - y2) < 10:  # Horizontal line
                horizontal_lines.append((x1, y1, x2, y2))
            elif abs(x1 - x2) < 10:  # Vertical line
                vertical_lines.append((x1, y1, x2, y2))
    return (horizontal_lines, vertical_lines)

# Find intersections
def find_intersections(horizontal_lines, vertical_lines):
    intersections = []
    for h_line in horizontal_lines:
        for v_line in vertical_lines:
            intersect = line_intersection(h_line, v_line)
            if intersect:
                intersections.append(intersect)
    return intersections

def line_intersection(line1, line2):
    x1, y1, x2, y2 = map(float, line1)  # Ensure float arithmetic
    x3, y3, x4, y4 = map(float, line2)

    # Compute determinant
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-10:  # Parallel or nearly parallel lines
        return None

    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom

    return int(px), int(py)  # Convert to integer for pixel coordinates

# Group intersections into rectangles
def find_bounding_boxes(intersections):
    bounding_boxes = []
    for i, pt1 in enumerate(intersections):
        for j, pt2 in enumerate(intersections):
            if i != j:
                x_min = min(pt1[0], pt2[0])
                y_min = min(pt1[1], pt2[1])
                x_max = max(pt1[0], pt2[0])
                y_max = max(pt1[1], pt2[1])

                # Ensure valid size and aspect ratio
                width = x_max - x_min
                height = y_max - y_min
                if 300 < width < 10000 and 400 < height < 10000:  # Adjust size range
                    bounding_boxes.append((x_min, y_min, x_max, y_max))
    return bounding_boxes

# Get outermost bounding box
def get_outermost_bounding_box(bounding_boxes):
    outer_x_min, outer_y_min, outer_x_max, outer_y_max = (None, None, None, None)
    for box in bounding_boxes:
        x_min, y_min, x_max, y_max = box
        if outer_x_min is None or x_min < outer_x_min:
            outer_x_min = x_min
        if outer_x_max is None or x_max > outer_x_max:
            outer_x_max = x_max
        if outer_y_min is None or y_min < outer_y_min:
            outer_y_min = y_min
        if outer_y_max is None or y_max > outer_y_max:
            outer_y_max = y_max
    return (outer_x_min, outer_y_min, outer_x_max, outer_y_max)

def convert_to_pdf(page_images, output_path):
    # Define PDF page size for 8.5 x 11 inches
    page_width, page_height = letter  # 8.5 x 11 inches in points (612 x 792)

    # Create the PDF
    c = canvas.Canvas(output_path, pagesize=letter)

    # Insets so they don't get cutoff when printing too close to the edge
    HORIZONTAL_PADDING = 15
    VERTICAL_PADDING = 10

    image_width = page_width - 2 * HORIZONTAL_PADDING
    image_height = page_height - 2 * VERTICAL_PADDING

    for i,image in enumerate(page_images):
        # Create a temporary image file resized for the PDF
        temp_file = f"temp_image_{i}.png"
        cv2.imwrite(temp_file, image)

        # Draw the image onto the PDF
        c.drawImage(temp_file, HORIZONTAL_PADDING, VERTICAL_PADDING, width=image_width, height=image_height)
        os.remove(temp_file)
        c.showPage()

    # Save the PDF
    c.save()

def convert_pdf(from_file, to_file):
    images_of_pdf = convert_from_path(from_file)  # Convert PDF to List of PIL Images
    cropped_images = []

    for pil_image in images_of_pdf:
        img = np.array(pil_image)

        imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        imgEdges = cv2.Canny(imgGray,100,250)
        lines = cv2.HoughLinesP(imgEdges,10,np.pi/180,10, minLineLength = 475, maxLineGap = 15)

        # Draw lines on the original image
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]  # Extract the line coordinates
                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Draw the line in green color with thickness 2

        # Display the image with lines
        cv2.imshow('Lines on Image', img)
        cv2.waitKey(3000)  # Wait for a key press
        # cv2.destroyAllWindows()  # Close all OpenCV windows

        horizontal_lines, vertical_lines = group_lines(lines)
        intersections = find_intersections(horizontal_lines, vertical_lines)
        bounding_boxes = find_bounding_boxes(intersections)
        outer_x_min, outer_y_min, outer_x_max, outer_y_max = get_outermost_bounding_box(bounding_boxes)
            
        # Display image with bounding box
        if outer_x_min is None or outer_x_max is None or outer_y_min is None or outer_y_max is  None:
            return False

        # Outset the bounding box a little so we get the dotted lines
        OUTSET = 3
        outer_x_min -= OUTSET
        outer_x_max += OUTSET
        outer_y_min -= OUTSET
        outer_y_max += OUTSET

        cropped_image = img[outer_y_min:outer_y_max, outer_x_min:outer_x_max]
        cropped_images.append(cropped_image)

        # cv2.imshow('Final Image with dotted Lines detected',cropped_image) 
        # cv2.waitKey(3000)
    
    cards = []
    CARD_HEIGHT = 634
    CARD_WIDTH = 974

    for image in cropped_images:
        height, width = image.shape[:2]
        height_in_cards = round(height / CARD_HEIGHT)
        height_of_card = height / height_in_cards

        for card_idx in range(height_in_cards):
            TOP_FUDGE = 0 if card_idx == 0 else 2
            BOTTOM_FUDGE = 0 if card_idx == (height_in_cards - 1) else 4
            start_y = card_idx * height_of_card - TOP_FUDGE
            end_y = start_y + height_of_card + TOP_FUDGE + BOTTOM_FUDGE
            card = image[int(start_y):int(end_y), 0:width]

            card = cv2.resize(card, (CARD_WIDTH, CARD_HEIGHT))

            cards.append(card)

    NUM_ROWS = 4
    NUM_COLS = 2
    PER_PAGE = NUM_COLS * NUM_ROWS

    # Fill in empty spots with white cards
    last_page_filled_count = len(cards) % (PER_PAGE)
    last_page_needed_count = PER_PAGE - last_page_filled_count
    for i in range(last_page_needed_count):
        cards.append(np.ones((CARD_HEIGHT, CARD_WIDTH, 3), dtype=np.uint8) * 255)

    pages = []
    for page in range(len(cards) // PER_PAGE):
        i = page * PER_PAGE
        cols = []
        for c in range(NUM_COLS):
            col = []
            for r in range(NUM_ROWS):
                col.append(cards[i + (c * NUM_ROWS) + r])
            cols.append(cv2.vconcat(col))
        
        page_image = cv2.hconcat(cols)
        pages.append(page_image)

    convert_to_pdf(pages, to_file)
    return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python cards.py <input_filepath> <output_filepath>")
        exit()

    success = convert_pdf(sys.argv[1], sys.argv[2])
    if success:
       print("Succeeded")
    else:
       print("Failed")