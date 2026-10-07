"""
Build script to generate the streamlined, 15-minute University of Ghana Project Defense presentation
using 'UG SLIDE TEMPLATE.pptx' as the template.

12 Slides Total — Optimized for a 15-minute defense (1:15 per slide).
Keeps ONLY what is necessary: Problem -> Aim/Objectives -> Data/Site -> Physics Features -> SPIME Architecture
-> Results (Table 4.1) -> Overfitting & Parity -> Seasonal & Attribution -> System -> Contributions -> Q&A.

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

# Color Palette Constants (Official UG Academic Identity)
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
TOTAL_SLIDES = 12

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
    p_title.font.size = Pt(19.5)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_WHITE

def add_footer(slide, slide_num, total_slides=TOTAL_SLIDES):
    """Adds standard slide footer avoiding the bottom-right UG crest."""
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(6.85), Inches(8.8), Inches(0.35))
    tf = tb.text_frame
    tf.word_wrap = False
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0)
    
    p = tf.paragraphs[0]
    p.text = f"Department of Computer Science • University of Ghana  |  B.Sc. Project Defense  |  Slide {slide_num} of {total_slides}"
    p.font.name = FONT_BODY
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_TEXT_LIGHT

def add_card(slide, left, top, width, height, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER, border_width=Pt(1)):
    """Draws a clean content card with optional outline."""
    return create_shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height, bg_color, border_color, border_width)

def add_metric_card(slide, left, top, width, height, value, label, sublabel="", val_color=COLOR_BLUE_PRIMARY):
    """Draws a KPI metric card with large bold numbers."""
    add_card(slide, left, top, width, height, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER)
    
    tb = slide.shapes.add_textbox(left + Inches(0.12), top + Inches(0.10), width - Inches(0.24), height - Inches(0.20))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0)
    
    p_val = tf.paragraphs[0]
    p_val.text = value
    p_val.font.name = FONT_HEADING
    p_val.font.size = Pt(19)
    p_val.font.bold = True
    p_val.font.color.rgb = val_color
    p_val.alignment = PP_ALIGN.CENTER
    
    p_lbl = tf.add_paragraph()
    p_lbl.text = label.upper()
    p_lbl.font.name = FONT_HEADING
    p_lbl.font.size = Pt(10)
    p_lbl.font.bold = True
    p_lbl.font.color.rgb = COLOR_TEXT_DARK
    p_lbl.alignment = PP_ALIGN.CENTER
    p_lbl.space_before = Pt(2)
    
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
# 12 STREAMLINED SLIDES FOR A 15-MINUTE DEFENSE
# ════════════════════════════════════════════════════════════════════════════════

def build_slide_1(prs, layout):
    """Slide 1: Title Slide (Official UG Navy & Crest Title Background)."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    set_title_slide_background(slide, get_template_image2())
    
    # Header Banner text in upper navy area
    tb_inst = slide.shapes.add_textbox(Inches(1.0), Inches(0.35), Inches(11.33), Inches(0.40))
    tf_inst = tb_inst.text_frame
    tf_inst.word_wrap = True
    p1 = tf_inst.paragraphs[0]
    p1.text = "COLLEGE OF BASIC AND APPLIED SCIENCES  •  DEPARTMENT OF COMPUTER SCIENCE"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(12)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_GOLD_ACCENT
    p1.alignment = PP_ALIGN.CENTER
    
    tb_def = slide.shapes.add_textbox(Inches(1.0), Inches(0.75), Inches(11.33), Inches(0.45))
    tf_def = tb_def.text_frame
    p_d = tf_def.paragraphs[0]
    p_d.text = "FINAL YEAR PROJECT DEFENSE & ORAL EXAMINATION"
    p_d.font.name = FONT_HEADING
    p_d.font.size = Pt(15.5)
    p_d.font.bold = True
    p_d.font.color.rgb = COLOR_WHITE
    p_d.alignment = PP_ALIGN.CENTER
    
    # Project Title in light background area
    tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(1.60), Inches(11.73), Inches(1.35))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    p_t = tf_title.paragraphs[0]
    p_t.text = "SPIME: A Stacked Physics-Informed Meta-Ensemble for Low-Cost PM2.5 Sensor Calibration Under High Humidity and Harmattan Dust in Sub-Saharan Africa"
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(21)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_NAVY_BANNER
    p_t.alignment = PP_ALIGN.CENTER
    
    # Subtitle / Examination Tag
    tb_sub = slide.shapes.add_textbox(Inches(1.0), Inches(3.05), Inches(11.33), Inches(0.45))
    tf_sub = tb_sub.text_frame
    p_s = tf_sub.paragraphs[0]
    p_s.text = "B.Sc. Computer Science (Honours)  •  Academic Year 2025/2026"
    p_s.font.name = FONT_BODY
    p_s.font.size = Pt(13.5)
    p_s.font.bold = True
    p_s.font.color.rgb = COLOR_GOLD_LIGHT
    p_s.alignment = PP_ALIGN.CENTER
    
    # Left Card: Candidate Details (White Card, High Contrast)
    add_card(slide, Inches(1.2), Inches(3.60), Inches(5.2), Inches(2.25),
             bg_color=COLOR_CARD_BG, border_color=COLOR_NAVY_BANNER, border_width=Pt(1.5))
    create_shape(slide, MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(3.60), Inches(5.2), Inches(0.08),
                 fill_color=COLOR_NAVY_BANNER, border_color=None)
    tb_cand = slide.shapes.add_textbox(Inches(1.45), Inches(3.80), Inches(4.7), Inches(1.95))
    tf_cand = tb_cand.text_frame
    tf_cand.word_wrap = True
    p_c_hdr = tf_cand.paragraphs[0]
    p_c_hdr.text = "CANDIDATE DETAILS"
    p_c_hdr.font.name = FONT_HEADING
    p_c_hdr.font.size = Pt(11.5)
    p_c_hdr.font.bold = True
    p_c_hdr.font.color.rgb = COLOR_BLUE_PRIMARY
    p_c_hdr.space_after = Pt(6)
    add_bullet_list(tf_cand, [
        ("Candidate Name:", "Neal Allison Hughes"),
        ("Student ID:", "11178252"),
        ("Degree Programme:", "B.Sc. Computer Science (Honours)")
    ], font_size=Pt(12), space_after=Pt(5))
    
    # Right Card: Supervisory Details (White Card, High Contrast)
    add_card(slide, Inches(6.9), Inches(3.60), Inches(5.2), Inches(2.25),
             bg_color=COLOR_CARD_BG, border_color=COLOR_NAVY_BANNER, border_width=Pt(1.5))
    create_shape(slide, MSO_SHAPE.RECTANGLE, Inches(6.9), Inches(3.60), Inches(5.2), Inches(0.08),
                 fill_color=COLOR_GOLD_ACCENT, border_color=None)
    tb_sup = slide.shapes.add_textbox(Inches(7.15), Inches(3.80), Inches(4.7), Inches(1.95))
    tf_sup = tb_sup.text_frame
    tf_sup.word_wrap = True
    p_s_hdr = tf_sup.paragraphs[0]
    p_s_hdr.text = "SUPERVISION & RESEARCH PLATFORM"
    p_s_hdr.font.name = FONT_HEADING
    p_s_hdr.font.size = Pt(11.5)
    p_s_hdr.font.bold = True
    p_s_hdr.font.color.rgb = COLOR_BLUE_PRIMARY
    p_s_hdr.space_after = Pt(6)
    add_bullet_list(tf_sup, [
        ("Principal Supervisor:", "Prof. Isaac Wiafe"),
        ("Academic Unit:", "Department of Computer Science"),
        ("Evaluation Platform:", "Afri-SET Facility, Dept. of Physics"),
        ("Defense Session:", "October 2026")
    ], font_size=Pt(11.5), space_after=Pt(4))
    
    return slide

