"""
Build script to generate the official University of Ghana Project Defense presentation
using 'UG SLIDE TEMPLATE.pptx' as the template.

Author: Neal Allison Hughes (ID: 11178252)
Supervisor: Prof. Isaac Wiafe
Institution: Department of Computer Science, University of Ghana, Legon
"""

import os
import sys
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml import parse_xml

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Color Palette Constants
COLOR_NAVY_DEEP    = RGBColor(10, 22, 40)      # #0A1628
COLOR_NAVY_BANNER  = RGBColor(0, 0, 102)      # #000066 Official UG Navy
COLOR_GOLD_ACCENT  = RGBColor(218, 165, 32)    # #DAA520 Official UG Gold
COLOR_GOLD_LIGHT   = RGBColor(245, 158, 11)    # #F59E0B Warm Amber
COLOR_WHITE        = RGBColor(255, 255, 255)   # #FFFFFF
COLOR_TEXT_DARK    = RGBColor(15, 23, 42)      # #0F172A Slate Dark
COLOR_TEXT_MUTED   = RGBColor(71, 85, 105)     # #475569 Slate Muted
COLOR_TEXT_LIGHT   = RGBColor(100, 116, 139)   # #64748B Secondary
COLOR_CARD_BG      = RGBColor(255, 255, 255)   # Pure White Card
COLOR_CARD_BORDER  = RGBColor(203, 213, 225)   # #CBD5E1 Border
COLOR_CARD_ALT_BG  = RGBColor(248, 250, 252)   # #F8FAFC Light Tint
COLOR_CARD_ACCENT  = RGBColor(240, 249, 255)   # #F0F9FF Azure Tint
COLOR_BLUE_PRIMARY = RGBColor(37, 99, 235)     # #2563EB Royal Blue
COLOR_GREEN_EMERALD= RGBColor(5, 150, 105)     # #059669 Emerald Green
COLOR_RED_ROSE     = RGBColor(225, 29, 72)      # #E11D48 Rose

FONT_HEADING = 'Arial'
FONT_BODY    = 'Calibri'

def create_shape(slide, shape_type, left, top, width, height, fill_color=None, border_color=None, border_width=Pt(1)):
    """Creates a basic shape with fill and outline styling."""
    shape = slide.shapes.add_shape(shape_type, left, top, width, height)
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
        
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = border_width
    else:
        shape.line.fill.background()
    return shape

def add_header(slide, category, title):
    """Adds a standard University of Ghana navy banner header."""
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.22), Inches(11.7), Inches(1.18))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0)
    tf.margin_right = Inches(0)
    tf.margin_top = Inches(0)
    tf.margin_bottom = Inches(0)
    
    # Category / Breadcrumb
    p_cat = tf.paragraphs[0]
    p_cat.text = category.upper()
    p_cat.font.name = FONT_HEADING
    p_cat.font.size = Pt(11)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_GOLD_ACCENT
    p_cat.space_after = Pt(2)
    
    # Main Slide Title
    p_title = tf.add_paragraph()
    p_title.text = title
    p_title.font.name = FONT_HEADING
    p_title.font.size = Pt(20)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_WHITE

def add_footer(slide, slide_num, total_slides=22):
    """Adds standard slide footer avoiding the bottom-right UG crest."""
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(6.85), Inches(8.8), Inches(0.35))
    tf = tb.text_frame
    tf.word_wrap = False
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0)
    
    p = tf.paragraphs[0]
    p.text = f"Department of Computer Science • University of Ghana  |  SPIME v4 Defense  |  Slide {slide_num} of {total_slides}"
    p.font.name = FONT_BODY
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_TEXT_LIGHT

def add_card(slide, left, top, width, height, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER, border_width=Pt(1)):
    """Draws a clean content card with optional outline."""
    return create_shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height, bg_color, border_color, border_width)

def add_metric_card(slide, left, top, width, height, value, label, sublabel="", val_color=COLOR_BLUE_PRIMARY):
    """Draws a KPI metric card with large bold numbers."""
    add_card(slide, left, top, width, height, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER)
    
    tb = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.12), width - Inches(0.3), height - Inches(0.24))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0)
    
    # Value
    p_val = tf.paragraphs[0]
    p_val.text = value
    p_val.font.name = FONT_HEADING
    p_val.font.size = Pt(22)
    p_val.font.bold = True
    p_val.font.color.rgb = val_color
    p_val.alignment = PP_ALIGN.CENTER
    
    # Label
    p_lbl = tf.add_paragraph()
    p_lbl.text = label.upper()
    p_lbl.font.name = FONT_HEADING
    p_lbl.font.size = Pt(10)
    p_lbl.font.bold = True
    p_lbl.font.color.rgb = COLOR_TEXT_DARK
    p_lbl.alignment = PP_ALIGN.CENTER
    p_lbl.space_before = Pt(3)
    
    # Sublabel
    if sublabel:
        p_sub = tf.add_paragraph()
        p_sub.text = sublabel
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(9.5)
        p_sub.font.color.rgb = COLOR_TEXT_MUTED
        p_sub.alignment = PP_ALIGN.CENTER

def add_bullet_list(tf, items, font_size=Pt(12), space_after=Pt(6)):
    """Helper to populate bullet points into an existing text frame."""
    for i, item in enumerate(items):
        p = tf.add_paragraph() if i > 0 or len(tf.paragraphs[0].text) > 0 else tf.paragraphs[0]
        p.font.name = FONT_BODY
        p.font.size = font_size
        p.space_after = space_after
        
        if isinstance(item, tuple):
            lead, body = item
            r_lead = p.add_run()
            r_lead.text = lead + " "
            r_lead.font.bold = True
            r_lead.font.color.rgb = COLOR_TEXT_DARK
            
            r_body = p.add_run()
            r_body.text = body
            r_body.font.color.rgb = COLOR_TEXT_MUTED
        else:
            r = p.add_run()
            r.text = item
            r.font.color.rgb = COLOR_TEXT_MUTED

def clear_slide_placeholders(slide):
    """Removes template placeholder shapes while keeping the slide layout background intact."""
    for ph in list(slide.placeholders):
        sp = ph._element
        sp.getparent().remove(sp)

def get_template_image2():
    """Extracts or retrieves the official UG title slide background (image2.jpeg)."""
    cached_path = os.path.join(os.path.dirname(__file__), 'Defense_Presentation', 'extracted_media', 'image2_title_bg.jpeg')
    if os.path.exists(cached_path):
        return cached_path
    import zipfile
    os.makedirs(os.path.dirname(cached_path), exist_ok=True)
    with zipfile.ZipFile('UG SLIDE TEMPLATE.pptx', 'r') as z:
        with open(cached_path, 'wb') as f:
            f.write(z.read('ppt/media/image2.jpeg'))
    return cached_path

def set_title_slide_background(slide, img_path):
    """Sets the official UG title slide background (image2.jpeg) via <p:bg>."""
    img_part, rId = slide.part.get_or_add_image_part(img_path)
    bg_xml = (
        f'<p:bg xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        f'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        f'<p:bgPr><a:blipFill rotWithShape="0">'
        f'<a:blip r:embed="{rId}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/>'
        f'<a:stretch><a:fillRect/></a:stretch>'
        f'</a:blipFill><a:effectLst/></p:bgPr></p:bg>'
    )
    bg_element = parse_xml(bg_xml)
    existing_bg = slide._element.find('{http://schemas.openxmlformats.org/presentationml/2006/main}bg')
    if existing_bg is not None:
        slide._element.remove(existing_bg)
    slide._element.insert(0, bg_element)

# ════════════════════════════════════════════════════════════════════════════════
# SLIDE BUILDERS (1 TO 22)
# ════════════════════════════════════════════════════════════════════════════════

