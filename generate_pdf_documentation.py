#!/usr/bin/env python3
"""
MediSync PDF Documentation Generator
Converts the markdown documentation to a professional PDF format
"""

import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.colors import HexColor, black, white, blue, green, red
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import re
from datetime import datetime

class MediSyncPDFGenerator:
    def __init__(self, markdown_file, output_file):
        self.markdown_file = markdown_file
        self.output_file = output_file
        self.doc = SimpleDocTemplate(
            output_file,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        self.setup_custom_styles()

    def setup_custom_styles(self):
        """Setup custom styles for the PDF"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#2E86AB'),
            fontName='Helvetica-Bold'
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=HexColor('#A23B72'),
            fontName='Helvetica'
        ))

        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=HexColor('#2E86AB'),
            fontName='Helvetica-Bold'
        ))

        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=HexColor('#F18F01'),
            fontName='Helvetica-Bold'
        ))

        # Code style
        self.styles.add(ParagraphStyle(
            name='CodeStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Courier',
            backgroundColor=HexColor('#F5F5F5'),
            borderColor=HexColor('#CCCCCC'),
            borderWidth=1,
            leftIndent=20,
            rightIndent=20,
            spaceAfter=10,
            spaceBefore=10
        ))

        # Bullet point style
        self.styles.add(ParagraphStyle(
            name='BulletStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=20,
            bulletIndent=10,
            spaceAfter=6
        ))

    def parse_markdown_content(self):
        """Parse the markdown file and convert to PDF elements"""
        with open(self.markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split content into sections
        sections = content.split('\n## ')
        
        # Process title
        title_section = sections[0]
        title_lines = title_section.split('\n')
        main_title = title_lines[0].replace('# ', '')
        subtitle = title_lines[1] if len(title_lines) > 1 else ""

        # Add title page
        self.add_title_page(main_title, subtitle)

        # Process each section
        for i, section in enumerate(sections[1:], 1):
            self.process_section(section)
            if i < len(sections) - 1:
                self.story.append(PageBreak())

    def add_title_page(self, title, subtitle):
        """Add a professional title page"""
        self.story.append(Spacer(1, 2*inch))
        
        # Main title
        title_para = Paragraph(title, self.styles['CustomTitle'])
        self.story.append(title_para)
        self.story.append(Spacer(1, 0.5*inch))
        
        # Subtitle
        if subtitle:
            subtitle_para = Paragraph(subtitle, self.styles['CustomSubtitle'])
            self.story.append(subtitle_para)
            self.story.append(Spacer(1, 1*inch))

        # Add system info box
        system_info = """
        <b>System:</b> MediSync Healthcare Management Platform<br/>
        <b>Version:</b> 1.0<br/>
        <b>Documentation Type:</b> System Process & AI Analytics Guide<br/>
        <b>Generated:</b> """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
        """
        
        info_style = ParagraphStyle(
            name='InfoBox',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            backgroundColor=HexColor('#F0F8FF'),
            borderColor=HexColor('#2E86AB'),
            borderWidth=2,
            leftIndent=50,
            rightIndent=50,
            spaceAfter=20,
            spaceBefore=20
        )
        
        info_para = Paragraph(system_info, info_style)
        self.story.append(info_para)
        self.story.append(PageBreak())

    def process_section(self, section_content):
        """Process a section of the markdown content"""
        lines = section_content.split('\n')
        section_title = lines[0]
        
        # Add section header
        section_para = Paragraph(section_title, self.styles['SectionHeader'])
        self.story.append(section_para)
        
        current_content = []
        in_code_block = False
        code_content = []
        
        for line in lines[1:]:
            line = line.strip()
            
            if line.startswith('```'):
                if in_code_block:
                    # End code block
                    code_text = '\n'.join(code_content)
                    code_para = Paragraph(f'<pre>{code_text}</pre>', self.styles['CodeStyle'])
                    self.story.append(code_para)
                    code_content = []
                    in_code_block = False
                else:
                    # Start code block
                    if current_content:
                        self.process_text_content('\n'.join(current_content))
                        current_content = []
                    in_code_block = True
                continue
            
            if in_code_block:
                code_content.append(line)
                continue
            
            if line.startswith('### '):
                # Process accumulated content
                if current_content:
                    self.process_text_content('\n'.join(current_content))
                    current_content = []
                
                # Add subsection header
                subsection_title = line.replace('### ', '')
                subsection_para = Paragraph(subsection_title, self.styles['SubsectionHeader'])
                self.story.append(subsection_para)
            
            elif line.startswith('#### '):
                # Process accumulated content
                if current_content:
                    self.process_text_content('\n'.join(current_content))
                    current_content = []
                
                # Add sub-subsection header
                subsubsection_title = line.replace('#### ', '')
                subsubsection_style = ParagraphStyle(
                    name='SubSubsectionHeader',
                    parent=self.styles['Normal'],
                    fontSize=12,
                    fontName='Helvetica-Bold',
                    spaceAfter=8,
                    spaceBefore=12,
                    textColor=HexColor('#666666')
                )
                subsubsection_para = Paragraph(subsubsection_title, subsubsection_style)
                self.story.append(subsubsection_para)
            
            else:
                current_content.append(line)
        
        # Process remaining content
        if current_content:
            self.process_text_content('\n'.join(current_content))

    def process_text_content(self, content):
        """Process text content and convert to PDF elements"""
        if not content.strip():
            return
        
        paragraphs = content.split('\n\n')
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if para.startswith('- ') or para.startswith('* '):
                # Handle bullet points
                bullet_items = para.split('\n')
                for item in bullet_items:
                    if item.strip().startswith(('- ', '* ')):
                        bullet_text = item.strip()[2:]
                        bullet_para = Paragraph(f'• {bullet_text}', self.styles['BulletStyle'])
                        self.story.append(bullet_para)
            
            elif para.startswith('**') and para.endswith('**'):
                # Handle bold text as emphasis
                emphasis_text = para.replace('**', '')
                emphasis_style = ParagraphStyle(
                    name='Emphasis',
                    parent=self.styles['Normal'],
                    fontSize=12,
                    fontName='Helvetica-Bold',
                    spaceAfter=10,
                    textColor=HexColor('#2E86AB')
                )
                emphasis_para = Paragraph(emphasis_text, emphasis_style)
                self.story.append(emphasis_para)
            
            else:
                # Regular paragraph
                # Clean up markdown formatting
                clean_para = self.clean_markdown_formatting(para)
                if clean_para:
                    para_element = Paragraph(clean_para, self.styles['Normal'])
                    self.story.append(para_element)
                    self.story.append(Spacer(1, 6))

    def clean_markdown_formatting(self, text):
        """Clean markdown formatting for PDF"""
        # Convert bold
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        # Convert italic
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        # Convert inline code
        text = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', text)
        # Remove markdown links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def generate_pdf(self):
        """Generate the final PDF"""
        try:
            print("Parsing markdown content...")
            self.parse_markdown_content()
            
            print("Building PDF document...")
            self.doc.build(self.story)
            
            print(f"PDF generated successfully: {self.output_file}")
            return True
            
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            return False

def main():
    """Main function to generate the PDF documentation"""
    # File paths
    current_dir = Path(__file__).parent
    markdown_file = current_dir / "MediSync_System_Process_Documentation.md"
    output_file = current_dir / "MediSync_System_Process_Documentation.pdf"
    
    # Check if markdown file exists
    if not markdown_file.exists():
        print(f"Error: Markdown file not found: {markdown_file}")
        return False
    
    # Generate PDF
    print("Starting MediSync PDF Documentation Generation...")
    print(f"Input file: {markdown_file}")
    print(f"Output file: {output_file}")
    
    generator = MediSyncPDFGenerator(str(markdown_file), str(output_file))
    success = generator.generate_pdf()
    
    if success:
        print("\n✅ PDF documentation generated successfully!")
        print(f"📄 File location: {output_file}")
        print(f"📊 File size: {output_file.stat().st_size / 1024:.1f} KB")
    else:
        print("\n❌ Failed to generate PDF documentation")
    
    return success

if __name__ == "__main__":
    main()