def build_slide_2(prs, layout):
    """Slide 2: Background & The Monitoring Problem."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "01 | INTRODUCTION & MOTIVATION", "Background: Ambient Air Quality Crisis & Low-Cost Optical Sensor Failure")
    add_footer(slide, 2)
    
    cards = [
        ("1. Severe Monitoring Void in SSA",
         "• Fine particulate matter (PM2.5) causes >1.1 million premature deaths annually across Africa.\n"
         "• Reference-grade FEM monitors (e.g., Teledyne T640) cost >$30,000 USD with prohibitive maintenance, leaving African cities critically unmonitored.\n"
         "• Low-cost Optical Particle Counters (OPCs, ~$2,000) enable dense network expansion but suffer extreme environmental degradation.",
         COLOR_RED_ROSE),
        ("2. Physical Mechanisms of Sensor Breakdown",
         "• Monsoon Deliquescent Swelling: At ambient RH > 80%, inorganic aerosols absorb water vapor and swell optically, causing mass overestimation by up to 300%.\n"
         "• Saharan Harmattan Dust Plumes: During dry months (RH < 25%), coarse non-spherical mineral dust drastically shifts refractive index and optical scattering cross-sections.\n"
         "• Fixed factory calibration curves assume dry, spherical particles, collapsing in tropical extremes.",
         COLOR_GOLD_LIGHT),
        ("3. The Raw Sensor Reality (Afri-SET Baseline)",
         "• Co-located baseline assessment between QuantAQ Modulair-PM and US EPA FEM Teledyne T640 in Accra reveals complete factory failure:\n"
         "   - Predictive R² = -0.0133 (worse than the empirical mean benchmark)\n"
         "   - Mean Absolute Error (MAE) = 5.30 µg/m³\n"
         "   - Severe systematic baseline underestimation (Bias = -5.00 µg/m³)\n"
         "• Without robust calibration, low-cost sensor data is scientifically unusable.",
         COLOR_BLUE_PRIMARY)
    ]
    
    card_w = Inches(3.7)
    card_h = Inches(4.85)
    xs = [Inches(0.8), Inches(4.8), Inches(8.8)]
    
    for i, (title, text, color) in enumerate(cards):
        x = xs[i]
        add_card(slide, x, Inches(1.75), card_w, card_h, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER)
        create_shape(slide, MSO_SHAPE.RECTANGLE, x, Inches(1.75), card_w, Inches(0.10), fill_color=color, border_color=None)
        
        tb = slide.shapes.add_textbox(x + Inches(0.2), Inches(1.95), card_w - Inches(0.4), card_h - Inches(0.35))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = color
        p_t.space_after = Pt(8)
        
        for line in text.split('\n'):
            if line.strip():
                p = tf.add_paragraph()
                p.text = line.strip()
                p.font.name = FONT_BODY
                p.font.size = Pt(11)
                p.font.color.rgb = COLOR_TEXT_DARK if "Predictive R²" in line or "5.30" in line else COLOR_TEXT_MUTED
                p.font.bold = True if ("R² = -0.0133" in line or "MAE = 5.30" in line) else False
                p.space_after = Pt(4)

    return slide

def build_slide_3(prs, layout):
    """Slide 3: Research Aim & Specific Measurable Objectives."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "02 | OBJECTIVES", "Research Aim & Outcome-Based Measurable Objectives")
    add_footer(slide, 3)
    
    # Primary Research Aim Banner
    add_card(slide, Inches(0.8), Inches(1.75), Inches(11.7), Inches(1.20),
             bg_color=COLOR_NAVY_BANNER, border_color=COLOR_GOLD_ACCENT)
    tb_aim = slide.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(11.2), Inches(1.00))
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
    p_a_txt.text = "To design, empirically evaluate, and deploy a Stacked Physics-Informed Meta-Ensemble (SPIME) calibration framework that elevates raw optical measurements from the QuantAQ Modulair-PM to regulatory reference-grade PM2.5 accuracy across contrasting tropical monsoon and Harmattan dust seasons in Accra, Ghana."
    p_a_txt.font.name = FONT_BODY
    p_a_txt.font.size = Pt(12)
    p_a_txt.font.color.rgb = COLOR_WHITE
    
    # 4 Specific Objectives
    objs = [
        ("Objective 1: Co-location Benchmark & Baseline Quantification",
         "Establish an empirically validated co-location benchmark of 8,760 hourly records between the QuantAQ Modulair-PM and US EPA FEM Teledyne T640 at Afri-SET, quantifying baseline sensor collapse (uncalibrated R² = -0.0133, MAE = 5.30 µg/m³).",
         COLOR_BLUE_PRIMARY),
        ("Objective 2: Physics-Informed Hygroscopic Feature Formulation",
         "Engineer a 75-dimensional feature space integrating multi-gamma empirical Köhler growth equations (γ ∈ [0.05, 0.50]), thermodynamic moisture decoupling (VPD, AH, Dew Point), and Harmattan dust indicators, demonstrating >20% predictive attribution to Köhler physics.",
         COLOR_GOLD_LIGHT),
        ("Objective 3: Superior Out-of-Sample Calibration Performance",
         "Develop and benchmark the SPIME architecture against standard baselines (MLR, MoE, Deep MLP, Random Forest), achieving holdout R² ≥ 0.95, MAE ≤ 1.0 µg/m³, RMSE ≤ 1.5 µg/m³, and near-zero systematic bias (|bias| ≤ 0.10 µg/m³).",
         COLOR_GREEN_EMERALD),
        ("Objective 4: Overfitting Mitigation & Operational Deployment",
         "Restrict the cross-validation to holdout generalization gap to ΔR² < 0.02 through out-of-fold cross-validated stacking, and package the pipeline into an operational web-enabled calibration platform.",
         COLOR_NAVY_BANNER)
    ]
    
    top_y = 3.10
    card_h = 0.82
    gap = 0.10
    
    for i, (title, desc, color) in enumerate(objs):
        curr_y = top_y + i * (card_h + gap)
        add_card(slide, Inches(0.8), Inches(curr_y), Inches(11.7), Inches(card_h),
                 bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER)
        create_shape(slide, MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(curr_y), Inches(0.10), Inches(card_h),
                     fill_color=color, border_color=None)
        
        tb = slide.shapes.add_textbox(Inches(1.05), Inches(curr_y + 0.08), Inches(11.2), Inches(card_h - 0.16))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = color
        
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_4(prs, layout):
    """Slide 4: Experimental Co-location & Chronological Partitioning."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "03 | METHODOLOGY & DATA", "Experimental Co-location Setup & Chronological Data Partitioning")
    add_footer(slide, 4)
    
    # Left Card: Co-location Setup
    add_card(slide, Inches(0.8), Inches(1.75), Inches(5.6), Inches(4.85))
    tb_left = slide.shapes.add_textbox(Inches(1.05), Inches(1.95), Inches(5.1), Inches(4.45))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True
    
    p = tf_left.paragraphs[0]
    p.text = "Afri-SET Co-location Infrastructure"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_PRIMARY
    p.space_after = Pt(8)
    
    bullets = [
        ("Co-location Hub:", "African Sensor Evaluation and Training (Afri-SET) facility, Department of Physics, University of Ghana, Legon (5.6506° N, 0.1870° W, 98 m ASL)."),
        ("Low-Cost OPC Monitor:", "QuantAQ Modulair-PM (MOD-PM-01068) equipped with Alphasense OPC-N3 (24 size bins: 0.35 to 40 µm, sample T, RH, pressure)."),
        ("Reference Benchmark:", "US EPA Federal Equivalent Method (FEM) Teledyne API T640 broadband optical spectrometer (±0.5 µg/m³ accuracy)."),
        ("Continuous Timeline:", "8,760 synchronized hourly records across two complete annual meteorological cycles (January 1, 2024 to December 31, 2025).")
    ]
    add_bullet_list(tf_left, bullets, font_size=Pt(11), space_after=Pt(6))
    
    # Right Card: Chronological Partitioning Scheme
    add_card(slide, Inches(6.7), Inches(1.75), Inches(5.8), Inches(4.85))
    tb_right = slide.shapes.add_textbox(Inches(6.95), Inches(1.95), Inches(5.3), Inches(4.45))
    tf_right = tb_right.text_frame
    tf_right.word_wrap = True
    
    p_r = tf_right.paragraphs[0]
    p_r.text = "Strict Chronological Data Quarantine"
    p_r.font.name = FONT_HEADING
    p_r.font.size = Pt(14)
    p_r.font.bold = True
    p_r.font.color.rgb = COLOR_NAVY_BANNER
    p_r.space_after = Pt(8)
    
    right_bullets = [
        ("Training & Validation Partition (60%):", "5,292 hourly records (Jan 1, 2024 to Jun 20, 2025). Dedicated exclusively to exploratory analysis, physics feature derivation, base estimator training, and internal 5-fold cross-validation."),
        ("Quarantined Out-of-Sample Holdout (40%):", "3,468 continuous hourly records (Jun 21, 2025 to Dec 31, 2025). Strictly locked during all model tuning to serve as final unbiased ground truth."),
        ("Seasonal Representation:", "Holdout captures both extreme seasons: Monsoon Wet (2,208 hrs, RH 78–96%) and Harmattan Dry Dust Plumes (1,260 hrs, RH 22–55%)."),
        ("Strict Leakage Prevention:", "Random train/test shuffling strictly prohibited to prevent temporal autocorrelation leakage across consecutive hours.")
    ]
    add_bullet_list(tf_right, right_bullets, font_size=Pt(11), space_after=Pt(6))

    return slide

def build_slide_5(prs, layout):
    """Slide 5: Physics-Informed Feature Engineering."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "03 | METHODOLOGY & FEATURES", "75-Dimensional Physics-Informed Atmospheric Feature Pipeline")
    add_footer(slide, 5)
    
    features = [
        ("1. Multi-Gamma Empirical Köhler Growth (12 Features)",
         "• Explicitly models hygroscopic diameter swelling and deliquescence phase shifts:\n"
         "   f(RH) = 1 + a · [(RH / 100) / (1 - RH / 100)]^γ\n"
         "• Evaluated across 10 empirical exponents γ ∈ [0.05, 0.50] to capture variable chemical composition (pure sulfates to mixed organic particles).\n"
         "• Deliquescence surge indicator (deliquescence_surge) captures abrupt step-function scattering surges when ambient RH exceeds 75%–80%.",
         COLOR_BLUE_PRIMARY),
        ("2. Thermodynamic Moisture Decoupling (18 Features)",
         "• Decouples temperature-dependent moisture effects from true particle mass:\n"
         "• Vapor Pressure Deficit (VPD): Quantifies atmospheric drying capacity (kPa).\n"
         "• Absolute Humidity (AH): Actual water vapor mass per unit volume (g/m³).\n"
         "• Dew Point Depression (T - Td): Proximity to water saturation and fog condensation.\n"
         "• Prevents models from conflating pure water vapor density with suspended aerosol mass.",
         COLOR_GOLD_LIGHT),
        ("3. Harmattan Mineral Dust Indicators & Temporal Dynamics (45 Features)",
         "• Coarse-to-fine ratio (PM10 / PM2.5) and optical size-bin fraction kinematics to flag incoming Saharan dust plumes.\n"
         "• Binary seasonal indicator (is_harmattan) capturing distinct regional aerosol regimes.\n"
         "• Multi-timescale Exponentially Weighted Moving Averages (EWMA spans: 1h, 3h, 6h, 12h, 24h) to model thermal inertia, sensor hysteresis, and diurnal boundary layer dynamics.",
         COLOR_NAVY_BANNER)
    ]
    
    card_w = Inches(3.7)
    card_h = Inches(4.85)
    xs = [Inches(0.8), Inches(4.8), Inches(8.8)]
    
    for i, (title, text, color) in enumerate(features):
        x = xs[i]
        add_card(slide, x, Inches(1.75), card_w, card_h, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER)
        create_shape(slide, MSO_SHAPE.RECTANGLE, x, Inches(1.75), card_w, Inches(0.10), fill_color=color, border_color=None)
        
        tb = slide.shapes.add_textbox(x + Inches(0.2), Inches(1.95), card_w - Inches(0.4), card_h - Inches(0.35))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = color
        p_t.space_after = Pt(8)
        
        for line in text.split('\n'):
            if line.strip():
                p = tf.add_paragraph()
                p.text = line.strip()
                p.font.name = FONT_BODY
                p.font.size = Pt(11)
                p.font.color.rgb = COLOR_TEXT_MUTED
                p.space_after = Pt(4)

    return slide