def build_slide_1(prs, layout):
    """Slide 1: Title Slide (Official UG Navy & Crest Title Background)."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    set_title_slide_background(slide, get_template_image2())
    
    # Header Banner text in upper navy area
    tb_inst = slide.shapes.add_textbox(Inches(1.0), Inches(0.45), Inches(11.33), Inches(0.65))
    tf_inst = tb_inst.text_frame
    tf_inst.word_wrap = True
    p1 = tf_inst.paragraphs[0]
    p1.text = "COLLEGE OF BASIC AND APPLIED SCIENCES  •  DEPARTMENT OF COMPUTER SCIENCE"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_GOLD_ACCENT
    p1.alignment = PP_ALIGN.CENTER
    
    # Project Title
    tb_title = slide.shapes.add_textbox(Inches(1.0), Inches(1.15), Inches(11.33), Inches(1.65))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    p_t = tf_title.paragraphs[0]
    p_t.text = "SPIME: A Stacked Physics-Informed Meta-Ensemble for Low-Cost PM2.5 Sensor Calibration Under High Humidity and Harmattan Dust in Sub-Saharan Africa"
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(23)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_WHITE
    p_t.alignment = PP_ALIGN.CENTER
    
    # Subtitle / Examination Tag
    tb_sub = slide.shapes.add_textbox(Inches(1.0), Inches(2.95), Inches(11.33), Inches(0.55))
    tf_sub = tb_sub.text_frame
    p_s = tf_sub.paragraphs[0]
    p_s.text = "B.Sc. Computer Science  •  Final Year Project Defense & Oral Examination"
    p_s.font.name = FONT_BODY
    p_s.font.size = Pt(15)
    p_s.font.bold = True
    p_s.font.color.rgb = COLOR_GOLD_LIGHT
    p_s.alignment = PP_ALIGN.CENTER
    
    # Cards Container in navy area (above y = 6.06 in)
    # Left Card: Candidate Details
    c_left = add_card(slide, Inches(1.5), Inches(3.65), Inches(4.9), Inches(2.05),
                      bg_color=RGBColor(17, 31, 53), border_color=RGBColor(59, 130, 246))
    tb_cand = slide.shapes.add_textbox(Inches(1.75), Inches(3.80), Inches(4.4), Inches(1.75))
    tf_cand = tb_cand.text_frame
    tf_cand.word_wrap = True
    
    p_c_hdr = tf_cand.paragraphs[0]
    p_c_hdr.text = "CANDIDATE DETAILS"
    p_c_hdr.font.name = FONT_HEADING
    p_c_hdr.font.size = Pt(11)
    p_c_hdr.font.bold = True
    p_c_hdr.font.color.rgb = COLOR_GOLD_ACCENT
    p_c_hdr.space_after = Pt(6)
    
    add_bullet_list(tf_cand, [
        ("Candidate Name:", "Neal Allison Hughes"),
        ("Student ID:", "11178252"),
        ("Programme:", "B.Sc. Computer Science (Honours)")
    ], font_size=Pt(12), space_after=Pt(4))
    
    # Right Card: Supervisory & Facility
    c_right = add_card(slide, Inches(6.9), Inches(3.65), Inches(4.9), Inches(2.05),
                       bg_color=RGBColor(17, 31, 53), border_color=RGBColor(59, 130, 246))
    tb_sup = slide.shapes.add_textbox(Inches(7.15), Inches(3.80), Inches(4.4), Inches(1.75))
    tf_sup = tb_sup.text_frame
    tf_sup.word_wrap = True
    
    p_s_hdr = tf_sup.paragraphs[0]
    p_s_hdr.text = "SUPERVISION & RESEARCH FACILITY"
    p_s_hdr.font.name = FONT_HEADING
    p_s_hdr.font.size = Pt(11)
    p_s_hdr.font.bold = True
    p_s_hdr.font.color.rgb = COLOR_GOLD_ACCENT
    p_s_hdr.space_after = Pt(6)
    
    add_bullet_list(tf_sup, [
        ("Principal Supervisor:", "Prof. Isaac Wiafe"),
        ("Academic Unit:", "Department of Computer Science"),
        ("Evaluation Hub:", "Afri-SET Facility, Dept. of Physics"),
        ("Date of Defense:", "October 2026")
    ], font_size=Pt(11.5), space_after=Pt(3))
    
    return slide

def build_slide_2(prs, layout):
    """Slide 2: Overview & Roadmap."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "00 | OVERVIEW", "Presentation Outline & Research Roadmap")
    add_footer(slide, 2)
    
    sections = [
        ("01", "Context & Problem Statement", "Sub-Saharan Africa air quality health burden, low-cost optical particle counter (OPC) mechanics, physical hygroscopic swelling, and factory calibration failure."),
        ("02", "Research Objectives & Experimental Hub", "Primary research aim, four measurable specific objectives, and the Afri-SET co-location evaluation platform at University of Ghana, Legon."),
        ("03", "Methodology & Architecture", "75-dimensional physics-informed feature engineering, multi-gamma empirical Köhler curves, and the SPIME v4 hierarchical stacking meta-ensemble."),
        ("04", "Empirical Results & Diagnostics", "Out-of-sample 6-month holdout performance (R² = 0.9632, MAE = 0.61 µg/m³), elimination of overfitting, 1:1 parity alignment, SHAP attribution, and residual diagnostics."),
        ("05", "Cloud Deployment & Conclusion", "Asynchronous containerized FastAPI microservice, AirSense live web studio, core scientific contributions, study limitations, and future research roadmap.")
    ]
    
    top_y = 1.75
    card_h = 0.88
    gap = 0.12
    
    for i, (num, title, desc) in enumerate(sections):
        curr_y = top_y + i * (card_h + gap)
        
        # Number pill card
        add_card(slide, Inches(0.8), Inches(curr_y), Inches(1.1), Inches(card_h),
                 bg_color=COLOR_NAVY_BANNER, border_color=COLOR_GOLD_ACCENT)
        tb_num = slide.shapes.add_textbox(Inches(0.8), Inches(curr_y + 0.18), Inches(1.1), Inches(0.5))
        tf_num = tb_num.text_frame
        p_n = tf_num.paragraphs[0]
        p_n.text = num
        p_n.font.name = FONT_HEADING
        p_n.font.size = Pt(22)
        p_n.font.bold = True
        p_n.font.color.rgb = COLOR_WHITE
        p_n.alignment = PP_ALIGN.CENTER
        
        # Content Card
        add_card(slide, Inches(2.05), Inches(curr_y), Inches(10.45), Inches(card_h),
                 bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER)
        tb_text = slide.shapes.add_textbox(Inches(2.25), Inches(curr_y + 0.10), Inches(10.05), Inches(card_h - 0.20))
        tf_text = tb_text.text_frame
        tf_text.word_wrap = True
        
        p_t = tf_text.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(13.5)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_BLUE_PRIMARY
        p_t.space_after = Pt(2)
        
        p_d = tf_text.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_3(prs, layout):
    """Slide 3: Context & Motivation."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "01 | INTRODUCTION", "Background: The Air Quality Crisis & Monitoring Void in Sub-Saharan Africa")
    add_footer(slide, 3)
    
    # Left Narrative Card
    add_card(slide, Inches(0.8), Inches(1.75), Inches(5.6), Inches(4.85))
    tb_left = slide.shapes.add_textbox(Inches(1.05), Inches(1.95), Inches(5.1), Inches(4.45))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True
    
    p = tf_left.paragraphs[0]
    p.text = "The Sub-Saharan Africa Air Pollution Burden"
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_PRIMARY
    p.space_after = Pt(10)
    
    bullets = [
        ("Global Health Toll:", "Ambient fine particulate matter (PM2.5) is the second leading risk factor for premature death in Sub-Saharan Africa, responsible for over 1.1 million deaths annually."),
        ("Urban Emission Hotspots:", "Rapid urban expansion across Greater Accra drives severe particulate exposure from vehicular exhaust, unpaved road dust, and biomass burning."),
        ("The Regulatory Cost Barrier:", "Reference-grade Beta Attenuation Monitors (BAM-1020) and Teledyne T640 spectrometers cost $30,000–$50,000 each with high recurring operational costs, resulting in fewer than 1 regulatory monitor per 10 million residents."),
        ("Low-Cost Sensor Opportunity:", "Low-cost optical particle counters ($150–$300) offer unprecedented spatial density, but suffer from catastrophic measurement errors in tropical climates without advanced calibration.")
    ]
    add_bullet_list(tf_left, bullets, font_size=Pt(11.5), space_after=Pt(8))
    
    # Right Column: 3 Metric Cards + Motivation Card
    add_metric_card(slide, Inches(6.6), Inches(1.75), Inches(5.9), Inches(1.15),
                    "1.1 Million+", "ANNUAL PREMATURE DEATHS IN AFRICA", "Attributable to ambient fine particulate matter (HEI, 2022)", COLOR_RED_ROSE)
                    
    add_metric_card(slide, Inches(6.6), Inches(3.02), Inches(5.9), Inches(1.15),
                    "$30,000 – $50,000", "REFERENCE MONITOR COST BARRIER", "Teledyne T640 / BAM-1020 capital expense per monitoring station", COLOR_NAVY_BANNER)
                    
    add_metric_card(slide, Inches(6.6), Inches(4.29), Inches(5.9), Inches(1.15),
                    "< 1 Per 10M People", "REGULATORY MONITORING DENSITY", "Severe spatial data void across West African population centers", COLOR_GOLD_ACCENT)
                    
    # Motivation Banner Box
    add_card(slide, Inches(6.6), Inches(5.56), Inches(5.9), Inches(1.04),
             bg_color=COLOR_CARD_ACCENT, border_color=COLOR_BLUE_PRIMARY)
    tb_mot = slide.shapes.add_textbox(Inches(6.8), Inches(5.62), Inches(5.5), Inches(0.92))
    tf_mot = tb_mot.text_frame
    tf_mot.word_wrap = True
    p_m_lbl = tf_mot.paragraphs[0]
    p_m_lbl.text = "CORE RESEARCH MOTIVATION:"
    p_m_lbl.font.name = FONT_HEADING
    p_m_lbl.font.size = Pt(11)
    p_m_lbl.font.bold = True
    p_m_lbl.font.color.rgb = COLOR_BLUE_PRIMARY
    
    p_m_txt = tf_mot.add_paragraph()
    p_m_txt.text = "To bridge this $30,000 economic divide by transforming affordable $200 sensors into regulatory-grade environmental instruments via physics-informed machine learning."
    p_m_txt.font.name = FONT_BODY
    p_m_txt.font.size = Pt(11)
    p_m_txt.font.color.rgb = COLOR_TEXT_DARK

    return slide

def build_slide_4(prs, layout):
    """Slide 4: Optical Particle Counters Mechanics."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "01 | INTRODUCTION", "Optical Particle Counters: Working Principles & Physical Distortions")
    add_footer(slide, 4)
    
    # Left Narrative Card
    add_card(slide, Inches(0.8), Inches(1.75), Inches(5.4), Inches(4.85))
    tb_left = slide.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.0), Inches(4.45))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True
    
    p = tf_left.paragraphs[0]
    p.text = "Optical Particle Counter (OPC) Mechanics"
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_PRIMARY
    p.space_after = Pt(10)
    
    bullets = [
        ("Mie Light Scattering:", "An internal infrared laser diode illuminates aerosol particles traversing the optical sensing chamber. A photo-detector captures scattered light pulses."),
        ("Pulse-Height Sizing:", "The intensity of scattered light scales with optical particle diameter, binning counts into size categories assuming spherical particles with constant refractive index (m = 1.5 + 0i)."),
        ("Physical Distortion 1 (Hygroscopic Swelling):", "When relative humidity exceeds the Deliquescence point (~75%), soluble aerosols absorb ambient moisture and swell in size. The sensor counts water droplets as dry dust, inflating PM2.5 by up to 300%."),
        ("Physical Distortion 2 (Harmattan Coarse Dust):", "Irregular, non-spherical Saharan mineral dust grains cause optical scattering saturation, leading to severe under-counting in dry winter months.")
    ]
    add_bullet_list(tf_left, bullets, font_size=Pt(11.5), space_after=Pt(8))
    
    # Right Column: Figure 2.1
    img_path = 'figures/fig_2_1_opc_working_principle.png'
    add_card(slide, Inches(6.5), Inches(1.75), Inches(6.0), Inches(4.85))
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(6.7), Inches(1.95), width=Inches(5.6))
        
    tb_cap = slide.shapes.add_textbox(Inches(6.6), Inches(6.05), Inches(5.8), Inches(0.45))
    tf_cap = tb_cap.text_frame
    p_c = tf_cap.paragraphs[0]
    p_c.text = "Figure 2.1: Optical Particle Counter (OPC) Mie Scattering & Hygroscopic Swelling Mechanism"
    p_c.font.name = FONT_BODY
    p_c.font.size = Pt(10)
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_TEXT_MUTED
    p_c.alignment = PP_ALIGN.CENTER

    return slide

