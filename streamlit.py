import streamlit as st
import json
from datetime import date, datetime
import os
from supabase import create_client
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
import re

# Email validation function
def is_valid_email(email):
    """
    Validate email format using regex
    Returns True if valid, False otherwise
    """
    if not email:  # Empty email
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Stricter pattern that also checks for common TLDs
    strict_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|org|net|edu|gov|mil|biz|info|io|ai|app|dev|co|uk|in|de|fr|jp|au|ca|br|mx|es|it|nl|se|no|dk|fi|pl|cz|hu|gr|pt|at|ch|be|us)$'
    
    return re.match(pattern, email, re.IGNORECASE) is not None

# Email validation with detailed feedback
def validate_email_with_feedback(email):
    """
    Validate email and return (is_valid, error_message)
    """
    if not email:
        return False, "Email address cannot be empty"
    
    if not re.match(r'^[a-zA-Z0-9._%+-]+@', email):
        return False, "Email must contain a username followed by @"
    
    if '@' not in email:
        return False, "Email must contain @ symbol"
    
    if email.count('@') > 1:
        return False, "Email cannot contain multiple @ symbols"
    
    local_part, domain = email.rsplit('@', 1)
    
    if not local_part:
        return False, "Email must have a username before @"
    
    if not domain:
        return False, "Email must have a domain after @"
    
    if '.' not in domain:
        return False, "Domain must contain a dot (e.g., .com, .org)"
    
    if domain.startswith('.') or domain.endswith('.'):
        return False, "Domain cannot start or end with a dot"
    
    if '..' in domain:
        return False, "Domain cannot contain consecutive dots"
    
    tld = domain.split('.')[-1]
    if len(tld) < 2:
        return False, f"Top-level domain '{tld}' is too short"
    
    # Check for common typos
    common_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'protonmail.com']
    if domain in common_domains:
        pass  # Valid common domain
    elif len(domain.split('.')) == 2:
        # Check for typos in common domains
        for common in common_domains:
            if common.startswith(domain.split('.')[0]) and common != domain:
                return False, f"Did you mean @{common}?"
    
    return True, "Valid email format"


# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="User Details Manager",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
def local_css():
    st.markdown("""
    <style>
    /* Main container styling */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Gradient text for title */
    .gradient-text {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .css-1r6slb0 {
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Form container */
    .form-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    }
    
    /* Success message animation */
    @keyframes slideIn {
        0% {
            transform: translateY(-100%);
            opacity: 0;
        }
        100% {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    .success-animation {
        animation: slideIn 0.5s ease-out;
        padding: 15px;
        border-radius: 8px;
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #000;
        margin: 10px 0;
    }
    
    /* Stats card */
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #666;
        margin-top: 10px;
    }
    
    /* Emoji grid */
    .emoji-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
        gap: 10px;
        padding: 10px;
    }
    
    .emoji-item {
        font-size: 2rem;
        text-align: center;
        padding: 10px;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .emoji-item:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        transform: scale(1.1);
    }
    
    .emoji-item.selected {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transform: scale(1.1);
    }
    
    /* Custom button */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border: none;
        padding: 10px 30px;
        border-radius: 50px;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
    }
    
    /* Birthday animation */
    @keyframes confetti {
        0% { transform: translateY(0) rotate(0); }
        100% { transform: translateY(100vh) rotate(720deg); }
    }
    
    .confetti {
        position: fixed;
        width: 10px;
        height: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        animation: confetti 3s ease-out;
        opacity: 0;
    }
    
    /* ===== ADD THESE NEW RULES FOR BLACK INPUT TEXT ===== */
    
    /* Make all text input text black */
    .stTextInput input {
        color: black !important;
        background-color: white !important;
        font-weight: 500 !important;
    }
    
    /* Make date input text black */
    .stDateInput input {
        color: black !important;
        background-color: white !important;
    }
    
    /* Make select box text black */
    .stSelectbox div[data-baseweb="select"] span {
        color: black !important;
    }
    
    /* Ensure text stays black when typing and on focus */
    .stTextInput input:focus,
    .stTextInput input:active,
    .stTextInput input:hover,
    .stDateInput input:focus,
    .stDateInput input:active,
    .stDateInput input:hover {
        color: black !important;
    }
    
    /* Make placeholder text lighter */
    .stTextInput input::placeholder {
        color: #999 !important;
        opacity: 1;
    }
    
    /* For number inputs if you have any */
    .stNumberInput input {
        color: black !important;
    }
    
    /* For text areas if you have any */
    .stTextArea textarea {
        color: black !important;
    }
    
    /* Ensure the text in the input field is black */
    input[type="text"],
    input[type="email"],
    input[type="date"],
    input[type="number"],
    textarea {
        color: black !important;
    }
    
    /* Make sure the text is black when the input is filled */
    input:not(:placeholder-shown) {
        color: black !important;
    }
    
    /* For the email validation indicator to align properly */
    div[data-testid="column"]:nth-of-type(2) {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

def add_dark_bg_with_overlay(image_url, opacity=0.7):
    """
    Add background image with dark overlay for better text readability
    """
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0, 0, 0, {opacity}), rgba(0, 0, 0, {opacity})), url({image_url});
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }}
        
        /* Make text white for better contrast */
        .stMarkdown, .stText, p, li, h1, h2, h3, h4, h5, h6 {{
            color: white !important;
        }}
        
        /* Adjust input fields for dark background */
        .stTextInput > div > div > input,
        .stDateInput > div > div > input,
        .stSelectbox > div > div {{
            background-color: rgba(255, 255, 255, 0.9) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    url = "https://oxsebytemqzoumgsrwgo.supabase.co"
    SYPABASE_KEY = 'sb_publishable_miNkgxkmhh-ptYZ_Sqba8w_PZvQBQGR'
    return create_client(url, SYPABASE_KEY)

# Get database statistics
def get_db_stats(supabase):
    try:
        response = supabase.table("user_entries").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            return {
                'total': len(df),
                'unique_emails': df['email'].nunique(),
                'unique_dates': df['dob_key'].nunique(),
                'recent_date': df['created_at'].max()[:10] if len(df) > 0 else 'N/A',
                'df': df
            }
    except:
        pass
    return {'total': 0, 'unique_emails': 0, 'unique_dates': 0, 'recent_date': 'N/A', 'df': pd.DataFrame()}

# Apply custom CSS
nature_bg = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-1.2.1&auto=format&fit=crop&w=1080&q=80"
local_css()
add_dark_bg_with_overlay(nature_bg, opacity=0.7)

# Initialize Supabase
supabase = init_supabase()
stats = get_db_stats(supabase)

# Sidebar navigation
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: white;'>👤</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Navigation menu
    selected = option_menu(
        menu_title=None,
        options=["Add Entry", "View All", "Analytics", "Search"],
        icons=["person-plus", "table", "graph-up", "search", "gear"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "white", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "5px",
                "--hover-color": "rgba(255,255,255,0.1)",
                "color": "white"
            },
            "nav-link-selected": {"background-color": "rgba(255,255,255,0.2)"},
        }
    )
    
    st.markdown("---")
    
    # Quick stats in sidebar
    st.markdown("### 📊 Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Entries", stats['total'])
    with col2:
        st.metric("Unique Users", stats['unique_emails'])
    
    st.markdown("---")
    st.markdown("### 📅 Today's Date")
    st.markdown(f"**{datetime.now().strftime('%B %d, %Y')}**")

# Main content based on selection
if selected == "Add Entry":
    # Title with gradient
    st.markdown('<h1 class="gradient-text">👤 Your Details</h1>', unsafe_allow_html=True)
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Form container
        with st.container():
            st.markdown("### 📝 Information")
            
            # Name input with icon
            name = st.text_input("👤 Full Name", placeholder="Enter your full name")
            
            # Date of birth with icon
            dob = st.date_input(
                "🎂 Date of Birth",
                min_value=date(1900, 1, 1),
                max_value=date.today(),
                value=date(2000, 1, 1)
            )
            
            # Email with icon and real-time validation
            col11, col12 = st.columns([3, 1])
            with col11:
                email = st.text_input(
                    "📧 Email Address", 
                    placeholder="your@email.com",
                    help="Enter a valid email address (e.g., name@domain.com)"
                )
            
            # Real-time email validation indicator
            if email:
                is_valid, message = validate_email_with_feedback(email)
                with col12:
                    if is_valid:
                        st.markdown("""
                        <div style="background: #00ff0020; border-radius: 5px; padding: 5px; text-align: center; margin-top: 25px;">
                            <span style="color: green; font-size: 20px;">✅</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background: #ff000020; border-radius: 5px; padding: 5px; text-align: center; margin-top: 25px;">
                            <span style="color: red; font-size: 20px;" title="{message}">❌</span>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Show validation message if email is invalid
            if email:
                is_valid, message = validate_email_with_feedback(email)
                if not is_valid:
                    st.warning(f"⚠️ {message}")
            
            # Calculate age
            if dob:
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                st.info(f"📅 Age: {age} years")
    
    with col2:
        st.markdown("### 😊 Choose Your Emoji")
        
        # Emoji selection with grid
        emoji_list = ["😀", "😄", "🥳", "🎉", "🔥", "💡", "🚀", "❤️", "😎", "🌟", "⭐", "✨"]
        
        # Custom emoji selector
        selected_emoji = st.radio(
            "Select emoji",
            emoji_list,
            horizontal=True,
            label_visibility="collapsed"
        )
        
        # Preview section
        st.markdown("### 👀 Preview")
        if name and email:
            preview_container = st.container()
            with preview_container:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); padding: 20px; border-radius: 10px;">
                    <h3 style="text-align: center; margin-bottom: 20px;">Your Entry Preview</h3>
                    <p style="font-size: 2rem; text-align: center;">{selected_emoji}</p>
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Birthday:</strong> {dob.strftime('%B %d, %Y')}</p>
                    <p><strong>Special Key:</strong> {dob.strftime('%d-%m')}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Submit button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 ADD TO DATABASE", use_container_width=True):
            if not name:
                st.warning("⚠️ Please fill in Name")
            elif not email:
                st.warning("⚠️ Please fill in Email")
            elif not is_valid_email(email):
                st.error("❌ Please enter a valid email address")
            else:
                dob_key = dob.strftime("%d-%m")
                dob_iso = dob.isoformat()
                
                db_data = {
                    "name": name,
                    "dob": dob_iso,
                    "dob_key": dob_key,
                    "email": email,
                    "emoji": selected_emoji
                }
                
                try:
                    with st.spinner('Saving to database...'):
                        response = supabase.table("user_entries").insert(db_data).execute()
                    
                    if response.data:
                        st.balloons()
                        st.markdown(f"""
                        <div class="success-animation">
                            <h3>✅ Success!</h3>
                            <p>Your entry has been saved with ID: <strong>{response.data[0]['id']}</strong></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display the saved data
                        display_data = {
                            dob_key: {
                                "name": name,
                                "email": email,
                                "emoji": selected_emoji
                            }
                        }
                        # st.json(display_data)
                        
                except Exception as e:
                    st.error(f"❌ Database error: {str(e)}")

elif selected == "View All":
    st.markdown('<h1 class="gradient-text">📋 All Entries</h1>', unsafe_allow_html=True)
    
    try:
        response = supabase.table("user_entries")\
            .select("*")\
            .order("created_at", desc=True)\
            .execute()
        
        if response.data:
            # Convert to DataFrame for better display
            df = pd.DataFrame(response.data)
            
            # Display as interactive table
            st.dataframe(
                df[['id', 'name', 'email', 'dob', 'emoji', 'created_at']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": "ID",
                    "name": "Name",
                    "email": "Email",
                    "dob": "Date of Birth",
                    "emoji": "Emoji",
                    "created_at": "Created At"
                }
            )
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"user_entries_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("📭 No entries found in database")
            
    except Exception as e:
        st.error(f"Error loading entries: {str(e)}")

elif selected == "Analytics":
    st.markdown('<h1 class="gradient-text">📊 Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    if stats['total'] > 0:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-number">{}</div>
                <div class="stat-label">Total Entries</div>
            </div>
            """.format(stats['total']), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-number">{}</div>
                <div class="stat-label">Unique Users</div>
            </div>
            """.format(stats['unique_emails']), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-number">{}</div>
                <div class="stat-label">Unique Dates</div>
            </div>
            """.format(stats['unique_dates']), unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-number">{}</div>
                <div class="stat-label">Recent Entry</div>
            </div>
            """.format(stats['recent_date']), unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Entries Over Time")
            df = stats['df']
            df['date'] = pd.to_datetime(df['created_at']).dt.date
            daily_counts = df.groupby('date').size().reset_index(name='count')
            fig = px.line(daily_counts, x='date', y='count', title='Daily Entry Count')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎭 Emoji Distribution")
            emoji_counts = df['emoji'].value_counts().reset_index()
            emoji_counts.columns = ['emoji', 'count']
            fig = px.pie(emoji_counts, values='count', names='emoji', title='Emoji Usage')
            st.plotly_chart(fig, use_container_width=True)
        
        # Birthday calendar heatmap
        st.markdown("### 📅 Birthday Calendar")
        month_days = df['dob_key'].value_counts().reset_index()
        month_days.columns = ['date', 'count']
        fig = px.bar(month_days, x='date', y='count', title='Entries by Date (DD-MM)')
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("📊 No data available for analytics")

elif selected == "Search":
    st.markdown('<h1 class="gradient-text">🔍 Search Entries</h1>', unsafe_allow_html=True)
    
    search_type = st.radio(
        "Search by:",
        ["Name", "Email", "Date (DD-MM)", "Emoji"],
        horizontal=True
    )
    
    if search_type == "Name":
        search_term = st.text_input("Enter name to search:")
        if search_term:
            try:
                response = supabase.table("user_entries")\
                    .select("*")\
                    .ilike("name", f"%{search_term}%")\
                    .execute()
                
                if response.data:
                    st.success(f"Found {len(response.data)} results")
                    df = pd.DataFrame(response.data)
                    st.dataframe(df[['name', 'email', 'dob', 'emoji']])
                else:
                    st.info("No results found")
            except Exception as e:
                st.error(f"Search error: {str(e)}")
    
    elif search_type == "Email":
        search_term = st.text_input("Enter email to search:")
        if search_term:
            try:
                response = supabase.table("user_entries")\
                    .select("*")\
                    .ilike("email", f"%{search_term}%")\
                    .execute()
                
                if response.data:
                    st.success(f"Found {len(response.data)} results")
                    df = pd.DataFrame(response.data)
                    st.dataframe(df[['name', 'email', 'dob', 'emoji']])
                else:
                    st.info("No results found")
            except Exception as e:
                st.error(f"Search error: {str(e)}")
    
    elif search_type == "Date (DD-MM)":
        search_date = st.text_input("Enter date (DD-MM format, e.g., 15-02):")
        if search_date:
            try:
                response = supabase.table("user_entries")\
                    .select("*")\
                    .eq("dob_key", search_date)\
                    .execute()
                
                if response.data:
                    st.success(f"Found {len(response.data)} results")
                    df = pd.DataFrame(response.data)
                    st.dataframe(df[['name', 'email', 'dob', 'emoji']])
                else:
                    st.info("No results found for this date")
            except Exception as e:
                st.error(f"Search error: {str(e)}")
    
    elif search_type == "Emoji":
        search_emoji = st.selectbox("Select emoji:", emoji_list)
        if search_emoji:
            try:
                response = supabase.table("user_entries")\
                    .select("*")\
                    .eq("emoji", search_emoji)\
                    .execute()
                
                if response.data:
                    st.success(f"Found {len(response.data)} results")
                    df = pd.DataFrame(response.data)
                    st.dataframe(df[['name', 'email', 'dob', 'emoji']])
                else:
                    st.info("No results found for this emoji")
            except Exception as e:
                st.error(f"Search error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>👤 Arup | Streamlit & Supabase</p>
    <p style="font-size: 0.8rem; opacity: 0.8;">© 2026 All rights reserved</p>
</div>
""", unsafe_allow_html=True)
