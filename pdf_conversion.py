# To read the PDF
import PyPDF2
# To analyze the PDF layout and extract text
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
# To extract text from tables in PDF
import pdfplumber
# To extract the images from the PDFs
from PIL import Image
from pdf2image import convert_from_path
# To perform OCR to extract text from images
import pytesseract
# To remove the additional created files
import os

from utils import  text_extraction,crop_image,convert_to_images,image_to_text,extract_table,table_converter


# Find the PDF path
pdf_path = '/content/220929_Chinese_Academy_of_Sciences.pdf'

# create a PDF file object
pdfFileObj = open(pdf_path, 'rb')
# create a PDF reader object
pdfReader = PyPDF2.PdfReader(pdfFileObj)

text_per_page = {}
# We extract the pages from the PDF
for pagenum, page in enumerate(extract_pages(pdf_path)):

    # Initialize the variables needed for the text extraction from the page
    pageObj = pdfReader.pages[pagenum]
    page_text = []
    line_format = []
    text_from_images = []
    text_from_tables = []
    page_content = []
    # Initialize the number of the examined tables
    table_num = 0
    first_element= True
    table_extraction_flag= False
    # Open the pdf file
    pdf = pdfplumber.open(pdf_path)
    # Find the examined page
    page_tables = pdf.pages[pagenum]
    # Find the number of tables on the page
    tables = page_tables.find_tables()


    # Find all the elements
    page_elements = [(element.y1, element) for element in page._objs]
    # Sort all the elements as they appear in the page
    page_elements.sort(key=lambda a: a[0], reverse=True)

    # Find the elements that composed a page
    for i,component in enumerate(page_elements):
        # Extract the position of the top side of the element in the PDF
        pos= component[0]
        # Extract the element of the page layout
        element = component[1]

        # Check if the element is a text element
        if isinstance(element, LTTextContainer):
            # Check if the text appeared in a table
            if table_extraction_flag == False:
                # Use the function to extract the text and format for each text element
                (line_text, format_per_line) = text_extraction(element)
                # Append the text of each line to the page text
                page_text.append(line_text)
                # Append the format for each line containing text
                line_format.append(format_per_line)
                page_content.append(line_text)
            else:
                # Omit the text that appeared in a table
                pass
        # Check the elements for images
        if isinstance(element, LTFigure):
            # Crop the image from the PDF
            crop_image(element, pageObj)
            # Convert the cropped pdf to an image
            convert_to_images('cropped_image.pdf')
            # Extract the text from the image
            image_text = image_to_text('PDF_image.png')
            text_from_images.append(image_text)
            page_content.append(image_text)
            # Add a placeholder in the text and format lists
            page_text.append('image')
            line_format.append('image')
        
                # Check the elements for tables
        if isinstance(element, LTRect):
            # If the first rectangular element
            if first_element == True and (table_num+1) <= len(tables):
                # Find the bounding box of the table
                lower_side = page.bbox[3] - tables[table_num].bbox[3]
                upper_side = element.y1
                # Extract the information from the table
                table = extract_table(pdf_path, pagenum, table_num)
                # Convert the table information in structured string format
                table_string = table_converter(table)
                # Append the table string into a list
                text_from_tables.append(table_string)
                page_content.append(table_string)
                # Set the flag as True to avoid the content again
                table_extraction_flag = True
                # Make it another element
                first_element = False
                # Add a placeholder in the text and format lists
                page_text.append('table')
                line_format.append('table')

                # Check if we already extracted the tables from the page
                if element.y0 >= lower_side and element.y1 <= upper_side:
                    pass
                elif not isinstance(page_elements[i+1][1], LTRect):
                    table_extraction_flag = False
                    first_element = True
                    table_num+=1
    # Create the key of the dictionary
    dctkey = 'Page_'+str(pagenum)
    # Add the list of list as the value of the page key
    text_per_page[dctkey]= [page_text, line_format, text_from_images,text_from_tables, page_content]

# Closing the pdf file object
pdfFileObj.close()

# Deleting the additional files created
os.remove('cropped_image.pdf')
os.remove('PDF_image.png')

# Display the content of the page
result = ''.join(text_per_page['Page_0'][4])
print(result)