def build_slide_5(prs, layout):
    """Slide 5: Problem Statement & Existing ML Gaps."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "01 | INTRODUCTION", "Problem Statement & Critical Gaps in Existing Calibration Methods")
    add_footer(slide, 5)
    
    gaps = [
        ("1. Factory Calibration Breakdown", 
         "Factory calibration algorithms are derived in temperate laboratory chambers under low humidity. In West Africa's tropical climate, raw sensor readings collapse to near-zero correlation (R² = -0.0133, MAE = 5.30 µg/m³), rendering uncalibrated data scientifically invalid.",
         COLOR_RED_ROSE),
        ("2. Baseline ML Incapacity & Linearity Assumptions", 
         "Standard linear models (R² = 0.6760) and multi-linear regressions assume linear meteorological responses. They fail to capture exponential hygroscopic growth past deliquescence thresholds and complex non-linear atmospheric interactions.",
         COLOR_GOLD_LIGHT),
        ("3. Deep Learning Overfitting & Noise Memorization", 
         "Deep Neural Networks (MLP, LSTM) achieve high in-sample training fit (R² = 0.9232) but suffer catastrophic drops on holdout test sets (R² = 0.5214, ΔR² = +0.4018), memorizing microclimate noise rather than true atmospheric physics.",
         COLOR_BLUE_PRIMARY),
        ("4. Neglect of Harmattan Mineral Dust Regimes", 
         "Existing calibration models developed in Europe or North America assume constant aerosol chemistry. They completely fail during the West African Harmattan season, where coarse Saharan dust shifts particle size distributions drastically.",
         COLOR_NAVY_BANNER)
    ]
    
    xs = [Inches(0.8), Inches(6.7)]
    ys = [Inches(1.75), Inches(4.25)]
    w = Inches(5.7)
    h = Inches(2.35)
    
    for idx, (title, desc, color) in enumerate(gaps):
        x = xs[idx % 2]
        y = ys[idx // 2]
        
        add_card(slide, x, y, w, h, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER)
        
        # Color bar on left edge of card
        create_shape(slide, MSO_SHAPE.RECTANGLE, x, y, Inches(0.12), h, fill_color=color, border_color=None)
        
        tb = slide.shapes.add_textbox(x + Inches(0.3), y + Inches(0.2), w - Inches(0.45), h - Inches(0.35))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(13.5)
        p_t.font.bold = True
        p_t.font.color.rgb = color
        p_t.space_after = Pt(6)
        
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_6(prs, layout):
    """Slide 6: Research Aim & Specific Objectives."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "02 | OBJECTIVES", "Research Aim & Specific Measurable Objectives")
    add_footer(slide, 6)
    
    # Primary Research Aim Card
    add_card(slide, Inches(0.8), Inches(1.75), Inches(11.7), Inches(1.15),
             bg_color=COLOR_NAVY_BANNER, border_color=COLOR_GOLD_ACCENT)
    tb_aim = slide.shapes.add_textbox(Inches(1.1), Inches(1.85), Inches(11.1), Inches(0.95))
    tf_aim = tb_aim.text_frame
    tf_aim.word_wrap = True
    
    p_a_lbl = tf_aim.paragraphs[0]
    p_a_lbl.text = "PRIMARY RESEARCH AIM"
    p_a_lbl.font.name = FONT_HEADING
    p_a_lbl.font.size = Pt(11)
    p_a_lbl.font.bold = True
    p_a_lbl.font.color.rgb = COLOR_GOLD_ACCENT
    p_a_lbl.space_after = Pt(2)
    
    p_a_txt = tf_aim.add_paragraph()
    p_a_txt.text = "To design, evaluate, and deploy a physics-informed, non-overfitting machine learning calibration framework (SPIME v4) that elevates low-cost OPC sensors to regulatory-grade accuracy across tropical wet and Harmattan dust seasons in Sub-Saharan Africa."
    p_a_txt.font.name = FONT_BODY
    p_a_txt.font.size = Pt(12.5)
    p_a_txt.font.color.rgb = COLOR_WHITE
    
    # 4 Specific Objectives
    objs = [
        ("Objective 1: Physics-Informed Feature Engineering",
         "Formulate a 75-dimensional feature space integrating multi-gamma empirical Köhler swelling models, thermodynamic moisture terms, EWMA lag dynamics, and seasonal Harmattan coarse dust ratios."),
        ("Objective 2: Hierarchical Stacking Architecture",
         "Develop a multi-stage stacking meta-ensemble (SPIME v4) combining diverse base learners (LightGBM, Random Forest, Extra Trees, Gradient Boosting) via an L2-regularized Ridge meta-regressor."),
        ("Objective 3: Rigorous Holdout & Anti-Overfitting Validation",
         "Benchmark calibration accuracy on an unseen 6-month chronological holdout dataset (3,468 hourly records) under 5-Fold out-of-fold cross-validation to guarantee zero generalization loss."),
        ("Objective 4: Operational Edge/Cloud Deployment",
         "Package the complete calibrated pipeline into an open-source, containerized microservice (FastAPI/Docker) with sub-10ms inference and automated EPA AQI calculation.")
    ]
    
    top_y = 3.05
    card_h = 0.82
    gap = 0.10
    
    for i, (title, desc) in enumerate(objs):
        curr_y = top_y + i * (card_h + gap)
        add_card(slide, Inches(0.8), Inches(curr_y), Inches(11.7), Inches(card_h),
                 bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER)
                 
        tb = slide.shapes.add_textbox(Inches(1.1), Inches(curr_y + 0.08), Inches(11.1), Inches(card_h - 0.16))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(12.5)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_BLUE_PRIMARY
        
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_7(prs, layout):
    """Slide 7: Experimental Platform: Co-location Setup at Afri-SET."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "03 | METHODOLOGY", "Experimental Platform: Co-location Setup & Instrumentation")
    add_footer(slide, 7)
    
    # Left Narrative Card
    add_card(slide, Inches(0.8), Inches(1.75), Inches(5.5), Inches(4.85))
    tb_left = slide.shapes.add_textbox(Inches(1.05), Inches(1.95), Inches(5.0), Inches(4.45))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True
    
    p = tf_left.paragraphs[0]
    p.text = "Co-location Monitoring Infrastructure"
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_PRIMARY
    p.space_after = Pt(10)
    
    bullets = [
        ("Research Facility:", "African Sensor Evaluation and Training Facility (Afri-SET), Department of Physics, University of Ghana, Legon (Accra, Ghana)."),
        ("Low-Cost Sensor Device:", "QuantAQ Modulair-PM (MOD-PM-01068) equipped with optical particle counter (OPC-N3) measuring PM1, PM2.5, PM10, relative humidity, temperature, and dew point."),
        ("Regulatory Gold Standard:", "Teledyne API T640 US EPA Federal Equivalent Method (FEM) continuous ambient particulate spectrometer providing true ground-truth PM2.5 mass concentrations."),
        ("Environmental Scope:", "Continuous hourly co-location data spanning over a full annual cycle, capturing intense tropical monsoon rainfall and dry Saharan dust storms.")
    ]
    add_bullet_list(tf_left, bullets, font_size=Pt(11.5), space_after=Pt(8))
    
    # Right Column: 3 Stat Cards + Data Protocol
    add_metric_card(slide, Inches(6.6), Inches(1.75), Inches(5.9), Inches(1.15),
                    "Afri-SET Facility", "TESTING & EVALUATION HUB", "Department of Physics, University of Ghana, Legon", COLOR_NAVY_BANNER)
                    
    add_metric_card(slide, Inches(6.6), Inches(3.02), Inches(5.9), Inches(1.15),
                    "Teledyne API T640", "REGULATORY GOLD STANDARD", "US EPA FEM Certified Continuous Ambient Spectrometer", COLOR_GREEN_EMERALD)
                    
    add_metric_card(slide, Inches(6.6), Inches(4.29), Inches(5.9), Inches(1.15),
                    "3,468 Hourly Records", "6-MONTH UNSEEN HOLDOUT SET", "Strictly out-of-sample temporal evaluation dataset", COLOR_GOLD_ACCENT)
                    
    # Data Quality Protocol Card
    add_card(slide, Inches(6.6), Inches(5.56), Inches(5.9), Inches(1.04),
             bg_color=COLOR_CARD_ALT_BG, border_color=COLOR_CARD_BORDER)
    tb_proto = slide.shapes.add_textbox(Inches(6.8), Inches(5.62), Inches(5.5), Inches(0.92))
    tf_proto = tb_proto.text_frame
    tf_proto.word_wrap = True
    p_p_lbl = tf_proto.paragraphs[0]
    p_p_lbl.text = "DATA INTEGRITY PROTOCOL:"
    p_p_lbl.font.name = FONT_HEADING
    p_p_lbl.font.size = Pt(11)
    p_p_lbl.font.bold = True
    p_p_lbl.font.color.rgb = COLOR_TEXT_DARK
    
    p_p_txt = tf_proto.add_paragraph()
    p_p_txt.text = "Strict quality assurance: sample flow rate stabilization, removal of negative particulate readings, and chronological alignment ensuring zero temporal data leakage."
    p_p_txt.font.name = FONT_BODY
    p_p_txt.font.size = Pt(11)
    p_p_txt.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_8(prs, layout):
    """Slide 8: End-to-End Machine Learning Calibration Pipeline."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "03 | METHODOLOGY", "End-to-End Machine Learning Calibration Pipeline")
    add_footer(slide, 8)
    
    img_path = 'figures/fig_3_2_calibration_pipeline.png'
    add_card(slide, Inches(0.8), Inches(1.75), Inches(11.7), Inches(4.85))
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(1.0), Inches(1.95), width=Inches(11.3), height=Inches(4.1))
        
    tb_cap = slide.shapes.add_textbox(Inches(1.0), Inches(6.15), Inches(11.3), Inches(0.40))
    tf_cap = tb_cap.text_frame
    p_c = tf_cap.paragraphs[0]
    p_c.text = "Figure 3.2: Five-Stage Physics-Informed Machine Learning Calibration Pipeline (Ingestion -> Physics Engineering -> 5-Fold OOF Stacking -> Meta-Inference -> Production Deployment)"
    p_c.font.name = FONT_BODY
    p_c.font.size = Pt(11)
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_TEXT_MUTED
    p_c.alignment = PP_ALIGN.CENTER

    return slide

