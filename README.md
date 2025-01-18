# TempleCards
Nicer formatting for LDS temple cards that makes cutting them out easier.

## What it does
Converts a PDF from FamilySearch into a PDF with the same cards in a more compact format. This new format shrinks the cards slightly but uses less paper and requires less trimming with scissors, since there is no border that must be cut out.
| Before             |  After |
:-------------------------:|:-------------------------:
<img width="316" alt="Screenshot 2025-01-18 at 2 18 15 PM" src="https://github.com/user-attachments/assets/b8095370-2afb-4bfd-b5dd-ba2b9338b741" /> | <img width="633" alt="Screenshot 2025-01-18 at 2 19 50 PM" src="https://github.com/user-attachments/assets/2f316adf-7a45-4083-8eec-b10645e69363" />


## How it works
* Use computer vision to find the dotted lines.
* Use that to figure out where each card is.
* Crop cards from original PDF.
* Rearrange cards into new layout and fill in blank spaces.
* Fit onto multiple sheets of 8.5 x 11 paper inside a new PDF.

## Deploying
* Copy contents of code files into corresponding files on PythonAnywhere.
* Reload website
* Find it hosted [here](https://ephraimkunz.pythonanywhere.com)

<img width="1840" alt="Screenshot 2025-01-18 at 2 23 00 PM" src="https://github.com/user-attachments/assets/6ac04a96-66d4-43bb-a94a-a060da6c7af9" />

