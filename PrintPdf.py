import pdfplumber
import pandas as pd

def extract_and_print_pdf_content(pdf_path):
    # open pdf with pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            # add pg no for reference
            print(f"\n--- Page {page_num + 1} ---\n")

            # extract all word from page with thier positions
            words = page.extract_words()

            # extract all tables and thier bounding boxes
            tables = page.extract_tables()
            table_bboxes = [table.bbox for table in page.find_tables()]

            # create list to store text and tables
            content = []

            # add text to list except if text inside in table
            for word in words:
                # check if work is not lying under the boundaries of tables
                if not any(is_word_in_bbox(word, bbox) for bbox in table_bboxes):
                    content.append({
                        "type": "text",
                        "text": word["text"],
                        "position": word["top"],  # for y-position
                        "x0": word["x0"]  #for x-position
                    })

            # add tables to lsit
            for i, table in enumerate(tables):
                # use pandas to create correct format for table
                df = pd.DataFrame(table)
                content.append({
                    "type": "table",
                    "table": df,
                    "position": table_bboxes[i][1],  # for y-position
                })

            # sort content list according to position of text and tables
            content.sort(key=lambda x: (x["position"], x["x0"] if "x0" in x else 0))

            # print content
            previous_position = None
            previous_x = None
            for item in content:
                if item["type"] == "text":
                    # compare y-positions to check if we need to add newline
                    if previous_position is not None and item["position"] != previous_position:
                        print("\n", end="")
                    # check if it is not first word on line and no extra space is needed
                    if previous_x is not None and abs(item["x0"] - previous_x) > 5:
                        print(" ", end="")
                    print(item["text"], end="")

                    # save x and y position for next word
                    previous_position = item["position"]
                    previous_x = item["x0"]
                elif item["type"] == "table":
                    # Add newlines before and after the table
                    print("\n\n--- Table ---\n")
                    print(item["table"].to_string(index=False, header=False))
                    print("\n")
                    previous_position = None 

def is_word_in_bbox(word, bbox):
    x0, y0, x1, y1 = bbox
    word_x0, word_y0, word_x1, word_y1 = word["x0"], word["top"], word["x1"], word["bottom"]
    # Check if the word falls within bbox of table
    return (word_x0 >= x0 and word_x1 <= x1 and word_y0 >= y0 and word_y1 <= y1)

# Path for the PDF input
pdf_path = "SamplePdfs\\a.pdf"

extract_and_print_pdf_content(pdf_path)