def build_slide_9(prs, layout):
    """Slide 9: 75-Dimensional Physics-Informed Feature Space."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "03 | METHODOLOGY", "75-Dimensional Physics-Informed Feature Engineering")
    add_footer(slide, 9)
    
    features = [
        ("1. Empirical Köhler Hygroscopic Growth (15 Features)",
         "Models non-linear aerosol diameter swelling: f(RH) = 1 + a·(RH/100)^b / (1 - RH/100). Parameterizes multiple growth factors across γ ∈ [0.2, 0.8], kappa-Köhler moisture deltas, and optical ratio interactions.",
         COLOR_BLUE_PRIMARY),
        ("2. Thermodynamic Moisture Formulations (18 Features)",
         "Decouples relative humidity from temperature: Vapor Pressure Deficit (VPD), Dew Point depression (T - Td), psychrometric water vapor density, and absolute moisture content (g/m³).",
         COLOR_GREEN_EMERALD),
        ("3. Multi-Window Temporal EWMA Dynamics (24 Features)",
         "Exponentially Weighted Moving Averages (EWMA) across 1h, 3h, 6h, 12h, and 24h spans capturing boundary-layer diurnal ventilation, atmospheric stagnation, and sensor chamber thermal inertia.",
         COLOR_GOLD_ACCENT),
        ("4. Seasonal Harmattan & Temporal Harmonics (18 Features)",
         "Harmattan mineral dust ratio (PM10/PM2.5), coarse fraction (PM10 - PM2.5), diurnal sinusoidal harmonics (sin/cos of hour), and seasonal dry-season transition flags.",
         COLOR_NAVY_BANNER)
    ]
    
    xs = [Inches(0.8), Inches(6.7)]
    ys = [Inches(1.75), Inches(4.25)]
    w = Inches(5.7)
    h = Inches(2.35)
    
    for idx, (title, desc, color) in enumerate(features):
        x = xs[idx % 2]
        y = ys[idx // 2]
        
        add_card(slide, x, y, w, h, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER)
        create_shape(slide, MSO_SHAPE.RECTANGLE, x, y, Inches(0.12), h, fill_color=color, border_color=None)
        
        tb = slide.shapes.add_textbox(x + Inches(0.3), y + Inches(0.2), w - Inches(0.45), h - Inches(0.35))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(13.5)
        p_t.font.bold = True
        p_t.font.color.rgb = color
        p_t.space_after = Pt(6)
        
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_10(prs, layout):
    """Slide 10: SPIME v4 Hierarchical Stacking Architecture."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "03 | METHODOLOGY", "SPIME v4: Hierarchical Stacking Meta-Ensemble Architecture")
    add_footer(slide, 10)
    
    img_path = 'figures/fig_3_6_spime_architecture.png'
    add_card(slide, Inches(0.8), Inches(1.75), Inches(11.7), Inches(4.85))
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(1.0), Inches(1.95), width=Inches(11.3), height=Inches(4.1))
        
    tb_cap = slide.shapes.add_textbox(Inches(1.0), Inches(6.15), Inches(11.3), Inches(0.40))
    tf_cap = tb_cap.text_frame
    p_c = tf_cap.paragraphs[0]
    p_c.text = "Figure 3.3: SPIME v4 Two-Level Hierarchical Stacking Architecture (Diverse Level-1 Base Learners + Out-of-Fold Matrix + L2 Regularized Ridge Meta-Regressor)"
    p_c.font.name = FONT_BODY
    p_c.font.size = Pt(11)
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_TEXT_MUTED
    p_c.alignment = PP_ALIGN.CENTER

    return slide

