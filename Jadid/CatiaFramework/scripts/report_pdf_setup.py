#### ----------------------------Read Me----------------------------####
"""
Structure of the PDF Report feature:
-The customCanvas class creates the document template with logo, page numeration and lines and is used for all pages
-The PDFReport class is used to create the report and its content using a set of methods described below:
    -__init__ initializes the object and is used to set basic settings of the report
    -_header_footer creates the header and footer tables and is printed on all pages
    -stacked_barchart_make creates the comparative barcharts automatically, when the data is fed in the correct format. A few attributes can bes set for formatting.
    -autoScale is used by stacked_barchart_make to automatically scale the y-axis according to the given values and a user specified number of increments
    -createReport puts the report on the custom canvas and returns ist to the print_pdf.py, where it is then presented to the user as a PDF file disposition
    -reportContent is where all the content that is used to create the report is gathered from the database and objects and then processed to show in the defined layout

Further details:
-In print_pdf.py, use boolean save_file to choose of report should be saved on server or not. !!! Will overwrite exports from the same day!!!
-The list hexColors defines the colours that are used when generating charts and diagrams as well as legends. It can be extended or modified to suit the desired style

Future features to be included:
-Finish footer feature to follow QM specification
    -As soon as Analysis Comparison can be versioned, the report should inherit the version number
    -The report author and release will be the project owner, as soon as this attribute is specified in later releases
    -The propject scope should be defined somewhere and then be included in the footer correctly
-Automatic naming of processes should be more precise and not start with "Idemat 2022", as this does not help to differentiate processes and complicates the layout of charts and diagrams

To do's:
-Check number formatting!
-Check autoscale method with negative values

"""
#### ---------------------------------------------------------------####
from PIL import Image as PILImage
#imports
from django.shortcuts import get_object_or_404
from django.db import models
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib import colors as colours
from reportlab.lib.colors import HexColor as hexcol
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import  Drawing, Rect, String
from reportlab.lib.units import inch
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend, TotalAnnotator
from django.contrib.staticfiles.storage import staticfiles_storage
import os
import datetime
import numpy as np
from django.conf import settings
#create custom canvas with page numbers, lines and logo
class CustomCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self.width, self.height = landscape(A4)

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def drawPageNumber(self, page_count):
        self.setFont('Helvetica', 10)
        self.drawRightString(self.width-2*cm, 0.75 * cm,
                             '%s/%s' % (self._pageNumber, page_count))

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.drawPageNumber(num_pages)
            self.drawLogos()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def drawLogos(self):
        self.saveState()
        self.setStrokeColorRGB(0, 0, 0)
        self.setLineWidth(1.0)
        src_path = staticfiles_storage.path('website/images/Website_Ico.png')
        self.drawImage(src_path, self.width-cm*6, self.height-3*cm, width=4*cm, height=None, preserveAspectRatio=True)
        self.line(2*cm, self.height - 4.75*cm, self.width - 2*cm, self.height - 4.75*cm)
        self.line(2*cm, 1.75*cm, self.width - 2*cm, 1.75*cm)
        self.restoreState()