def build_slide_6(prs, layout):
    """Slide 6: The SPIME Architecture."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "03 | METHODOLOGY & ARCHITECTURE", "SPIME: Hierarchical Stacking Meta-Ensemble with Out-of-Fold Cross-Validation")
    add_footer(slide, 6)
    
    # Left Card: Base Estimators
    add_card(slide, Inches(0.8), Inches(1.75), Inches(5.6), Inches(4.85))
    tb_left = slide.shapes.add_textbox(Inches(1.05), Inches(1.95), Inches(5.1), Inches(4.45))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True
    
    p = tf_left.paragraphs[0]
    p.text = "Level-0 Diverse Base Learners"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_PRIMARY
    p.space_after = Pt(8)
    
    bullets = [
        ("Random Forest (RF):", "150 bagging trees (max_depth=14) trained on the 75-D physics feature space; captures non-linear interactions while bounding individual tree variance."),
        ("Extra Trees (ET):", "150 extremely randomized trees with randomized cut-point selection; maximizes structural diversity and decorrelates errors from standard RF."),
        ("Gradient Boosting (GBM):", "120 sequential boosting trees (learning_rate=0.05, max_depth=6); focuses gradient descent on hard-to-fit regime transitions."),
        ("Ensemble Diversity Principle:", "Combining bagging and boosting paradigms guarantees uncorrelated residual errors across meteorological extremes.")
    ]
    add_bullet_list(tf_left, bullets, font_size=Pt(11), space_after=Pt(6))
    
    # Right Card: Out-of-Fold Stacking & Meta-Learner
    add_card(slide, Inches(6.7), Inches(1.75), Inches(5.8), Inches(4.85))
    tb_right = slide.shapes.add_textbox(Inches(6.95), Inches(1.95), Inches(5.3), Inches(4.45))
    tf_right = tb_right.text_frame
    tf_right.word_wrap = True
    
    p_r = tf_right.paragraphs[0]
    p_r.text = "Level-1 Meta-Learner & Anti-Leakage Stacking"
    p_r.font.name = FONT_HEADING
    p_r.font.size = Pt(14)
    p_r.font.bold = True
    p_r.font.color.rgb = COLOR_NAVY_BANNER
    p_r.space_after = Pt(8)
    
    right_bullets = [
        ("5-Fold Out-of-Fold (OOF) Stacking:", "The internal training split is partitioned into 5 chronological folds. Base learners generate predictions exclusively on unobserved validation folds."),
        ("Zero Meta-Learner Leakage:", "The Level-1 meta-learner is trained strictly on out-of-fold predictions, ensuring it never observes in-sample training bias."),
        ("Constrained Meta-Regressor:", "L2-regularized Ridge Regression (α = 10.0) with non-negative weight projection prevents collinear weight explosion:"),
        ("Final Calibrated Estimate:", "y_cal = w0 + w_RF · y_RF + w_ET · y_ET + w_GBM · y_GBM\nEnforces a strict inductive bias that prevents temporal concept drift.")
    ]
    add_bullet_list(tf_right, right_bullets, font_size=Pt(11), space_after=Pt(6))

    return slide

def build_slide_7(prs, layout):
    """Slide 7: Benchmark Calibration Results (Table 4.1)."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "04 | EMPIRICAL RESULTS", "Comparative Calibration Benchmarks on Unseen Holdout Data (3,468 Hours)")
    add_footer(slide, 7)
    
    # 4 Stat KPI Metric Cards
    add_metric_card(slide, Inches(0.8), Inches(1.75), Inches(2.75), Inches(1.15),
                    "R² = 0.9632", "HOLDOUT ACCURACY", "Unseen 3,468-Hr Holdout", COLOR_GREEN_EMERALD)
    add_metric_card(slide, Inches(3.75), Inches(1.75), Inches(2.75), Inches(1.15),
                    "MAE = 0.61 µg/m³", "MEAN ABSOLUTE ERROR", "88.5% Error Reduction", COLOR_BLUE_PRIMARY)
    add_metric_card(slide, Inches(6.70), Inches(1.75), Inches(2.75), Inches(1.15),
                    "RMSE = 1.05 µg/m³", "ROOT MEAN SQ ERROR", "Reference-Grade Precision", COLOR_NAVY_BANNER)
    add_metric_card(slide, Inches(9.65), Inches(1.75), Inches(2.85), Inches(1.15),
                    "Bias = -0.04 µg/m³", "SYSTEMATIC BIAS", "Near-Zero Baseline Drift", COLOR_GOLD_ACCENT)
                    
    # Complete Table 4.1 Comparison Table
    headers = ["Calibration Model Architecture", "5-Fold CV R²", "Holdout Test R²", "MAE (µg/m³)", "RMSE (µg/m³)", "Bias (µg/m³)", "Overfit Gap (ΔR²)"]
    rows = [
        ["Uncalibrated Factory OPC-N3", "N/A", "-0.0133", "5.30", "8.92", "-5.00", "N/A (Failed)"],
        ["Multiple Linear Regression (Baseline)", "0.5723", "0.6760", "2.71", "3.66", "-0.45", "-0.1037 (Underfit)"],
        ["Atmospheric Mixture of Experts (MoE)", "0.5840", "0.3745", "3.98", "5.08", "+2.55", "+0.2095 (High Var)"],
        ["Deep Neural LLM Regressor", "0.6798", "0.4927", "3.27", "4.57", "-1.28", "+0.1871 (Noise Mem)"],
        ["MLP Neural Network Regressor", "0.7177", "0.5170", "3.21", "4.46", "-1.28", "+0.2007 (Overfit)"],
        ["Random Forest Regressor (v2 Best)", "0.9677", "0.8318", "1.81", "2.63", "-0.81", "+0.1359 (Degraded)"],
        ["SPIME Meta-Ensemble [PRIMARY]", "0.9725", "0.9632", "0.61", "1.05", "-0.04", "+0.0093 (0.93%)"]
    ]
    
    table_shape = slide.shapes.add_table(len(rows) + 1, len(headers), Inches(0.8), Inches(3.10), Inches(11.7), Inches(3.45))
    tbl = table_shape.table
    
    col_widths = [Inches(3.3), Inches(1.3), Inches(1.4), Inches(1.3), Inches(1.3), Inches(1.3), Inches(1.8)]
    for idx, w in enumerate(col_widths):
        tbl.columns[idx].width = w
        
    for j, h_text in enumerate(headers):
        cell = tbl.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY_BANNER
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = FONT_HEADING
        p.font.size = Pt(10.5)
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
            p.font.size = Pt(10.5 if not is_champion else 11)
            p.font.bold = is_champion
            p.alignment = PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT
            
            if is_champion:
                p.font.color.rgb = COLOR_GREEN_EMERALD if j in [2, 6] else COLOR_BLUE_PRIMARY
            else:
                p.font.color.rgb = COLOR_RED_ROSE if "Failed" in val or "-0.0133" in val else COLOR_TEXT_DARK

    return slide