def build_slide_11(prs, layout):
    """Slide 11: Validation Protocol & Anti-Overfitting Design."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "03 | METHODOLOGY", "Validation Protocol: Chronological Partitioning & Anti-Overfitting Design")
    add_footer(slide, 11)
    
    # Left Narrative Card
    add_card(slide, Inches(0.8), Inches(1.75), Inches(5.2), Inches(4.85))
    tb_left = slide.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(4.8), Inches(4.45))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True
    
    p = tf_left.paragraphs[0]
    p.text = "Strict Out-of-Sample Protocol"
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_PRIMARY
    p.space_after = Pt(10)
    
    bullets = [
        ("Chronological Train-Holdout Split:", "The co-location dataset was partitioned strictly across time: Training split (60%), Validation split (20%), and an unseen 6-Month Holdout split (20%, 3,468 hourly observations)."),
        ("No Shuffling Across Time:", "Random shuffling was strictly prohibited to prevent data leakage and autocorrelation artifacts between consecutive hours."),
        ("5-Fold Out-of-Fold (OOF) Stacking:", "Level-1 models generate out-of-fold predictions on unobserved training folds, guaranteeing that the Level-2 meta-regressor never sees in-sample training bias."),
        ("Zero Generalization Loss Guarantee:", "Prevents the model from memorizing microclimate noise, achieving seamless cross-season generalization.")
    ]
    add_bullet_list(tf_left, bullets, font_size=Pt(11.5), space_after=Pt(8))
    
    # Right Column: Figure 3.4
    img_path = 'figures/fig_3_7_validation_scheme.png'
    add_card(slide, Inches(6.3), Inches(1.75), Inches(6.2), Inches(4.85))
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(6.5), Inches(2.25), width=Inches(5.8))
        
    tb_cap = slide.shapes.add_textbox(Inches(6.4), Inches(6.05), Inches(6.0), Inches(0.45))
    tf_cap = tb_cap.text_frame
    p_c = tf_cap.paragraphs[0]
    p_c.text = "Figure 3.4: Chronological Data Split & 5-Fold Out-of-Fold Stacking Protocol"
    p_c.font.name = FONT_BODY
    p_c.font.size = Pt(10.5)
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_TEXT_MUTED
    p_c.alignment = PP_ALIGN.CENTER

    return slide

def build_slide_12(prs, layout):
    """Slide 12: Empirical Benchmark Results."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "04 | RESULTS", "Empirical Results on Unseen 6-Month Chronological Holdout Set")
    add_footer(slide, 12)
    
    # 4 KPI Stat Cards
    add_metric_card(slide, Inches(0.8), Inches(1.75), Inches(2.75), Inches(1.15),
                    "R² = 0.9632", "HOLDOUT ACCURACY", "6-Month Unseen Holdout", COLOR_GREEN_EMERALD)
                    
    add_metric_card(slide, Inches(3.75), Inches(1.75), Inches(2.75), Inches(1.15),
                    "MAE = 0.61 µg/m³", "MEAN ABSOLUTE ERROR", "66.3% Error Reduction", COLOR_BLUE_PRIMARY)
                    
    add_metric_card(slide, Inches(6.70), Inches(1.75), Inches(2.75), Inches(1.15),
                    "RMSE = 1.23 µg/m³", "ROOT MEAN SQ ERROR", "Reference-Grade Precision", COLOR_NAVY_BANNER)
                    
    add_metric_card(slide, Inches(9.65), Inches(1.75), Inches(2.85), Inches(1.15),
                    "ΔR² = -0.0002", "OVERFITTING GAP", "Zero Generalization Loss", COLOR_GOLD_ACCENT)
                    
    # Benchmark Comparison Table
    headers = ["Model / Calibration Framework", "Holdout R²", "MAE (µg/m³)", "RMSE (µg/m³)", "MAPE (%)", "Overfit Gap (ΔR²)"]
    rows = [
        ["Raw Factory Sensor (Modulair-PM)", "-0.0133", "5.30", "7.14", "184.2%", "N/A (Failed)"],
        ["Baseline Linear Regression", "0.6760", "2.68", "3.63", "84.5%", "+0.0120"],
        ["Multilayer Perceptron (MLP Neural Net)", "0.5214", "3.12", "4.41", "96.8%", "+0.4018 (Severe)"],
        ["Random Forest (Stand-Alone)", "0.7752", "2.03", "3.03", "68.4%", "+0.1420 (Moderate)"],
        ["SPIME v4 (Proposed Meta-Ensemble)", "0.9632", "0.61", "1.23", "18.2%", "-0.0002 (Zero Gap)"]
    ]
    
    table_shape = slide.shapes.add_table(len(rows) + 1, len(headers), Inches(0.8), Inches(3.15), Inches(11.7), Inches(3.35))
    tbl = table_shape.table
    
    col_widths = [Inches(3.8), Inches(1.5), Inches(1.6), Inches(1.6), Inches(1.5), Inches(1.7)]
    for idx, w in enumerate(col_widths):
        tbl.columns[idx].width = w
        
    for j, h_text in enumerate(headers):
        cell = tbl.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY_BANNER
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT
        
    for i, row in enumerate(rows):
        is_champion = (i == len(rows) - 1)
        row_bg = RGBColor(240, 249, 255) if is_champion else (COLOR_CARD_ALT_BG if i % 2 == 1 else COLOR_WHITE)
        
        for j, val in enumerate(row):
            cell = tbl.cell(i + 1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = row_bg
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT_BODY
            p.font.size = Pt(11 if not is_champion else 12)
            p.font.bold = is_champion
            p.alignment = PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT
            
            if is_champion:
                p.font.color.rgb = COLOR_GREEN_EMERALD if j in [1, 5] else COLOR_BLUE_PRIMARY
            else:
                p.font.color.rgb = COLOR_TEXT_DARK

    return slide

def build_slide_13(prs, layout):
    """Slide 13: Holdout Calibration Parity Plot."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "04 | RESULTS", "Holdout Calibration Accuracy: 1:1 Parity Alignment with Reference BAM")
    add_footer(slide, 13)
    
    # Left Narrative Card
    add_card(slide, Inches(0.8), Inches(1.75), Inches(5.2), Inches(4.85))
    tb_left = slide.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(4.8), Inches(4.45))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True
    
    p = tf_left.paragraphs[0]
    p.text = "1:1 Reference Agreement"
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_PRIMARY
    p.space_after = Pt(10)
    
    bullets = [
        ("Near-Perfect Linearity:", "Calibrated predictions align tightly along the ideal 1:1 line (y = x) across both low and extreme pollution episodes (0 to 150 µg/m³)."),
        ("Elimination of Sensor Saturation:", "Non-linear response curve accurately linearizes optical detector response during heavy smoke and dust events."),
        ("US EPA Federal Equivalency Performance:", "Achieves slope m = 0.984 (ideal 1.00 ± 0.10) and intercept b = +0.12 (ideal 0.00 ± 5.00), meeting EPA FEM precision requirements."),
        ("High-Concentration Fidelity:", "Extreme peaks during Harmattan dust incursions are tracked with reference fidelity, avoiding under-estimation.")
    ]
    add_bullet_list(tf_left, bullets, font_size=Pt(11.5), space_after=Pt(8))
    
    # Right Column: Parity Plot Image
    img_path = 'Defense_Presentation/extracted_media/image5.png'
    add_card(slide, Inches(6.3), Inches(1.75), Inches(6.2), Inches(4.85))
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(6.7), Inches(2.05), width=Inches(5.4))
        
    tb_cap = slide.shapes.add_textbox(Inches(6.4), Inches(6.05), Inches(6.0), Inches(0.45))
    tf_cap = tb_cap.text_frame
    p_c = tf_cap.paragraphs[0]
    p_c.text = "Figure 4.1: Reference Teledyne T640 vs. Calibrated SPIME v4 Holdout Parity Plot"
    p_c.font.name = FONT_BODY
    p_c.font.size = Pt(10.5)
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_TEXT_MUTED
    p_c.alignment = PP_ALIGN.CENTER

    return slide

def build_slide_14(prs, layout):
    """Slide 14: Diagnostic Breakdown: Overfitting Elimination."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "04 | RESULTS", "Diagnostic Breakdown: Elimination of Overfitting in Calibration")
    add_footer(slide, 14)
    
    cards = [
        ("The Overfitting Crisis in Deep Learning (ΔR² = +0.4018)",
         "Neural networks (MLP, LSTM) achieved high in-sample training fit (Train R² = 0.9232) but completely collapsed on holdout data (Holdout R² = 0.5214). Over-parameterized architectures memorized high-frequency microclimate noise rather than true underlying physics.",
         COLOR_RED_ROSE),
        ("Why Stand-Alone Ensembles Degrade (ΔR² = +0.1420)",
         "Stand-alone Random Forest achieved Train R² = 0.9172 but dropped to R² = 0.7752 on holdout. Deep decision trees overfit to specific relative humidity threshold splits that did not reoccur in future seasonal cycles.",
         COLOR_GOLD_ACCENT),
        ("How SPIME v4 Solved Overfitting (ΔR² = -0.0002)",
         "SPIME v4 utilizes 5-Fold out-of-fold cross-validation stacking combined with an L2-regularized Ridge meta-regressor. The meta-learner receives predictions only from unobserved folds, achieving near-zero generalization loss (Train R² = 0.9630 vs Holdout R² = 0.9632).",
         COLOR_GREEN_EMERALD)
    ]
    
    top_y = 1.75
    card_h = 1.45
    gap = 0.20
    
    for i, (title, desc, color) in enumerate(cards):
        curr_y = top_y + i * (card_h + gap)
        add_card(slide, Inches(0.8), Inches(curr_y), Inches(11.7), Inches(card_h),
                 bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER)
        create_shape(slide, MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(curr_y), Inches(0.12), Inches(card_h),
                     fill_color=color, border_color=None)
                     
        tb = slide.shapes.add_textbox(Inches(1.15), Inches(curr_y + 0.15), Inches(11.1), Inches(card_h - 0.30))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(14)
        p_t.font.bold = True
        p_t.font.color.rgb = color
        p_t.space_after = Pt(4)
        
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(11.5)
        p_d.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_15(prs, layout):
    """Slide 15: Model Explainability: Feature Attribution & SHAP."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "04 | RESULTS", "Model Explainability: Physics-Guided Feature Attribution & SHAP Rankings")
    add_footer(slide, 15)
    
    # Left Narrative Card
    add_card(slide, Inches(0.8), Inches(1.75), Inches(5.2), Inches(4.85))
    tb_left = slide.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(4.8), Inches(4.45))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True
    
    p = tf_left.paragraphs[0]
    p.text = "Gini Feature Importance Rankings"
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_PRIMARY
    p.space_after = Pt(10)
    
    bullets = [
        ("1. Köhler Physics Dominance (24.5%):", "Multi-gamma hygroscopic growth interaction terms account for the single largest predictive attribution across tree base learners."),
        ("2. Thermodynamic Moisture (18.2%):", "Dew point depression and vapor pressure deficit provide critical non-linear corrections during dawn humidity spikes."),
        ("3. Optical Size Distribution (15.4%):", "Raw PM10/PM2.5 ratio actively signals coarse Saharan dust presence, triggering appropriate scattering corrections."),
        ("4. Temporal EWMA Dynamics (14.1%):", "3-hour and 12-hour moving averages filter out short-term turbulence and transient sensor noise."),
        ("Scientific Validation:", "Confirms that the model learns physical atmospheric mechanisms rather than spurious mathematical correlations.")
    ]
    add_bullet_list(tf_left, bullets, font_size=Pt(11), space_after=Pt(6))
    
    # Right Column: Feature Importance Plot
    img_path = 'figures/fig_4_4_feature_importance.png'
    add_card(slide, Inches(6.3), Inches(1.75), Inches(6.2), Inches(4.85))
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(6.5), Inches(1.95), width=Inches(5.8), height=Inches(4.1))
        
    tb_cap = slide.shapes.add_textbox(Inches(6.4), Inches(6.15), Inches(6.0), Inches(0.40))
    tf_cap = tb_cap.text_frame
    p_c = tf_cap.paragraphs[0]
    p_c.text = "Figure 4.2: Top 20 Feature Importance Attributions Across Tree Models"
    p_c.font.name = FONT_BODY
    p_c.font.size = Pt(10.5)
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_TEXT_MUTED
    p_c.alignment = PP_ALIGN.CENTER

    return slide

def build_slide_16(prs, layout):
    """Slide 16: Seasonal Generalization: Monsoon vs Harmattan."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "04 | RESULTS", "Seasonal Generalization: Performance Across Monsoon & Harmattan Regimes")
    add_footer(slide, 16)
    
    # Left Card: Monsoon Wet Season
    add_card(slide, Inches(0.8), Inches(1.75), Inches(5.7), Inches(4.85))
    create_shape(slide, MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.75), Inches(5.7), Inches(0.12),
                 fill_color=COLOR_BLUE_PRIMARY, border_color=None)
                 
    tb_mon = slide.shapes.add_textbox(Inches(1.05), Inches(2.0), Inches(5.2), Inches(4.45))
    tf_mon = tb_mon.text_frame
    tf_mon.word_wrap = True
    
    p_m = tf_mon.paragraphs[0]
    p_m.text = "1. Monsoon Wet Season (June – October)"
    p_m.font.name = FONT_HEADING
    p_m.font.size = Pt(15)
    p_m.font.bold = True
    p_m.font.color.rgb = COLOR_BLUE_PRIMARY
    p_m.space_after = Pt(10)
    
    bullets_mon = [
        ("Atmospheric Regime:", "Persistent high relative humidity (diurnal peaks > 90%), maritime air masses, frequent rainfall wash-out."),
        ("Physical Challenge:", "Severe hygroscopic aerosol swelling; raw optical sensors over-report particulate mass by 200%–300%."),
        ("SPIME v4 Performance:", "R² = 0.9684, MAE = 0.58 µg/m³, RMSE = 1.18 µg/m³."),
        ("Physics Correction:", "The parameterized Köhler hygroscopic growth curve mathematically deducts condensed water volume, matching reference BAM measurements precisely.")
    ]
    add_bullet_list(tf_mon, bullets_mon, font_size=Pt(11.5), space_after=Pt(8))
    
    # Right Card: Harmattan Dry Season
    add_card(slide, Inches(6.7), Inches(1.75), Inches(5.7), Inches(4.85))
    create_shape(slide, MSO_SHAPE.RECTANGLE, Inches(6.7), Inches(1.75), Inches(5.7), Inches(0.12),
                 fill_color=COLOR_GOLD_LIGHT, border_color=None)
                 
    tb_har = slide.shapes.add_textbox(Inches(6.95), Inches(2.0), Inches(5.2), Inches(4.45))
    tf_har = tb_har.text_frame
    tf_har.word_wrap = True
    
    p_h = tf_har.paragraphs[0]
    p_h.text = "2. Harmattan Dry Season (November – March)"
    p_h.font.name = FONT_HEADING
    p_h.font.size = Pt(15)
    p_h.font.bold = True
    p_h.font.color.rgb = COLOR_GOLD_ACCENT
    p_h.space_after = Pt(10)
    
    bullets_har = [
        ("Atmospheric Regime:", "Dry northeasterly Saharan trade winds, relative humidity drops below 30%, heavy coarse mineral dust incursions."),
        ("Physical Challenge:", "Irregular, non-spherical mineral dust grains cause optical scattering anomalies and detector saturation."),
        ("SPIME v4 Performance:", "R² = 0.9542, MAE = 0.69 µg/m³, RMSE = 1.34 µg/m³."),
        ("Physics Correction:", "Coarse dust fraction cross-terms (PM10/PM2.5) dynamically compensate for non-spherical particle scattering without manual recalibration.")
    ]
    add_bullet_list(tf_har, bullets_har, font_size=Pt(11.5), space_after=Pt(8))

    return slide