#Create PDF Report on custom canvas
class PdfReport:
    def __init__(self, buffer, session_id):
        from CatiaFramework.models import Workflow_Session
        # create buffer
        self.buffer = buffer
        # store analysis ID and dictionary for loop creation from dictionary
        self.analysis_id = session_id

        # here it will be decided if report will be printed for single analysis or for analysis_comparison
        query = Workflow_Session.objects.filter(pk = self.analysis_id)
        if query:
            self.analysis = query.get()
        self.analysis_dict = self.analysis.as_dict()


        # set some characteristics for pdf document
        self.pageSize = landscape(A4)
        self.width, self.height = self.pageSize
        self.Story = []
        self.doc = SimpleDocTemplate(
            self.buffer,
            showBoundary=0,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=5*cm,
            bottomMargin=2*cm,
            height=self.height,
            width=self.width,
            pagesize=self.pageSize)

        #set colours for report
        hexColors = ['#455561','#b9254c','#d92446','#e14d47','#e86b47','#ed8648','#f29f48','#f0b872','#ead0af','#e4e5e6']
        self.coloursList = []
        for code in hexColors:
            self.coloursList.append(hexcol(code))

    def _header_footer(self, canvas, doc):

        #get analysis dict and rename locally for ease of use
        ac = self.analysis

        #create canvas
        canvas.saveState()
        styles = getSampleStyleSheet()

        #Header Title
        header_title = Paragraph('Session Report', styles['Heading1'])
        w, h = header_title.wrap(doc.width, doc.topMargin)
        header_title.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin -h)

        #Header Table
        timestamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        table_data = [['Session Name', 'Project', 'Signature Date', 'Session ID'],
                      [ ac.name,  ac.project_model.reference_project.name, timestamp,  str(ac.UUID)]]


        header_table = Table(table_data, colWidths=doc.width/len(table_data[0]))

        header_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'),('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin -2*h)

        #Footer Table
        footer_data = [['EDAG Session Report', 'Author: ' + ac.project_model.reference_project.project_manager, 'Version: 1.0',
                        'Release: ' + ac.project_model.reference_project.project_manager, 'Scope: EDAG Group',  ac.get_protection_class_display()]]
        footer_table = Table(footer_data,) #colWidths=doc.width/(len(footer_data[0])))
        footer_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'),
                                          ('FONTNAME', (0,0), (-1,0), 'Helvetica')]))
        w, h = footer_table.wrap(doc.width, doc.bottomMargin)
        footer_table.drawOn(canvas, doc.leftMargin, 1.5*h)

        #Release Canvas
        canvas.restoreState()




    def createReport(self, request):
        # build document, write to buffer and return pdf
        self.reportContent(request)
        self.doc.build(self.Story,canvasmaker=CustomCanvas, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        pdf = self.buffer.getvalue()
        self.buffer.close()
        return pdf

    def reportContent(self, request):

        #Import and creation of local objects for report
        from CatiaFramework.models import Workflow_Session
        session = self.analysis

        #import styles and add metadata
        styles = getSampleStyleSheet()
        styles.add
        styles['Heading3'].fontName = 'Helvetica-Bold' #remove Italic property from H3
        #styles['Heading4'].fontName = 'Helvetica-Bold' #remove Italic property from H4
        self.doc.title = 'Session Report'
        self.doc.author = 'Author'
        self.doc.subject = 'Session Report'

        #set colours for report
        hexColors = ['#455561','#b9254c','#d92446','#e14d47','#e86b47','#ed8648','#f29f48','#f0b872','#ead0af','#e4e5e6']
        coloursList = []
        for code in hexColors:
            coloursList.append(hexcol(code))

        ########################## Page 1 ################################

        #find picture
        picture_path = os.path.join(settings.MEDIA_ROOT, "workflow_sessions" , f"User_{str(session.owner.UUID)}" ,  f"Session_{str(session.UUID)}", "reports", "Picture_Page_1.png" )

        # Use PIL to get the size of the image
        with PILImage.open(picture_path) as img:
            original_width, original_height = img.size

        # Desired width or height in inches
        desired_width = 8 * inch
        desired_height = None

        # Maintain aspect ratio
        if desired_width and not desired_height:
            ratio = desired_width / original_width
            new_width = desired_width
            new_height = original_height * ratio
        elif desired_height and not desired_width:
            ratio = desired_height / original_height
            new_height = desired_height
            new_width = original_width * ratio

        # Add the image to the story with the calculated dimensions
        img = Image(picture_path)
        img.drawWidth = new_width
        img.drawHeight = new_height

        #Header
        self.Story.append(Paragraph('Input', styles['Heading2']))
        self.Story[-1].keepWithNext = True
        self.Story.append(img)
        # # Page Break
        self.Story.append(PageBreak())


        ########################## Page 2 ################################
        #find picture
        picture_path = os.path.join(settings.MEDIA_ROOT, "workflow_sessions" , f"User_{str(session.owner.UUID)}" ,  f"Session_{str(session.UUID)}", "reports", "Picture_Page_2.png" )

        # Use PIL to get the size of the image
        with PILImage.open(picture_path) as img:
            original_width, original_height = img.size

        # Desired width or height in inches
        desired_width = 8 * inch
        desired_height = None

        # Maintain aspect ratio
        if desired_width and not desired_height:
            ratio = desired_width / original_width
            new_width = desired_width
            new_height = original_height * ratio
        elif desired_height and not desired_width:
            ratio = desired_height / original_height
            new_height = desired_height
            new_width = original_width * ratio

        # Add the image to the story with the calculated dimensions
        img = Image(picture_path)
        img.drawWidth = new_width
        img.drawHeight = new_height

        #Header
        self.Story.append(Paragraph('Waistline Y distance - stepwise', styles['Heading2']))
        self.Story[-1].keepWithNext = True
        self.Story.append(img)
        # # Page Break
        self.Story.append(PageBreak())

        ########################## Page 3 ################################
        #find picture
        picture_path = os.path.join(settings.MEDIA_ROOT, "workflow_sessions" , f"User_{str(session.owner.UUID)}" ,  f"Session_{str(session.UUID)}", "reports", "Picture_Page_3.png" )

        # Use PIL to get the size of the image
        with PILImage.open(picture_path) as img:
            original_width, original_height = img.size

        # Desired width or height in inches
        desired_width = 8 * inch
        desired_height = None

        # Maintain aspect ratio
        if desired_width and not desired_height:
            ratio = desired_width / original_width
            new_width = desired_width
            new_height = original_height * ratio
        elif desired_height and not desired_width:
            ratio = desired_height / original_height
            new_height = desired_height
            new_width = original_width * ratio

        # Add the image to the story with the calculated dimensions
        img = Image(picture_path)
        img.drawWidth = new_width
        img.drawHeight = new_height

        #Header
        self.Story.append(Paragraph('Waistline Y distance - comprehensive', styles['Heading2']))
        self.Story[-1].keepWithNext = True
        self.Story.append(img)

        # # Page Break
        self.Story.append(PageBreak())