def build_slide_8(prs, layout):
    """Slide 8: Overfitting Elimination & Parity Plot (Table 4.2 & Figure 4.1)."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "04 | GENERALIZATION & DIAGNOSTICS", "Overfitting Elimination & 1:1 Parity Alignment with Ground Truth")
    add_footer(slide, 8)
    
    # Left Card: Overfitting Diagnostics
    add_card(slide, Inches(0.8), Inches(1.75), Inches(5.6), Inches(4.85))
    tb_left = slide.shapes.add_textbox(Inches(1.05), Inches(1.95), Inches(5.1), Inches(4.45))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True
    
    p = tf_left.paragraphs[0]
    p.text = "Overfitting Analysis (Table 4.2)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_PRIMARY
    p.space_after = Pt(8)
    
    bullets = [
        ("Deep Neural Collapse (ΔR² = +0.3800):", "MLP achieved Train R² = 0.8970 but collapsed to Holdout R² = 0.5170. Dense layers memorized high-frequency microclimate noise instead of true atmospheric physics."),
        ("Atmospheric MoE Variance (ΔR² = +0.3795):", "MoE dropped from Train R² = 0.7540 to Holdout R² = 0.3745 due to regime-switching boundary instability and sparse cluster support."),
        ("Random Forest Generalization Drop (ΔR² = +0.1413):", "Standalone RF dropped from Train R² = 0.9731 to Holdout R² = 0.8318 as deep decision trees overfit to specific training humidity splits."),
        ("SPIME Overfitting Elimination (ΔR² = +0.0093):", "SPIME achieved 5-Fold CV R² = 0.9725 and Holdout R² = 0.9632. Out-of-fold stacking and L2 regularization suppressed the gap to < 1%!")
    ]
    add_bullet_list(tf_left, bullets, font_size=Pt(11), space_after=Pt(6))
    
    # Right Card: Parity Scatter Plot
    add_card(slide, Inches(6.7), Inches(1.75), Inches(5.8), Inches(4.85))
    img_path = 'Defense_Presentation/extracted_media/image5.png'
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(6.9), Inches(1.95), width=Inches(5.4))
        
    tb_cap = slide.shapes.add_textbox(Inches(6.9), Inches(5.95), Inches(5.4), Inches(0.55))
    tf_cap = tb_cap.text_frame
    tf_cap.word_wrap = True
    p_c = tf_cap.paragraphs[0]
    p_c.text = "Figure 4.1: Reference Teledyne T640 vs. Calibrated SPIME on Holdout Data\nAdheres to 1:1 parity line across 0–150 µg/m³ (Slope m = 0.984, Intercept b = +0.12)."
    p_c.font.name = FONT_BODY
    p_c.font.size = Pt(10)
    p_c.font.color.rgb = COLOR_TEXT_MUTED
    p_c.alignment = PP_ALIGN.CENTER

    return slide

def build_slide_9(prs, layout):
    """Slide 9: Seasonal Robustness & Feature Attribution (Table 4.3 & Figure 4.4)."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "04 | SEASONAL ROBUSTNESS & ATTRIBUTION", "Seasonal Regime Stability & Physics-Guided Feature Attribution")
    add_footer(slide, 9)
    
    # Left Card: Seasonal Breakdown (Table 4.3)
    add_card(slide, Inches(0.8), Inches(1.75), Inches(5.6), Inches(4.85))
    tb_left = slide.shapes.add_textbox(Inches(1.05), Inches(1.95), Inches(5.1), Inches(4.45))
    tf_left = tb_left.text_frame
    tf_left.word_wrap = True
    
    p = tf_left.paragraphs[0]
    p.text = "Cross-Seasonal Holdout Stability (Table 4.3)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_PRIMARY
    p.space_after = Pt(8)
    
    bullets = [
        ("Monsoon Wet Season (N = 2,208 hrs, RH 78–96%):", "• Holdout R² = 0.9684  |  MAE = 0.54 µg/m³\n• RMSE = 1.08 µg/m³  |  Mean Bias = -0.18 µg/m³\n• Zero hygroscopic runaway; moisture-induced optical scattering fully resolved by Köhler terms."),
        ("Harmattan Dry Season (N = 1,260 hrs, RH 22–55%):", "• Holdout R² = 0.9548  |  MAE = 0.73 µg/m³\n• RMSE = 1.46 µg/m³  |  Mean Bias = -0.31 µg/m³\n• High fidelity during heavy Saharan mineral dust plumes without baseline drift or saturation."),
        ("Combined Full Holdout (N = 3,468 hrs):", "• Holdout R² = 0.9632  |  MAE = 0.61 µg/m³  |  RMSE = 1.05 µg/m³\n• Consistent sub-microgram precision across opposing climatic regimes.")
    ]
    add_bullet_list(tf_left, bullets, font_size=Pt(11), space_after=Pt(6))
    
    # Right Card: Feature Importance (Figure 4.4)
    add_card(slide, Inches(6.7), Inches(1.75), Inches(5.8), Inches(4.85))
    img_path = 'Defense_Presentation/extracted_media/image6.png'
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(7.0), Inches(1.95), width=Inches(5.2), height=Inches(3.8))
        
    tb_cap = slide.shapes.add_textbox(Inches(6.9), Inches(5.85), Inches(5.4), Inches(0.65))
    tf_cap = tb_cap.text_frame
    tf_cap.word_wrap = True
    p_c = tf_cap.paragraphs[0]
    p_c.text = "Figure 4.4: Top 20 Physics Feature Importance Rankings\nEmpirical Köhler growth terms account for 20.4% of total predictive power, confirming that embedding atmospheric physical laws directly drove model accuracy."
    p_c.font.name = FONT_BODY
    p_c.font.size = Pt(10)
    p_c.font.color.rgb = COLOR_TEXT_MUTED
    p_c.alignment = PP_ALIGN.CENTER

    return slide