def build_slide_17(prs, layout):
    """Slide 17: Statistical Residual Diagnostics."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "04 | RESULTS", "Statistical Residual Diagnostics: Normality, Homoscedasticity & Bias")
    add_footer(slide, 17)
    
    # Left Narrative Card
    add_card(slide, Inches(0.8), Inches(1.75), Inches(5.2), Inches(4.85))
    tb_left = slide.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(4.8), Inches(4.45))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True
    
    p = tf_left.paragraphs[0]
    p.text = "Diagnostic Residual Verification"
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_PRIMARY
    p.space_after = Pt(10)
    
    bullets = [
        ("Zero Mean Error (Unbiasedness):", "Mean prediction error on 3,468 holdout hours is μ = -0.012 µg/m³, proving the absence of systematic calibration drift."),
        ("Gaussian Normality:", "Residual distribution conforms tightly to a normal distribution with minimal skewness (S = 0.08) and controlled kurtosis (K = 3.12)."),
        ("Homoscedasticity:", "Residual variance remains uniform across all concentration ranges (0 to 150 µg/m³), confirming error does not explode during extreme pollution spikes."),
        ("Durbin-Watson Test (d = 1.96):", "Confirms absence of residual serial autocorrelation, satisfying all linear meta-model assumptions.")
    ]
    add_bullet_list(tf_left, bullets, font_size=Pt(11.5), space_after=Pt(8))
    
    # Right Column: Residual Histogram Plot
    img_path = 'figures/fig_4_5_residual_histogram.png'
    add_card(slide, Inches(6.3), Inches(1.75), Inches(6.2), Inches(4.85))
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(6.5), Inches(2.05), width=Inches(5.8))
        
    tb_cap = slide.shapes.add_textbox(Inches(6.4), Inches(6.05), Inches(6.0), Inches(0.45))
    tf_cap = tb_cap.text_frame
    p_c = tf_cap.paragraphs[0]
    p_c.text = "Figure 4.3: Holdout Calibration Residual Distribution & Gaussian Normality Fit"
    p_c.font.name = FONT_BODY
    p_c.font.size = Pt(10.5)
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_TEXT_MUTED
    p_c.alignment = PP_ALIGN.CENTER

    return slide

def build_slide_18(prs, layout):
    """Slide 18: Operational Cloud Deployment & Web Dashboard."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "05 | DEPLOYMENT", "Operational Cloud Deployment & Software Architecture")
    add_footer(slide, 18)
    
    components = [
        ("1. Serialized Model Pipeline Artifact (7.8 MB)",
         "The full SPIME v4 pipeline—including feature scaling, Köhler math transformations, base models, and meta-regressor—is compiled into an optimized, self-contained joblib binary ready for instant serverless execution.",
         COLOR_BLUE_PRIMARY),
        ("2. Asynchronous REST API (FastAPI)",
         "Exposes high-throughput POST /calibrate and /batch-calibrate endpoints with sub-10ms response latency, Pydantic input schemas, and comprehensive Swagger documentation.",
         COLOR_GREEN_EMERALD),
        ("3. Containerized Microservice (Docker)",
         "Packaged as a lightweight Docker container deployable on cloud or local server with automated health probes, zero single point of failure (SPOF), and US EPA Air Quality Index (AQI) calculations.",
         COLOR_GOLD_ACCENT),
        ("4. AirSense V2 Live Atmospheric Dashboard",
         "Interactive web portal featuring real-time QuantAQ telemetry ingestion, What-If physics simulator, model benchmarking leaderboard, and RAG conversational intelligence.",
         COLOR_NAVY_BANNER)
    ]
    
    xs = [Inches(0.8), Inches(6.7)]
    ys = [Inches(1.75), Inches(4.25)]
    w = Inches(5.7)
    h = Inches(2.35)
    
    for idx, (title, desc, color) in enumerate(components):
        x = xs[idx % 2]
        y = ys[idx // 2]
        
        add_card(slide, x, y, w, h, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER)
        create_shape(slide, MSO_SHAPE.RECTANGLE, x, y, Inches(0.12), h, fill_color=color, border_color=None)
        
        tb = slide.shapes.add_textbox(x + Inches(0.3), y + Inches(0.2), w - Inches(0.45), h - Inches(0.35))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(13.5)
        p_t.font.bold = True
        p_t.font.color.rgb = color
        p_t.space_after = Pt(6)
        
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_19(prs, layout):
    """Slide 19: Summary of Core Research Contributions."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "05 | CONCLUSION", "Summary of Core Research Contributions")
    add_footer(slide, 19)
    
    contribs = [
        ("1. Multi-Gamma Köhler Physics Formulation",
         "First calibration framework to integrate parameterized multi-gamma hygroscopic growth curves, resolving exponential moisture swelling in Sub-Saharan Africa without hardware driers."),
        ("2. Elimination of Overfitting in Sensor Calibration",
         "Demonstrated that 5-Fold out-of-fold cross-validation stacking eliminates the 40% overfitting drop seen in traditional neural networks and stand-alone decision trees (ΔR² = -0.0002)."),
        ("3. Multi-Season Field Validation at Afri-SET",
         "Conducted comprehensive co-location evaluation spanning both maritime monsoon humidity and Saharan Harmattan mineral dust at the University of Ghana, proving robust multi-season generalization."),
        ("4. Open-Source Deployment-Ready Artifacts",
         "Delivered an open, reproducible, containerized software stack (FastAPI, Docker, AirSense Web Dashboard) enabling immediate municipal environmental surveillance across African cities.")
    ]
    
    top_y = 1.75
    card_h = 1.05
    gap = 0.16
    
    for i, (title, desc) in enumerate(contribs):
        curr_y = top_y + i * (card_h + gap)
        add_card(slide, Inches(0.8), Inches(curr_y), Inches(11.7), Inches(card_h),
                 bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER)
        create_shape(slide, MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(curr_y), Inches(0.12), Inches(card_h),
                     fill_color=COLOR_BLUE_PRIMARY, border_color=None)
                     
        tb = slide.shapes.add_textbox(Inches(1.15), Inches(curr_y + 0.12), Inches(11.1), Inches(card_h - 0.24))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_BLUE_PRIMARY
        p_t.space_after = Pt(3)
        
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_20(prs, layout):
    """Slide 20: Study Limitations & Future Research Roadmap."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "05 | CONCLUSION", "Study Limitations & Future Research Roadmap")
    add_footer(slide, 20)
    
    # Left Card: Study Limitations
    add_card(slide, Inches(0.8), Inches(1.75), Inches(5.7), Inches(4.85))
    create_shape(slide, MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.75), Inches(5.7), Inches(0.12),
                 fill_color=COLOR_RED_ROSE, border_color=None)
                 
    tb_lim = slide.shapes.add_textbox(Inches(1.05), Inches(2.0), Inches(5.2), Inches(4.45))
    tf_lim = tb_lim.text_frame
    tf_lim.word_wrap = True
    
    p_l = tf_lim.paragraphs[0]
    p_l.text = "Study Limitations"
    p_l.font.name = FONT_HEADING
    p_l.font.size = Pt(15)
    p_l.font.bold = True
    p_l.font.color.rgb = COLOR_RED_ROSE
    p_l.space_after = Pt(10)
    
    bullets_lim = [
        ("1. Single Co-location Node:", "Evaluation was conducted at the Afri-SET platform in Legon; spatial transferability across heterogeneous urban microclimates requires multi-site verification."),
        ("2. Reference Instrument Dependency:", "Supervised calibration models require periodic co-location training periods with gold-standard monitors before independent deployment."),
        ("3. Long-Term Sensor Aging:", "Physical degradation of laser diodes and optical chambers over multi-year periods requires drift tracking and periodic recalibration."),
        ("4. Ultra-Fine Particle Invisibility:", "Optical particle counters cannot detect particles smaller than 0.35 µm, relying on proxy sizing ratios.")
    ]
    add_bullet_list(tf_lim, bullets_lim, font_size=Pt(11.5), space_after=Pt(8))
    
    # Right Card: Future Roadmap
    add_card(slide, Inches(6.7), Inches(1.75), Inches(5.7), Inches(4.85))
    create_shape(slide, MSO_SHAPE.RECTANGLE, Inches(6.7), Inches(1.75), Inches(5.7), Inches(0.12),
                 fill_color=COLOR_GREEN_EMERALD, border_color=None)
                 
    tb_fut = slide.shapes.add_textbox(Inches(6.95), Inches(2.0), Inches(5.2), Inches(4.45))
    tf_fut = tb_fut.text_frame
    tf_fut.word_wrap = True
    
    p_f = tf_fut.paragraphs[0]
    p_f.text = "Future Research Roadmap"
    p_f.font.name = FONT_HEADING
    p_f.font.size = Pt(15)
    p_f.font.bold = True
    p_f.font.color.rgb = COLOR_GREEN_EMERALD
    p_f.space_after = Pt(10)
    
    bullets_fut = [
        ("1. Multi-City Sensor Mesh Transfer:", "Deploying calibrated sensor nodes across Accra, Kumasi, and Tamale to evaluate spatial domain adaptation and transfer learning."),
        ("2. Edge Microcontroller Inference:", "Quantizing the SPIME v4 ensemble for embedded C++ execution directly on ESP32 or Raspberry Pi microcontrollers for zero-latency local calibration."),
        ("3. Satellite & Reanalysis Data Fusion:", "Fusing ground-level low-cost sensor meshes with Sentinel-5P satellite aerosol optical depth (AOD) and ERA5 meteorological models."),
        ("4. Mobile Vehicular Sensing:", "Mounting calibrated nodes on public transit vehicles (trotros) for hyper-local street-level air pollution mapping.")
    ]
    add_bullet_list(tf_fut, bullets_fut, font_size=Pt(11.5), space_after=Pt(8))

    return slide

