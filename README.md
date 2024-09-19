## INSTALLATION

first, you need to install Python 3.12.2 and Tesseract-OCR.

Then, open the extract.py file and modify the 7th line to points to your Tesseract-OCR executable. 

```
    pytesseract.pytesseract.tesseract_cmd = "path/to/your/tesseract.exe"
```

/!\  In order to not slowing down the app, Tesseract should be located in the C:/, not in U:/   /!\

then, open the terminal (cmd) at the root of the project and execute the following command lines : 

this one bellow is **optional**, to activate a virtual environment
```
    python -m venv env 
    .\env\Scripts\activate
```

Install the necessary packages 

```
    pip install -r .\requirements.txt
```

Once, all the packages installed, you can start the project by entering 
```
    python api.py
```

The project is now running ! Go to http://localhost:5000/ or click here [Start web app](http://127.0.0.1:5000/) to explore the web app !


## Introduction 

This solution is an information pdf extractor that can be applied on various type of PDF. The mechanism is simple : 

- Click on the "Drawing on templates" section
- Enter a *sample PDF*
- Specify the areas you want to extract information from (the name of the drawn areas will be the names of result data frame columns)
- Enter the *"test"* PDFs, all the files you want the information about
- Download the results files 

All the files created and uploaded including *sample PDF*, *test PDFs*, *drawing.json* (file containing the region of interest) and results files in csv/json are saved and stored in ./uploads/by_drawing/**sess_id**/ where **sess_id** corresponds to the session ID (an incremental number)


If you already have the config file containing the ROI to extract, you can go on "Choosing a configuration" section and enter the sample file and the config file, as well as the corresponding *test PDFs* from which you want extract information. The sample file should be selected carefully as it will serve as an example for aligning others *test* files.


During the drawing part, it is possible to get a larger representation of the PDF page to be more accurate when specifying/drawing the region of interest by clicking on **More options** and increasing the DPI. In the same section, you can enter a JSON file as a configuration file to visualize or edit it to create a new one.
There is also an option "1 to N pages" to specify whether the information to be extracted is the same on all pages of a PDF or not. If so, you must indicate what is the number of the page, of the drawing you made, which contains the bounding box to extract on each page for each test PDF (default page 1).