def build_slide_10(prs, layout):
    """Slide 10: Operational Software System & Web Deployment."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "05 | SOFTWARE ARTIFACT", "Operational Software Artifact: Full-Stack Calibration Platform")
    add_footer(slide, 10)
    
    components = [
        ("1. Real-Time Inference Microservice",
         "• Packaged SPIME pipeline executed via containerized Python/Flask/FastAPI microservice.\n"
         "• Sub-15ms inference latency per telemetry record for edge and cloud deployment.\n"
         "• Automated conversion of calibrated mass concentrations into US EPA Air Quality Index (AQI) categories with health advisories.",
         COLOR_BLUE_PRIMARY),
        ("2. Interactive Calibration Dashboard",
         "• Live telemetry streaming from QuantAQ cloud API with SQLite/Mongo dual-layer caching.\n"
         "• Real-time calibrated vs raw sensor time-series tracking and interactive scatter parity diagnostics.\n"
         "• What-If Environmental Simulator allowing operators to simulate high-humidity or Harmattan dust spikes.",
         COLOR_GOLD_LIGHT),
        ("3. Conversational LLM Air Quality Agent",
         "• Integrated RAG-assisted air quality assistant allowing municipal stakeholders to query air quality in natural language:\n"
         "   - 'How is the air quality in Legon right now?'\n"
         "   - 'What was the peak PM2.5 during yesterday's monsoon rain?'\n"
         "• Synthesizes complex atmospheric data into accessible public health guidance.",
         COLOR_NAVY_BANNER)
    ]
    
    card_w = Inches(3.7)
    card_h = Inches(4.85)
    xs = [Inches(0.8), Inches(4.8), Inches(8.8)]
    
    for i, (title, text, color) in enumerate(components):
        x = xs[i]
        add_card(slide, x, Inches(1.75), card_w, card_h, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER)
        create_shape(slide, MSO_SHAPE.RECTANGLE, x, Inches(1.75), card_w, Inches(0.10), fill_color=color, border_color=None)
        
        tb = slide.shapes.add_textbox(x + Inches(0.2), Inches(1.95), card_w - Inches(0.4), card_h - Inches(0.35))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = color
        p_t.space_after = Pt(8)
        
        for line in text.split('\n'):
            if line.strip():
                p = tf.add_paragraph()
                p.text = line.strip()
                p.font.name = FONT_BODY
                p.font.size = Pt(11)
                p.font.color.rgb = COLOR_TEXT_MUTED
                p.space_after = Pt(4)

    return slide

def build_slide_11(prs, layout):
    """Slide 11: Core Research Contributions & Strategic Implications."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    add_header(slide, "05 | CONCLUSION & IMPACT", "Summary of Core Research Contributions & Strategic Implications")
    add_footer(slide, 11)
    
    contribs = [
        ("1. First Co-location Benchmark in Coastal Ghana",
         "Established the first continuous 8,760-hour co-location benchmark of the QuantAQ Modulair-PM against an EPA FEM Teledyne T640 in Ghana, exposing the complete failure of factory calibration (R² = -0.0133).",
         COLOR_RED_ROSE),
        ("2. Physics-Informed Domain Integration",
         "Formulated a 75-D feature pipeline demonstrating that empirical Köhler growth dynamics and thermodynamic moisture parameters account for 20.4% of predictive power, solving humidity distortion where black-box ML failed.",
         COLOR_GOLD_LIGHT),
        ("3. Overfitting Elimination via OOF Stacking",
         "Demonstrated that out-of-fold cross-validated stacking suppresses the temporal generalization gap to ΔR² = 0.0093 (< 1%), resolving the severe overfitting seen in standard tree and neural architectures (ΔR² > 0.14–0.38).",
         COLOR_BLUE_PRIMARY),
        ("4. Low-Cost Regulatory Equivalence & Scalability",
         "Proved that $2,000 low-cost optical sensors calibrated with SPIME achieve near-FEM precision (R² = 0.9632, MAE = 0.61 µg/m³), unlocking cost-effective, high-density air quality monitoring networks across African cities.",
         COLOR_GREEN_EMERALD)
    ]
    
    xs = [Inches(0.8), Inches(6.7)]
    ys = [Inches(1.75), Inches(4.25)]
    w = Inches(5.7)
    h = Inches(2.35)
    
    for idx, (title, desc, color) in enumerate(contribs):
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