def build_slide_21(prs, layout):
    """Slide 21: Conclusion & Strategic Takeaways."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "05 | CONCLUSION", "Conclusion & Strategic Takeaways")
    add_footer(slide, 21)
    
    takeaways = [
        ("1. The Hardware Gap is Bridged",
         "Low-cost optical particle counters, when coupled with physics-informed machine learning (SPIME v4), achieve regulatory-grade holdout accuracy (R² = 0.9632, MAE = 0.61 µg/m³), matching $30,000 reference monitors at 1% of the capital cost.",
         COLOR_BLUE_PRIMARY),
        ("2. Physics Guidance Eliminates Overfitting",
         "Integrating thermodynamic moisture formulations and empirical Köhler growth curves prevents machine learning models from memorizing microclimate noise, delivering robust multi-season generalization without accuracy degradation (ΔR² = -0.0002).",
         COLOR_GREEN_EMERALD),
        ("3. Democratized Environmental Surveillance for Africa",
         "This research provides a scalable, open-source, reproducible framework that enables Sub-Saharan municipalities to establish dense ambient air quality networks without multi-million-dollar capital budgets, empowering data-driven public health intervention.",
         COLOR_NAVY_BANNER)
    ]
    
    top_y = 1.75
    card_h = 1.45
    gap = 0.20
    
    for i, (title, desc, color) in enumerate(takeaways):
        curr_y = top_y + i * (card_h + gap)
        add_card(slide, Inches(0.8), Inches(curr_y), Inches(11.7), Inches(card_h),
                 bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER)
        create_shape(slide, MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(curr_y), Inches(0.12), Inches(card_h),
                     fill_color=color, border_color=None)
                     
        tb = slide.shapes.add_textbox(Inches(1.15), Inches(curr_y + 0.15), Inches(11.1), Inches(card_h - 0.30))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(14)
        p_t.font.bold = True
        p_t.font.color.rgb = color
        p_t.space_after = Pt(4)
        
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(11.5)
        p_d.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_22(prs, layout):
    """Slide 22: Closing Slide (Official UG Navy & Crest Title Background)."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    set_title_slide_background(slide, get_template_image2())
    
    # Header Banner in navy area
    tb_inst = slide.shapes.add_textbox(Inches(1.0), Inches(0.45), Inches(11.33), Inches(0.65))
    tf_inst = tb_inst.text_frame
    p1 = tf_inst.paragraphs[0]
    p1.text = "UNIVERSITY OF GHANA  •  DEPARTMENT OF COMPUTER SCIENCE"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_GOLD_ACCENT
    p1.alignment = PP_ALIGN.CENTER
    
    # Title
    tb_title = slide.shapes.add_textbox(Inches(1.0), Inches(1.15), Inches(11.33), Inches(1.0))
    tf_title = tb_title.text_frame
    p_t = tf_title.paragraphs[0]
    p_t.text = "THANK YOU FOR YOUR ATTENTION"
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(28)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_WHITE
    p_t.alignment = PP_ALIGN.CENTER
    
    # Subtitle
    tb_sub = slide.shapes.add_textbox(Inches(1.0), Inches(2.25), Inches(11.33), Inches(0.55))
    tf_sub = tb_sub.text_frame
    p_s = tf_sub.paragraphs[0]
    p_s.text = "Questions, Critiques & Committee Discussion"
    p_s.font.name = FONT_BODY
    p_s.font.size = Pt(17)
    p_s.font.bold = True
    p_s.font.color.rgb = COLOR_GOLD_LIGHT
    p_s.alignment = PP_ALIGN.CENTER
    
    # Project Summary Card in navy area
    add_card(slide, Inches(2.0), Inches(3.05), Inches(9.33), Inches(2.65),
             bg_color=RGBColor(17, 31, 53), border_color=RGBColor(59, 130, 246))
             
    tb_card = slide.shapes.add_textbox(Inches(2.3), Inches(3.2), Inches(8.73), Inches(2.35))
    tf_card = tb_card.text_frame
    tf_card.word_wrap = True
    
    p_c_lbl = tf_card.paragraphs[0]
    p_c_lbl.text = "PROJECT METADATA & REPOSITORY ARCHIVE"
    p_c_lbl.font.name = FONT_HEADING
    p_c_lbl.font.size = Pt(11)
    p_c_lbl.font.bold = True
    p_c_lbl.font.color.rgb = COLOR_GOLD_ACCENT
    p_c_lbl.space_after = Pt(8)
    
    bullets = [
        ("Research Title:", "SPIME: A Stacked Physics-Informed Meta-Ensemble for Low-Cost PM2.5 Sensor Calibration"),
        ("Candidate:", "Neal Allison Hughes (Student ID: 11178252)"),
        ("Principal Supervisor:", "Prof. Isaac Wiafe (Department of Computer Science)"),
        ("Live Web Application:", "https://afri-airsense.netlify.app"),
        ("Open-Source Codebase:", "github.com/hughes-allison/Modulair-PM-Calibration")
    ]
    add_bullet_list(tf_card, bullets, font_size=Pt(12), space_after=Pt(5))

    return slide

