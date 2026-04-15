import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import io

# Page configuration
st.set_page_config(
    page_title="HR Data Safety Checker",
    page_icon="🛡️",
    layout="wide"
)

# Title and description
st.title("🛡️ HR Data Safety Checker")
st.markdown("### For SMEs: Identify risks before they become breaches")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    This tool helps HR consultants and SME owners:
    - **Identify** common HR data security gaps
    - **Get** a risk score and actionable recommendations
    - **Download** a professional PDF report for clients
    """)

with col2:
    st.info("**Built for:**\nHR Consultants | SME Owners | People Ops")

st.divider()

# Company information
st.subheader("📋 Company Information")

col1, col2 = st.columns(2)

with col1:
    company_name = st.text_input("Company Name", placeholder="e.g., TechSME Ltd")
    num_employees = st.number_input("Number of Employees", min_value=1, max_value=500, value=20)

with col2:
    industry = st.selectbox("Industry", [
        "Technology", "Retail", "Manufacturing", "Services", 
        "Healthcare", "Education", "Finance", "Other"
    ])
    has_hr_department = st.radio("Has dedicated HR person?", ["No", "Yes - part-time", "Yes - full-time"])

st.divider()

# Security assessment questions
st.subheader("🔍 HR Data Security Assessment")
st.markdown("*Answer these questions honestly to get an accurate risk assessment*")

questions = {
    "data_storage": "Where are employee records stored?",
    "access_control": "Who has access to employee data?",
    "training": "Do employees receive data privacy training?",
    "cv_storage": "How are candidate CVs/applications stored?",
    "device_policy": "Is there a policy for company devices?",
    "offboarding": "Is access revoked immediately when someone leaves?",
    "sharing": "Are HR documents shared via email or WhatsApp?",
    "backup": "Are HR data backups performed regularly?"
}

options = {
    "data_storage": ["Paper files only", "Spreadsheets (Excel)", "HR software/Cloud", "Don't know"],
    "access_control": ["Everyone can access", "Only managers", "Only HR", "No clear policy"],
    "training": ["Never", "Once when hired", "Annually", "Not sure"],
    "cv_storage": ["Shared folder (unrestricted)", "Email inbox only", "ATS/HR system", "Paper only"],
    "device_policy": ["No policy", "Basic password required", "Encryption + passwords", "In development"],
    "offboarding": ["Manually, takes days", "Immediately", "We forget sometimes", "No process"],
    "sharing": ["Often via email/WhatsApp", "Sometimes", "Rarely", "Using secure links"],
    "backup": ["Never", "Sometimes", "Regularly scheduled", "Not sure"]
}

answers = {}
for key, question in questions.items():
    answers[key] = st.selectbox(question, options[key])

st.divider()

# Calculate risk score
def calculate_risk_score(answers, num_employees):
    score = 0
    max_score = 100
    
    # Weighted scoring (lower score = safer)
    risk_weights = {
        "data_storage": {"Paper files only": 30, "Spreadsheets (Excel)": 40, "HR software/Cloud": 10, "Don't know": 50},
        "access_control": {"Everyone can access": 50, "Only managers": 25, "Only HR": 5, "No clear policy": 40},
        "training": {"Never": 45, "Once when hired": 20, "Annually": 10, "Not sure": 30},
        "cv_storage": {"Shared folder (unrestricted)": 40, "Email inbox only": 35, "ATS/HR system": 5, "Paper only": 15},
        "device_policy": {"No policy": 50, "Basic password required": 25, "Encryption + passwords": 5, "In development": 20},
        "offboarding": {"Manually, takes days": 35, "Immediately": 5, "We forget sometimes": 50, "No process": 45},
        "sharing": {"Often via email/WhatsApp": 45, "Sometimes": 30, "Rarely": 15, "Using secure links": 5},
        "backup": {"Never": 50, "Sometimes": 30, "Regularly scheduled": 5, "Not sure": 35}
    }
    
    total_risk = 0
    for key, answer in answers.items():
        total_risk += risk_weights[key].get(answer, 25)
    
    # Average risk score (0-100, higher = more risky)
    raw_score = total_risk / len(answers)
    
    # Adjust for company size (larger companies = more risk if insecure)
    if num_employees > 100:
        raw_score = min(100, raw_score * 1.2)
    elif num_employees > 50:
        raw_score = min(100, raw_score * 1.1)
    
    # Invert so higher score = better (safer)
    safety_score = 100 - raw_score
    
    return round(safety_score, 1)

# Generate recommendations
def generate_recommendations(answers, num_employees):
    recommendations = []
    
    if answers["data_storage"] in ["Spreadsheets (Excel)", "Paper files only"]:
        recommendations.append("🔐 **Move to secure HR software**: Spreadsheets and paper files are high-risk. Consider affordable SME options like BambooHR, Zoho People, or even Google Sheets with strict access controls.")
    
    if answers["access_control"] in ["Everyone can access", "No clear policy"]:
        recommendations.append("👥 **Implement role-based access**: Only HR and relevant managers should see employee data. Start with a simple policy document this week.")
    
    if answers["training"] in ["Never", "Not sure"]:
        recommendations.append("📚 **Run quarterly data privacy training**: 15-minute sessions can prevent 80% of common breaches. Free resources available from ISC2 and NIST.")
    
    if answers["cv_storage"] in ["Shared folder (unrestricted)", "Email inbox only"]:
        recommendations.append("📁 **Secure candidate data**: Create a password-protected folder or use a free ATS like Manatal or Recruitee's free tier.")
    
    if answers["device_policy"] in ["No policy", "In development"]:
        recommendations.append("💻 **Create a BYOD/device policy**: Require passwords, screen locks, and remote wipe capability for company devices.")
    
    if answers["offboarding"] in ["Manually, takes days", "We forget sometimes", "No process"]:
        recommendations.append("🚪 **Automate offboarding access removal**: Create a checklist that triggers immediately upon resignation/termination.")
    
    if answers["sharing"] in ["Often via email/WhatsApp", "Sometimes"]:
        recommendations.append("📧 **Stop sharing sensitive docs via email**: Use Google Drive with link expiration or secure file sharing services like OnionShare or Tresorit.")
    
    if answers["backup"] in ["Never", "Sometimes", "Not sure"]:
        recommendations.append("💾 **Set up automated backups**: Use Google Workspace backup, OneDrive, or a simple cron job to backup HR data weekly.")
    
    # Additional recommendations based on company size
    if num_employees > 50:
        recommendations.append("🏢 **Consider hiring a part-time HR/compliance person**: At 50+ employees, manual processes become unsustainable.")
    
    if num_employees > 20 and answers["training"] == "Once when hired":
        recommendations.append("🔄 **Move to annual refresher training**: Once when hired isn't enough. People forget and new threats emerge.")
    
    if not recommendations:
        recommendations.append("✅ **Great job!** Your HR data practices appear solid. Focus on maintaining regular audits and staying updated on data protection regulations (like Kenya's Data Protection Act).")
    
    return recommendations

# Generate PDF report
def generate_pdf(company_name, num_employees, industry, has_hr_department, safety_score, recommendations):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, spaceAfter=30, textColor=colors.HexColor('#1f77b4'))
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=12, spaceAfter=12, textColor=colors.HexColor('#2c3e50'))
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10, spaceAfter=6)
    
    story = []
    
    # Title
    story.append(Paragraph(f"HR Data Safety Report", title_style))
    story.append(Paragraph(f"Prepared for: {company_name}", normal_style))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", normal_style))
    story.append(Spacer(1, 20))
    
    # Company summary
    story.append(Paragraph("Company Summary", heading_style))
    story.append(Paragraph(f"• Employees: {num_employees}", normal_style))
    story.append(Paragraph(f"• Industry: {industry}", normal_style))
    story.append(Paragraph(f"• HR Structure: {has_hr_department}", normal_style))
    story.append(Spacer(1, 15))
    
    # Risk score
    story.append(Paragraph(f"Safety Score: {safety_score}/100", heading_style))
    if safety_score >= 80:
        risk_level = "Low Risk ✅"
        risk_color = colors.green
    elif safety_score >= 50:
        risk_level = "Medium Risk ⚠️"
        risk_color = colors.orange
    else:
        risk_level = "High Risk 🔴"
        risk_color = colors.red
    
    story.append(Paragraph(f"Risk Level: {risk_level}", normal_style))
    story.append(Spacer(1, 20))
    
    # Recommendations
    story.append(Paragraph("Actionable Recommendations", heading_style))
    for rec in recommendations:
        story.append(Paragraph(f"• {rec}", normal_style))
        story.append(Spacer(1, 6))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph("Generated by HR Data Safety Checker - Empowering SMEs to secure their people data", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Display results
if st.button("🚀 Generate Safety Report", type="primary"):
    if not company_name:
        st.error("Please enter a company name")
    else:
        # Calculate score
        safety_score = calculate_risk_score(answers, num_employees)
        
        # Determine risk level
        if safety_score >= 80:
            risk_level = "🟢 Low Risk"
            color = "green"
        elif safety_score >= 50:
            risk_level = "🟡 Medium Risk"
            color = "orange"
        else:
            risk_level = "🔴 High Risk"
            color = "red"
        
        # Display results
        st.success(f"### Report generated for {company_name}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Safety Score", f"{safety_score}/100")
        with col2:
            st.metric("Risk Level", risk_level)
        with col3:
            st.metric("Employees at risk", num_employees)
        
        # Recommendations
        st.subheader("📋 Actionable Recommendations")
        recommendations = generate_recommendations(answers, num_employees)
        
        for rec in recommendations:
            st.markdown(f"- {rec}")
        
        # PDF Download
        pdf_buffer = generate_pdf(company_name, num_employees, industry, has_hr_department, safety_score, recommendations)
        
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_buffer,
            file_name=f"HR_Safety_Report_{company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
        
        # Export CSV of answers for record keeping
        export_data = {
            "Company": company_name,
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Safety_Score": safety_score,
            **answers
        }
        df = pd.DataFrame([export_data])
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="📊 Download Assessment Data (CSV)",
            data=csv,
            file_name=f"HR_Assessment_{company_name.replace(' ', '_')}.csv",
            mime="text/csv"
        )
        
        st.info("💡 **Pro tip:** Send this report to SME clients as a free audit. It opens the conversation for paid HR system implementation work.")

st.divider()
st.caption("Built for HR Consultants & SMEs | Data Privacy Standards based on Kenya Data Protection Act & ISC2 guidelines")