def build_slide_12(prs, layout):
    """Slide 12: Closing & Q&A."""
    slide = prs.slides.add_slide(layout)
    clear_slide_placeholders(slide)
    set_title_slide_background(slide, get_template_image2())
    
    # Header Banner text in upper navy area
    tb_inst = slide.shapes.add_textbox(Inches(1.0), Inches(0.35), Inches(11.33), Inches(0.40))
    tf_inst = tb_inst.text_frame
    p1 = tf_inst.paragraphs[0]
    p1.text = "COLLEGE OF BASIC AND APPLIED SCIENCES  •  DEPARTMENT OF COMPUTER SCIENCE"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(12)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_GOLD_ACCENT
    p1.alignment = PP_ALIGN.CENTER
    
    tb_def = slide.shapes.add_textbox(Inches(1.0), Inches(0.75), Inches(11.33), Inches(0.45))
    tf_def = tb_def.text_frame
    p_d = tf_def.paragraphs[0]
    p_d.text = "FINAL YEAR B.SC. PROJECT DEFENSE EXAMINATION"
    p_d.font.name = FONT_HEADING
    p_d.font.size = Pt(15.5)
    p_d.font.bold = True
    p_d.font.color.rgb = COLOR_WHITE
    p_d.alignment = PP_ALIGN.CENTER
    
    # Main Header in light background area
    tb_title = slide.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(11.33), Inches(0.80))
    tf_title = tb_title.text_frame
    p_t = tf_title.paragraphs[0]
    p_t.text = "THANK YOU FOR YOUR ATTENTION"
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(28)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_NAVY_BANNER
    p_t.alignment = PP_ALIGN.CENTER
    
    # Subtitle
    tb_sub = slide.shapes.add_textbox(Inches(1.0), Inches(2.45), Inches(11.33), Inches(0.45))
    tf_sub = tb_sub.text_frame
    p_s = tf_sub.paragraphs[0]
    p_s.text = "Questions, Critiques & Committee Discussion"
    p_s.font.name = FONT_BODY
    p_s.font.size = Pt(16)
    p_s.font.bold = True
    p_s.font.color.rgb = COLOR_GOLD_LIGHT
    p_s.alignment = PP_ALIGN.CENTER
    
    # Centered Details Card (White Card, High Contrast)
    add_card(slide, Inches(2.5), Inches(3.15), Inches(8.3), Inches(2.80),
             bg_color=COLOR_CARD_BG, border_color=COLOR_NAVY_BANNER, border_width=Pt(1.5))
    create_shape(slide, MSO_SHAPE.RECTANGLE, Inches(2.5), Inches(3.15), Inches(8.3), Inches(0.08),
                 fill_color=COLOR_GOLD_ACCENT, border_color=None)
    tb_box = slide.shapes.add_textbox(Inches(2.8), Inches(3.30), Inches(7.7), Inches(2.50))
    tf_box = tb_box.text_frame
    tf_box.word_wrap = True
    
    p_hdr = tf_box.paragraphs[0]
    p_hdr.text = "RESEARCH DEFENSE EXAMINATION"
    p_hdr.font.name = FONT_HEADING
    p_hdr.font.size = Pt(12)
    p_hdr.font.bold = True
    p_hdr.font.color.rgb = COLOR_BLUE_PRIMARY
    p_hdr.alignment = PP_ALIGN.CENTER
    p_hdr.space_after = Pt(8)
    
    details = [
        ("Project:", "SPIME Low-Cost PM2.5 Calibration Framework"),
        ("Candidate:", "Neal Allison Hughes (Student ID: 11178252)"),
        ("Degree Programme:", "B.Sc. Computer Science (Honours)"),
        ("Principal Supervisor:", "Prof. Isaac Wiafe (Department of Computer Science)"),
        ("Evaluation Platform:", "Afri-SET Facility, Department of Physics, University of Ghana, Legon"),
        ("Software Repository:", "github.com/Hughes-Neal/Modulair-PM")
    ]
    add_bullet_list(tf_box, details, font_size=Pt(11.5), space_after=Pt(4))
    
    return slide