# ════════════════════════════════════════════════════════════════════════════════
# MAIN GENERATOR FUNCTION
# ════════════════════════════════════════════════════════════════════════════════

def generate_presentation():
    template_path = 'UG SLIDE TEMPLATE.pptx'
    if not os.path.exists(template_path):
        print(f"[-] Template not found at: {template_path}")
        return False
        
    print(f"[*] Loading official University of Ghana template: {template_path}")
    prs = Presentation(template_path)
    
    # The UG branded master is slide_masters[1]
    ug_master = prs.slide_masters[1]
    title_layout = ug_master.slide_layouts[0]     # image2.jpeg background
    content_layout = ug_master.slide_layouts[1]   # image1.jpeg background
    
    print("[*] Generating 22 academic defense slides...")
    
    build_slide_1(prs, title_layout)
    build_slide_2(prs, content_layout)
    build_slide_3(prs, content_layout)
    build_slide_4(prs, content_layout)
    build_slide_5(prs, content_layout)
    build_slide_6(prs, content_layout)
    build_slide_7(prs, content_layout)
    build_slide_8(prs, content_layout)
    build_slide_9(prs, content_layout)
    build_slide_10(prs, content_layout)
    build_slide_11(prs, content_layout)
    build_slide_12(prs, content_layout)
    build_slide_13(prs, content_layout)
    build_slide_14(prs, content_layout)
    build_slide_15(prs, content_layout)
    build_slide_16(prs, content_layout)
    build_slide_17(prs, content_layout)
    build_slide_18(prs, content_layout)
    build_slide_19(prs, content_layout)
    build_slide_20(prs, content_layout)
    build_slide_21(prs, content_layout)
    build_slide_22(prs, title_layout)
    
    print("[*] Removing 8 initial placeholder template slides...")
    for _ in range(8):
        rId = prs.slides._sldIdLst[0]
        prs.part.drop_rel(rId.rId)
        del prs.slides._sldIdLst[0]
        
    output_dir = 'Defense_Presentation'
    os.makedirs(output_dir, exist_ok=True)
    
    out_ug_template = os.path.join(output_dir, '11178252_HUGHES_NEAL_ALLISON_Project_Defense_UG_Template.pptx')
    out_main = os.path.join(output_dir, '11178252_HUGHES_NEAL_ALLISON_Project_Defense.pptx')
    
    prs.save(out_ug_template)
    print(f"[+] Saved: {out_ug_template}")
    
    prs.save(out_main)
    print(f"[+] Overwrote: {out_main}")
    
    print(f"\n[SUCCESS] Successfully built {len(prs.slides)} slides using 'UG SLIDE TEMPLATE.pptx'!")
    return True

if __name__ == '__main__':
    generate_presentation()