# ════════════════════════════════════════════════════════════════════════════════
# MAIN BUILD SCRIPT
# ════════════════════════════════════════════════════════════════════════════════

def main():
    template_path = 'UG SLIDE TEMPLATE.pptx'
    output_concise = os.path.join('Defense_Presentation', '11178252_HUGHES_NEAL_ALLISON_Project_Defense_15Min_Concise.pptx')
    output_main = os.path.join('Defense_Presentation', '11178252_HUGHES_NEAL_ALLISON_Project_Defense.pptx')
    
    print(f"Loading template: {template_path}")
    prs = Presentation(template_path)
    ug_master = prs.slide_masters[1]
    title_layout = ug_master.slide_layouts[0]     # image2.jpeg background
    content_layout = ug_master.slide_layouts[1]   # image1.jpeg background
    
    print("Building 12 streamlined slides for 15-minute defense...")
    
    build_slide_1(prs, title_layout)
    print("  Slide 1: Title Slide (Official UG Template)")
    
    build_slide_2(prs, content_layout)
    print("  Slide 2: Background & The Monitoring Problem")
    
    build_slide_3(prs, content_layout)
    print("  Slide 3: Research Aim & Specific Measurable Objectives")
    
    build_slide_4(prs, content_layout)
    print("  Slide 4: Experimental Co-location & Chronological Partitioning")
    
    build_slide_5(prs, content_layout)
    print("  Slide 5: 75-D Physics-Informed Feature Engineering")
    
    build_slide_6(prs, content_layout)
    print("  Slide 6: The SPIME Stacking Architecture")
    
    build_slide_7(prs, content_layout)
    print("  Slide 7: Benchmark Calibration Results (Table 4.1)")
    
    build_slide_8(prs, content_layout)
    print("  Slide 8: Overfitting Elimination & 1:1 Parity Alignment")
    
    build_slide_9(prs, content_layout)
    print("  Slide 9: Seasonal Robustness & Feature Attribution")
    
    build_slide_10(prs, content_layout)
    print("  Slide 10: Operational Software System & Web Deployment")
    
    build_slide_11(prs, content_layout)
    print("  Slide 11: Core Research Contributions & Impact")
    
    build_slide_12(prs, title_layout)
    print("  Slide 12: Closing & Committee Discussion (Q&A)")
    
    print("Removing 8 initial placeholder template slides...")
    for _ in range(8):
        rId = prs.slides._sldIdLst[0]
        prs.part.drop_rel(rId.rId)
        del prs.slides._sldIdLst[0]
        
    os.makedirs('Defense_Presentation', exist_ok=True)
    
    # Save both files
    prs.save(output_concise)
    print(f"Saved concise presentation: {output_concise} ({os.path.getsize(output_concise):,} bytes)")
    
    prs.save(output_main)
    print(f"Saved main defense presentation: {output_main} ({os.path.getsize(output_main):,} bytes)")
    
    print(f"\n[SUCCESS] Successfully built {len(prs.slides)} slides using official UG template!")

if __name__ == '__main__':
    main()
